"""Stand in for model_router.py.

Planned input was per-request features. The live Azure page shows one
sponsorship subscription and no model mix. Routing stays unresolved.
"""

from cowork_inference.ledger import load_snapshot


def router():
    seat = load_snapshot()["sponsorship"]
    return {
        "script": "model_router",
        "status": "NOT_EVALUATED",
        "subscriptions_observed": seat["subscriptions"],
        "model_mix": [],
        "routes": [],
        "reason": (
            "One sponsorship line is not a request log. "
            "No model prices or request features were visible."
        ),
    }


if __name__ == "__main__":
    print(router())
