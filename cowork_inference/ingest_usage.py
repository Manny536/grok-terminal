"""Stand in for ingest_usage.py.

Planned input was Graph Copilot usage reports, an Analytics CSV, and
Studio/AOAI logs. Those feeds are not on hand. The ingest that can run
today records the sponsorship card, the usage-table total, and the
Cowork task census. It does not store prompts.
"""

from cowork_inference.ledger import load_snapshot


def ingest():
    snap = load_snapshot()
    seat = snap["sponsorship"]
    return {
        "script": "ingest_usage",
        "status": "PARTIAL",
        "missing_inputs": list(snap["missing_inputs"]),
        "rows": [
            {
                "source": "azure_sponsorship_balance_card",
                "meter": seat["meter"],
                "used_usd": seat["card_used_usd"],
                "remaining_usd": seat["card_remaining_usd"],
                "cap_usd": seat["cap_usd"],
                "as_of": snap["observed_on"],
            },
            {
                "source": "azure_sponsorship_usage_table",
                "meter": seat["meter"],
                "spend_usd": seat["usage_table_spend_usd"],
                "window_start": seat["usage_window_start"],
                "window_end": seat["usage_window_end"],
            },
            {
                "source": "cowork_my_tasks",
                "september_task_count": len(snap["cowork"]["september_tasks"]),
                "prompt_text_stored": False,
            },
        ],
    }


if __name__ == "__main__":
    print(ingest())
