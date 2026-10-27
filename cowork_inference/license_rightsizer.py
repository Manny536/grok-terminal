"""License rightsizer: seats, idle seats, and per-app counts.

A seat is one assigned Microsoft 365 Copilot license. An idle seat is a seat
whose holder's last activity is at least ``idle_days`` days before the as-of
date (or who has none). The caller supplies ``idle_days``: no value is
assumed, and without one ``idle_seats`` stays null.

Two paths, one function:

* No usage given: the snapshot fallback. It reports cap use for the one known
  sponsorship seat and leaves reassignment empty. Output is unchanged.
* Usage given (the result of ``copilot_usage.summarize_export``): seat counts
  from a Copilot usage-by-user export, plus per-app counts laid out for
  comparison with the admin center tiles.

Unassigned licenses are not in the export, so they are never inferred from it.
Prompt counts are admin center counts, not tokens, not cost, not savings. The
output holds counts and salted pseudonyms only: no names, no user principal names.
"""

from cowork_inference.copilot_usage import COUNT_LABEL, reconciliation
from cowork_inference.ledger import load_snapshot, teams

IDLE_POLICY = "value to be set by the data owner"
IDLE_BOUNDARY = "OPEN: idle when (as_of - last activity) in days is at least idle_days, or no activity"


def _from_export(usage):
    agg = usage["aggregates"]
    enabled = agg["enabled_users"]
    active = agg["active_users_in_window"]
    accounting = usage["accounting"]
    return {
        "script": "license_rightsizer",
        "status": "PARTIAL",
        "org_optimization": "OPEN",
        "source": "copilot_usage_export",
        "seat_definition": "one assigned Microsoft 365 Copilot license",
        "as_of": usage.get("as_of"),
        "window_days": usage.get("window_days"),
        "seats_in_export": enabled,
        "seats_with_activity_date": agg["users_with_activity_date"],
        "never_active": agg["never_active"],
        "active_seats_in_window": active,
        "seats_not_active_in_window": (
            enabled - active if active is not None else None
        ),
        "idle_days": agg["idle_days"],
        "idle_seats": agg["idle_seats"],
        "idle_seat_pseudonyms": usage.get("idle_seat_pseudonyms"),
        "idle_policy": IDLE_POLICY,
        "idle_boundary": IDLE_BOUNDARY,
        "unassigned_licenses": None,
        "unassigned_licenses_note": "Unassigned licenses are not in the export and are not inferred.",
        "reassignments": [],
        "teams": {name: "UNRESOLVED" for name in teams()},
        "prompt_counts": agg["admin_center_counts"],
        "prompt_counts_label": COUNT_LABEL,
        "per_app_reconciliation": reconciliation(usage),
        "accounting": {
            "input_rows": accounting["input_rows"],
            "accepted": accounting["accepted"],
            "excluded": accounting["excluded"],
            "excluded_by_reason": accounting["excluded_by_reason"],
            "balanced": accounting["balanced"],
        },
        "warnings": list(usage.get("warnings") or []),
        "user_id_stored": usage["user_id_stored"],
        "salt_stored": usage["salt_stored"],
        "reason": (
            "An idle seat is a seat to look at, not a decision to remove a license. "
            "A seat not active in the window is not the same as an idle seat or a never-active seat. "
            "The sponsorship total is not a Copilot seat cost."
        ),
    }


def rightsizer(usage=None):
    if usage is not None:
        return _from_export(usage)
    snap = load_snapshot()
    seat = snap["sponsorship"]
    used = seat["card_used_usd"]
    cap = seat["cap_usd"]
    return {
        "script": "license_rightsizer",
        "status": "NOT_EVALUATED",
        "seat": seat["seat"],
        "cap_usd": cap,
        "used_usd": used,
        "utilization": round(used / cap, 6),
        "reassignments": [],
        "teams": {name: "UNRESOLVED" for name in teams()},
        "reason": (
            "No licence assignment ledger and no per-team Cowork corpus. "
            "Cap use is the sponsorship total, not a Copilot seat list."
        ),
    }


if __name__ == "__main__":
    print(rightsizer())
