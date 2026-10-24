"""Stand in for license_rightsizer.py.

Planned input was usage plus licence assignments. Neither a per-seat
assignment list nor a team split is available. The script reports cap
use for the one known sponsorship seat and leaves reassignment empty.
"""

from cowork_inference.ledger import load_snapshot, teams


def rightsizer():
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
