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
Each alias is tagged VERIFIED (shown in the Microsoft Learn Graph reference) or
OPEN (a documented metric label, or a v2 field, whose exact export header was
not checked). A caller can override any column with ``column_map``.
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
OPEN = "OPEN"
CONFIGURED = "CONFIGURED"
ABSENT = "ABSENT"

EXCLUSION_REASONS = (
    "missing_user_id",
    "duplicate_user_id",
    "bad_date",
    "malformed_row",
)

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
        ("Last activity date of Teams Copilot (UTC)", OPEN),
    ),
    "word": (
        ("Word Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Word Copilot (UTC)", OPEN),
    ),
    "excel": (
        ("Excel Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Excel Copilot (UTC)", OPEN),
    ),
    "powerpoint": (
        ("PowerPoint Copilot Last Activity Date", VERIFIED),
        ("Last activity date of PowerPoint Copilot (UTC)", OPEN),
    ),
    "outlook": (
        ("Outlook Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Outlook Copilot (UTC)", OPEN),
    ),
    "onenote": (
        ("OneNote Copilot Last Activity Date", VERIFIED),
        ("Last activity date of OneNote Copilot (UTC)", OPEN),
    ),
    "loop": (
        ("Loop Copilot Last Activity Date", VERIFIED),
        ("Last activity date of Loop Copilot (UTC)", OPEN),
    ),
    "copilot_chat": (("Copilot Chat Last Activity Date", VERIFIED),),
    "copilot_chat_work": (
        ("Copilot Chat (work) Last Activity Date", OPEN),
        ("Last activity date of Copilot Chat (work) (UTC)", OPEN),
    ),
    "copilot_chat_web": (
        ("Copilot Chat (web) Last Activity Date", OPEN),
        ("Last activity date of Copilot Chat (web) (UTC)", OPEN),
    ),
    "m365_app": (
        ("Microsoft 365 Copilot Last Activity Date", OPEN),
        ("Last activity date of Microsoft 365 App (UTC)", OPEN),
    ),
    "edge": (
        ("Edge Last Activity Date", OPEN),
        ("Last activity date of Microsoft Edge (UTC)", OPEN),
    ),
    "copilot_agent": (("Copilot Agent Last Activity Date", OPEN),),
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


def _normalize(rows, resolved, salt):
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
        key = user_id.lower()
        if key in seen:
            excluded.append({"row": number, "reason": "duplicate_user_id"})
            continue
        seen.add(key)
        period = None
        raw_period = (_cell(row, resolved, "report_period") or "").strip()
        if raw_period.isdigit():
            period = int(raw_period)
        accepted.append({
            "user_pseudonym": pseudonymize(user_id, salt),
            "report_refresh_date": dates["report_refresh_date"],
            "report_period": period,
            "last_activity": dates["last_activity"],
            "apps": {field: dates[field] for field in APP_FIELDS},
        })
    return accepted, excluded


def _iso(value):
    return value.isoformat() if value else None


def _within(day, as_of, window_days):
    return day is not None and (as_of - day).days < window_days


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
        summary["aggregates"] = _aggregates([], None, None, None)
        return summary

    resolved = resolve_columns(headers, column_map)
    if resolved["user_id"]["header"] is None:
        raise ExportError(
            "no user id column found; set column_map={'user_id': '<header>'}. Headers seen: "
            + ", ".join(headers)
        )
    accepted, excluded = _normalize(rows, resolved, salt)

    as_of_source = "argument"
    if as_of is None:
        refresh = [item["report_refresh_date"] for item in accepted if item["report_refresh_date"]]
        as_of = max(refresh) if refresh else None
        as_of_source = "report_refresh_date" if as_of else None
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
            idle = last is None or (as_of - last).days >= idle_days
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
    summary["aggregates"] = _aggregates(accepted, as_of, window_days, idle_days)
    return summary


def _accounting(total, accepted, excluded):
    by_reason = {reason: 0 for reason in EXCLUSION_REASONS}
    for item in excluded:
        by_reason[item["reason"]] += 1
    return {
        "input_rows": total,
        "accepted": accepted,
        "excluded": len(excluded),
        "excluded_by_reason": by_reason,
        "excluded_rows": excluded,
        "balanced": total == accepted + len(excluded),
    }


def _aggregates(accepted, as_of, window_days, idle_days):
    """Counts to compare with the admin center. No money, no savings."""
    can_window = as_of is not None and window_days is not None
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
        "users_with_activity_date": sum(1 for day in last if day is not None),
        "never_active": sum(1 for day in last if day is None),
        "active_users_in_window": (
            sum(1 for day in last if _within(day, as_of, window_days)) if can_window else None
        ),
        "active_per_app": per_app,
        "idle_days": idle_days,
        "idle_seats": None,
        "idle_policy": "value to be set by the data owner",
        "window_boundary": "OPEN: active when (as_of - last activity) in days is below window_days",
    }
    if idle_days is not None and as_of is not None:
        result["idle_seats"] = sum(
            1 for day in last if day is None or (as_of - day).days >= idle_days
        )
    return result
