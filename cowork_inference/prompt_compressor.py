"""Stand in for prompt_compressor.py.

Planned input was prompts and grounding context. None of that text was
exported. The script refuses a token-savings figure.
"""

from cowork_inference.ledger import load_snapshot


def compressor():
    missing = load_snapshot()["missing_inputs"]
    return {
        "script": "prompt_compressor",
        "status": "NOT_EVALUATED",
        "prompts_on_hand": 0,
        "tokens_before": None,
        "tokens_after": None,
        "reason": "Exact prompts are in the missing-input list: " + ", ".join(missing) + ".",
    }


if __name__ == "__main__":
    print(compressor())
