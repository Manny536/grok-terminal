"""Read a Microsoft 365 Copilot usage-by-user export. Stdlib only. No network.

Accepted inputs:
  * the CSV from the Microsoft Graph report
    getMicrosoft365CopilotUsageUserDetail (headers such as "User Principal Name"),
  * the JSON from the Graph beta endpoint (camelCase properties such as
    "userPrincipalName"),
  * the CSV exported from the Microsoft 365 admin center Copilot usage report.

Privacy rules this module keeps:
  * the user principal name is replaced by a salted HMAC-SHA256 pseudonym,
  * the salt comes from an argument or the environment and is never stored,
  * the display name column is never read,
  * prompts are not part of this report and are never read or stored.

Column names are matched by a normalised key (lower case, letters and digits
only), so "Last Activity Date" and "lastActivityDate" are the same column.
Each alias is tagged VERIFIED (shown in the Microsoft Learn Graph reference),
OBSERVED (seen in the header row of a real admin center export taken on
2026-10-26, from one tenant) or OPEN (a documented metric label, or a v2 field,
whose exact export header was not checked). A caller can override any column
with ``column_map``.
Source URLs are listed in cowork_inference/COPILOT_USAGE_INGEST.md.
"""

import codecs
import csv
import hashlib
import hmac
import io
import json
import os
import re
from datetime import date
from pathlib import Path

SALT_ENV = "COWORK_INFERENCE_SALT"

VERIFIED = "VERIFIED"
OBSERVED = "OBSERVED"
OPEN = "OPEN"
CONFIGURED = "CONFIGURED"
ABSENT = "ABSENT"

EXCLUSION_REASONS = (
    "missing_user_id",
    "duplicate_user_id",
    "bad_date",
    "malformed_row",
)
# Reported in excluded_by_reason only when a row was excluded for it.
FUTURE_DATE = "future_date"

COUNT_LABEL = "admin center count, not tokens, not cost, not savings"

# canonical field -> ordered (header text, status) aliases.
COLUMN_ALIASES = {
    "user_id": (
        ("User Principal Name", VERIFIED),
        ("User name", OPEN),
    ),
    "report_refresh_date": (("Report Refresh Date", VERIFIED),),
    "report_period": (("Report Period", VERIFIED),),
    "last_activity": (
        ("Last Activity Date", VERIFIED),
        ("Last activity date (UTC)", OPEN),
    ),
    "teams": (
        ("Microsoft Teams Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Teams Copilot (UTC)", OBSERVED),
    ),
    "word": (
        ("Word Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Word Copilot (UTC)", OBSERVED),
    ),
    "excel": (
        ("Excel Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Excel Copilot (UTC)", OBSERVED),
    ),
    "powerpoint": (
        ("PowerPoint Copilot Last Activity Date", VERIFIED),
        ("Last activity date of PowerPoint Copilot (UTC)", OBSERVED),
    ),
    "outlook": (
        ("Outlook Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Outlook Copilot (UTC)", OBSERVED),
    ),
    "onenote": (
        ("OneNote Copilot Last Activity Date", VERIFIED),
        ("Last activity date of OneNote Copilot (UTC)", OBSERVED),
    ),
    "loop": (
        ("Loop Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Loop Copilot (UTC)", OBSERVED),
    ),
    "copilot_chat": (("Copilot Chat Last Activity Date", VERIFIED),),
    "copilot_chat_work": (
        ("Copilot Chat (work) Last Activity Date", OPEN),
        ("Last activity date of Copilot Chat (work) (UTC)", OBSERVED),
    ),
    "copilot_chat_web": (
        ("Copilot Chat (web) Last Activity Date", OPEN),
        ("Last activity date of Copilot Chat (web) (UTC)", OBSERVED),
    ),
    "m365_app": (
        ("Microsoft 365 Copilot Last Activity Date", OPEN),
        ("Last activity date of Microsoft 365 Copilot (app) (UTC)", OBSERVED),
        ("Last activity date of Microsoft 365 App (UTC)", OPEN),
    ),
    "edge": (
        ("Edge Last Activity Date", OPEN),
        ("Last activity date of Edge (UTC)", OBSERVED),
        ("Last activity date of Microsoft Edge (UTC)", OPEN),
    ),
    "copilot_agent": (("Copilot Agent Last Activity Date", OPEN),),
    "prompts_all_apps": (("Prompts submitted for All Apps", OBSERVED),),
    "prompts_chat_work": (("Prompts submitted for Copilot Chat (work)", OBSERVED),),
    "prompts_chat_web": (("Prompts submitted for Copilot Chat (web)", OBSERVED),),
    "active_usage_days_all_apps": (("Active Usage Days for All Apps", OBSERVED),),
}

