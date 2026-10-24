"""Savings report from the two figures that were actually visible.

Live sponsorship spend versus the last posted monthly figure for the
same seat. The result is a burn delta, not a Cowork savings claim.
"""

from datetime import date

from cowork_inference.ledger import load_snapshot, teams


def _days(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def burn():
    snap = load_snapshot()
    seat = snap["sponsorship"]
    live = seat["usage_table_spend_usd"]
    posted = seat["monthly_sheet_posted_usd"]
    delta = round(live - posted, 2)
    elapsed = _days(seat["monthly_sheet_posted_on"], snap["observed_on"])
    daily = round(delta / elapsed, 2) if elapsed else None
    remaining = seat["card_remaining_usd"]
    runway = round(remaining / daily, 1) if daily else None
    return {
        "script": "savings_report",
        "status": "PROPOSED",
        "org_optimization": "OPEN",
        "meter": seat["meter"],
        "live_spend_usd": live,
        "card_used_usd": seat["card_used_usd"],
        "monthly_posted_usd": posted,
        "monthly_posted_on": seat["monthly_sheet_posted_on"],
        "unposted_delta_usd": delta,
        "elapsed_days": elapsed,
        "implied_daily_usd": daily,
        "card_remaining_usd": remaining,
        "implied_runway_days": runway,
        "offer_days_remaining_observed": seat["days_until_offer_end_observed"],
        "teams": {name: "UNRESOLVED" for name in teams()},
        "cowork_savings_usd": None,
        "reason": (
            "The delta is sponsorship burn since the monthly sheet, "
            "not measured Cowork token savings. A linear daily rate is an assumption."
        ),
    }


if __name__ == "__main__":
    print(burn())
