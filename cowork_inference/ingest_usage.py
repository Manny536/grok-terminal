"""Stand in for ingest_usage.py.

Planned input was Graph Copilot usage reports, an Analytics CSV, and
Studio/AOAI logs. Those feeds are not on hand. The ingest that can run
today records the sponsorship card, the usage-table total, and the
properties of the one September Cowork task. It does not store prompts
or the skill instructions.
"""

from cowork_inference.ledger import load_snapshot

_TASK_FIELDS = (
    "title",
    "last_activity",
    "usage_export",
    "token_meter",
    "steps_counter",
    "named_steps",
    "plugins",
    "activity_marks_as_displayed",
    "sync_folder",
    "outputs",
    "skill",
)

_SKILL_FIELDS = (
    "name",
    "source_file",
    "category",
    "icon",
    "backbone",
    "cadence",
    "draft_only",
    "sends_or_approves",
    "content_treated_as_data",
    "claim_labels",
    "score",
    "score_max",
    "score_source",
)


def _skill(value):
    """Properties of the produced skill. Instructions and trigger phrases stay out."""
    if not isinstance(value, dict):
        return None
    skill = {key: value[key] for key in _SKILL_FIELDS if key in value}
    skill["prompt_text_stored"] = False
    return skill


def _task(task):
    row = {key: task[key] for key in _TASK_FIELDS if key in task}
    row["prompt_text_stored"] = False
    row["outputs"] = list(row.get("outputs") or [])
    row["output_count"] = len(row["outputs"])
    row["named_steps"] = list(row.get("named_steps") or [])
    row["plugins"] = list(row.get("plugins") or [])
    if "skill" in task:
        row["skill"] = _skill(task.get("skill"))
    return row


def ingest():
    snap = load_snapshot()
    seat = snap["sponsorship"]
    cowork = snap["cowork"]
    tasks = [_task(task) for task in cowork["september_tasks"]]
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
                "inspected_on": cowork.get("inspected_on"),
                "september_task_count": len(tasks),
                "prompt_text_stored": False,
                "usage_export": any(task.get("usage_export") for task in tasks),
                "tasks": tasks,
            },
        ],
    }


if __name__ == "__main__":
    print(ingest())