# Numeric columns of the admin center export. Used as counts only, never per user.
# field -> unit
COUNT_FIELDS = {
    "prompts_all_apps": "prompts",
    "prompts_chat_work": "prompts",
    "prompts_chat_web": "prompts",
    "active_usage_days_all_apps": "days",
}

APP_FIELDS = (
    "teams", "word", "excel", "powerpoint", "outlook", "onenote", "loop",
    "copilot_chat", "copilot_chat_work", "copilot_chat_web",
    "m365_app", "edge", "copilot_agent",
)

_NESTED_PERIOD_KEY = "copilotActivityUserDetailsByPeriod"


class ExportError(ValueError):
    """The export cannot be read as a Copilot usage-by-user report."""


def column_key(name):
    """Normalise a header or property name for matching."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


# --- reading ---------------------------------------------------------------


def _decode(raw):
    if raw.startswith(codecs.BOM_UTF8):
        return raw.decode("utf-8-sig")
    if raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExportError("export is not UTF-8 or UTF-16 text") from exc


def _json_rows(text):
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ExportError("export looks like JSON but does not parse") from exc
    if isinstance(data, dict):
        data = data.get("value")
    if not isinstance(data, list):
        raise ExportError('JSON export has no "value" list of rows')
    rows = []
    for item in data:
        if not isinstance(item, dict):
            rows.append(None)
            continue
        flat = {key: value for key, value in item.items() if key != _NESTED_PERIOD_KEY}
        nested = item.get(_NESTED_PERIOD_KEY)
        if isinstance(nested, list) and nested and isinstance(nested[0], dict):
            if "reportPeriod" in nested[0]:
                flat["reportPeriod"] = nested[0]["reportPeriod"]
        rows.append(flat)
    headers = []
    for row in rows:
        headers.extend(key for key in (row or ()) if key not in headers)
    return headers, rows


def _csv_rows(text):
    reader = csv.DictReader(io.StringIO(text))
    headers = [name for name in (reader.fieldnames or []) if name is not None]
    rows = []
    for item in reader:
        rows.append({key: value for key, value in item.items() if key is not None})
    return headers, rows


def read_export(source):
    """Return (headers, rows) from a path (str or Path) or raw bytes.

    A row is a dict, or None when a JSON item is not an object.
    An empty file returns ([], []).
    """
    if isinstance(source, (bytes, bytearray)):
        raw = bytes(source)
    else:
        raw = Path(source).read_bytes()
    text = _decode(raw)
    stripped = text.lstrip("\ufeff \t\r\n")
    if not stripped:
        return [], []
    if stripped[0] in "{[":
        return _json_rows(stripped)
    return _csv_rows(text.lstrip("\ufeff"))


# --- column resolution -----------------------------------------------------


def resolve_columns(headers, column_map=None):
    """Map canonical fields to the headers present. Returns {field: {header, status}}.

    ``column_map`` is {canonical field: header text} and wins over the aliases.
    A configured header that is not in the export raises ExportError.
    """
    column_map = dict(column_map or {})
    unknown = sorted(set(column_map) - set(COLUMN_ALIASES))
    if unknown:
        raise ExportError("unknown column_map field(s): " + ", ".join(unknown))
    by_key = {}
    for header in headers:
        by_key.setdefault(column_key(header), header)
    resolved = {}
    for field, aliases in COLUMN_ALIASES.items():
        if field in column_map:
            header = by_key.get(column_key(column_map[field]))
            if header is None:
                raise ExportError(
                    "configured column for %s is not in the export: %s" % (field, column_map[field])
                )
            resolved[field] = {"header": header, "status": CONFIGURED}
            continue
        resolved[field] = {"header": None, "status": ABSENT}
        for alias, status in aliases:
            header = by_key.get(column_key(alias))
            if header is not None:
                resolved[field] = {"header": header, "status": status}
                break
    return resolved


# --- values ----------------------------------------------------------------


def pseudonymize(user_id, salt):
    """Salted HMAC-SHA256 of the lower-cased id. The salt is not kept."""
    return hmac.new(
        salt.encode("utf-8"), user_id.strip().lower().encode("utf-8"), hashlib.sha256
    ).hexdigest()[:32]


def _salt(salt):
    value = salt if salt is not None else os.environ.get(SALT_ENV)
    if not value:
        raise ValueError(
            "a salt is required: pass salt=... or set " + SALT_ENV + ". It is never stored."
        )
    return value


def parse_date(value):
    """Return (date or None, ok). Empty means no activity, which is valid."""
    if value is None:
        return None, True
    text = str(value).strip()
    if not text:
        return None, True
    if len(text) > 10 and text[10] in "T ":
        text = text[:10]
    if len(text) != 10:
        return None, False
    try:
        return date.fromisoformat(text), True
    except ValueError:
        return None, False


def _as_date(value, name):
    if value is None or isinstance(value, date):
        return value
    parsed, ok = parse_date(value)
    if not ok or parsed is None:
        raise ValueError(name + " must be a YYYY-MM-DD date")
    return parsed


def _positive(value, name):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive integer")
    return value


def _cell(row, resolved, field):
    header = resolved[field]["header"]
    if header is None:
        return None
    value = row.get(header)
    return value if value is None or isinstance(value, str) else str(value)


# --- accounting and aggregates ---------------------------------------------


_INT = re.compile(r"[0-9]+")


def _count(value):
    """Return an int for a plain non-negative integer text, else None (never guessed)."""
    text = (value or "").strip()
    return int(text) if _INT.fullmatch(text) else None


def _normalize(rows, resolved, salt, as_of=None):
    accepted, excluded, seen = [], [], set()
    date_fields = ("report_refresh_date", "last_activity") + APP_FIELDS
    for number, row in enumerate(rows, start=1):
        if row is None:
            excluded.append({"row": number, "reason": "malformed_row"})
            continue
        user_id = (_cell(row, resolved, "user_id") or "").strip()
        if not user_id:
            excluded.append({"row": number, "reason": "missing_user_id"})
            continue
        dates, bad = {}, False
        for field in date_fields:
            parsed, ok = parse_date(_cell(row, resolved, field))
            if not ok:
                bad = True
                break
            dates[field] = parsed
        if bad:
            excluded.append({"row": number, "reason": "bad_date"})
            continue
        if as_of is not None and any(
            dates[field] is not None and dates[field] > as_of
            for field in ("last_activity",) + APP_FIELDS
        ):
            excluded.append({"row": number, "reason": FUTURE_DATE})
            continue
        key = user_id.lower()
        if key in seen:
            excluded.append({"row": number, "reason": "duplicate_user_id"})
            continue
        seen.add(key)
        period = None
        raw_period = (_cell(row, resolved, "report_period") or "").strip()
        if raw_period.isdigit():
            period = int(raw_period)
        # A blank overall date falls back to the latest per-app date, so a user
        # with recent app activity is not counted as never active.
        last, derived = dates["last_activity"], False
        if last is None:
            app_days = [dates[field] for field in APP_FIELDS if dates[field] is not None]
            if app_days:
                last, derived = max(app_days), True
        counts = {}
        for field in COUNT_FIELDS:
            if resolved[field]["header"] is not None:
                counts[field] = _count(_cell(row, resolved, field))
        accepted.append({
            "user_pseudonym": pseudonymize(user_id, salt),
            "report_refresh_date": dates["report_refresh_date"],
            "report_period": period,
            "last_activity": last,
            "last_activity_derived": derived,
            "apps": {field: dates[field] for field in APP_FIELDS},
            "counts": counts,
        })
    return accepted, excluded


def _iso(value):
    return value.isoformat() if value else None


def _within(day, as_of, window_days):
    """Active in the window: not after as_of, and fewer than window_days before it."""
    return day is not None and 0 <= (as_of - day).days < window_days


def summarize_export(source, salt=None, as_of=None, window_days=None,
                     idle_days=None, column_map=None):
    """Normalise one export and return rows, accounting and aggregates.

    as_of        reference date. Default: latest Report Refresh Date in the accepted rows.
    window_days  report window. Default: the single Report Period value, if there is one.
    idle_days    a seat is idle with no activity in this many days. No default: the value
                 is to be set by the data owner. Without it, idle seats are not computed.
    """
    salt = _salt(salt)
    as_of = _as_date(as_of, "as_of")
    window_days = _positive(window_days, "window_days")
    idle_days = _positive(idle_days, "idle_days")

    headers, rows = read_export(source)
    summary = {
        "source": "copilot_usage_export",
        "status": "PARTIAL",
        "org_optimization": "OPEN",
        "user_id_stored": "salted_hmac_sha256_pseudonym",
        "salt_stored": False,
        "prompt_text_stored": False,
        "display_name_read": False,
        "warnings": [],
    }
    if not rows:
        summary["warnings"].append("empty_export")
        resolved = resolve_columns(headers, column_map) if headers else {}
        summary["column_resolution"] = resolved
        summary["accounting"] = _accounting(0, 0, [])
        summary["users"] = []
        summary["aggregates"] = _aggregates([], None, None, None, True, {})
        return summary

    resolved = resolve_columns(headers, column_map)
    if resolved["user_id"]["header"] is None:
        raise ExportError(
            "no user id column found; set column_map={'user_id': '<header>'}. Headers seen: "
            + ", ".join(headers)
        )
    accepted, excluded = _normalize(rows, resolved, salt, as_of)

    as_of_source = "argument"
    if as_of is None:
        refresh = [item["report_refresh_date"] for item in accepted if item["report_refresh_date"]]
        as_of = max(refresh) if refresh else None
        as_of_source = "report_refresh_date" if as_of else None
        if as_of is not None:
            # Run again with the reference date so a date after it is excluded.
            accepted, excluded = _normalize(rows, resolved, salt, as_of)
    future = sum(1 for item in excluded if item["reason"] == FUTURE_DATE)
    if future:
        summary["warnings"].append("future_date_rows_excluded:%d" % future)
    elif as_of is None:
        summary["warnings"].append("future_dates_not_checked:no_reference_date")
    activity_known = any(
        resolved[field]["header"] is not None for field in ("last_activity",) + APP_FIELDS
    )
    if not activity_known:
        summary["warnings"].append("no_activity_columns:map_last_activity_or_app_columns")
        for item in accepted:
            item["last_activity"] = None
    derived = sum(1 for item in accepted if item["last_activity_derived"])
    if derived:
        summary["warnings"].append("last_activity_derived_from_app_dates:%d" % derived)
    window_source = "argument"
    if window_days is None:
        periods = {item["report_period"] for item in accepted}
        periods.discard(None)
        window_days = periods.pop() if len(periods) == 1 else None
        window_source = "report_period" if window_days else None

    users = []
    for item in accepted:
        idle = None
        if idle_days is not None and as_of is not None:
            last = item["last_activity"]
            idle = (last is None or (as_of - last).days >= idle_days) if activity_known else None
        users.append({
            "user_pseudonym": item["user_pseudonym"],
            "last_activity_date": _iso(item["last_activity"]),
            "app_last_activity": {k: _iso(v) for k, v in item["apps"].items()},
            "idle": idle,
        })

    summary["column_resolution"] = resolved
    matched = {info["header"] for info in resolved.values()}
    summary["columns_unrecognised"] = sorted(
        header for header in headers
        if header not in matched and column_key(header) != "displayname"
    )
    summary["accounting"] = _accounting(len(rows), len(accepted), excluded)
    summary["users"] = users
    summary["as_of"] = _iso(as_of)
    summary["as_of_source"] = as_of_source
    summary["window_days"] = window_days
    summary["window_days_source"] = window_source
    summary["aggregates"] = _aggregates(
        accepted, as_of, window_days, idle_days, activity_known, summary["warnings"]
    )
    return summary


def _accounting(total, accepted, excluded):
    by_reason = {reason: 0 for reason in EXCLUSION_REASONS}
    for item in excluded:
        by_reason[item["reason"]] = by_reason.get(item["reason"], 0) + 1
    return {
        "input_rows": total,
        "accepted": accepted,
        "excluded": len(excluded),
        "excluded_by_reason": by_reason,
        "excluded_rows": excluded,
        "balanced": total == accepted + len(excluded),
    }


def _count_aggregates(accepted, warnings):
    """Sums and non-zero user counts for the numeric admin center columns. Counts only."""
    result = {}
    for field, unit in COUNT_FIELDS.items():
        if not any(field in item["counts"] for item in accepted):
            continue
        values = [item["counts"][field] for item in accepted if field in item["counts"]]
        good = [value for value in values if value is not None]
        skipped = len(values) - len(good)
        if skipped:
            warnings.append("non_integer_or_blank_values_excluded_from_sum:%s=%d" % (field, skipped))
        result[field] = {
            "unit": unit,
            "sum": sum(good),
            "users_with_nonzero": sum(1 for value in good if value > 0),
            "values_excluded_from_sum": skipped,
            "label": COUNT_LABEL,
        }
    return result


def _aggregates(accepted, as_of, window_days, idle_days, activity_known=True, warnings=None):
    """Counts to compare with the admin center. No money, no savings.

    When no activity column is mapped (activity_known is False) the activity
    counts are None (unknown), not zero and not idle.
    """
    can_window = activity_known and as_of is not None and window_days is not None
    per_app = {}
    for field in APP_FIELDS:
        dates = [item["apps"][field] for item in accepted]
        per_app[field] = {
            "with_activity_date": sum(1 for day in dates if day is not None),
            "active_in_window": (
                sum(1 for day in dates if _within(day, as_of, window_days)) if can_window else None
            ),
        }
    last = [item["last_activity"] for item in accepted]
    result = {
        "enabled_users": len(accepted),
        "users_with_activity_date": (
            sum(1 for day in last if day is not None) if activity_known else None
        ),
        "never_active": sum(1 for day in last if day is None) if activity_known else None,
        "last_activity_derived_from_apps": sum(1 for item in accepted if item["last_activity_derived"]),
        "active_users_in_window": (
            sum(1 for day in last if _within(day, as_of, window_days)) if can_window else None
        ),
        "active_per_app": per_app,
        "admin_center_counts": _count_aggregates(accepted, [] if warnings is None else warnings),
        "idle_days": idle_days,
        "idle_seats": None,
        "idle_policy": "value to be set by the data owner",
        "window_boundary": "OPEN: active when (as_of - last activity) in days is below window_days",
    }
    if activity_known and idle_days is not None and as_of is not None:
        result["idle_seats"] = sum(
            1 for day in last if day is None or (as_of - day).days >= idle_days
        )
    return result
