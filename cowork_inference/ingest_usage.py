"""ingest_usage.py

Two paths, one function:

* No export given: the snapshot fallback. It records the sponsorship card,
  the usage-table total, and the properties of the one September Cowork
  task. It does not store prompts or the skill instructions.
* Export given: the same snapshot rows, plus one row built from a Microsoft
  365 Copilot usage-by-user export (admin center CSV, Graph CSV, or Graph
  beta JSON). See cowork_inference/copilot_usage.py and
  cowork_inference/COPILOT_USAGE_INGEST.md.

Status stays PARTIAL either way. Org optimization stays OPEN.
"""

import argparse
import json
import sys

from cowork_inference.copilot_usage import summarize_export
from cowork_inference.ledger import load_snapshot

_EXPORT_SATISFIES = "Graph Copilot usage reports"

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


def ingest(export_path=None, salt=None, as_of=None, window_days=None,
           idle_days=None, column_map=None):
    """Snapshot fallback; with ``export_path`` also ingest a Copilot usage export."""
    snap = load_snapshot()
    seat = snap["sponsorship"]
    cowork = snap["cowork"]
    tasks = [_task(task) for task in cowork["september_tasks"]]
    rows = [
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
    ]
    missing = list(snap["missing_inputs"])
    if export_path is not None:
        rows.append(summarize_export(
            export_path, salt=salt, as_of=as_of, window_days=window_days,
            idle_days=idle_days, column_map=column_map,
        ))
        missing = [item for item in missing if item != _EXPORT_SATISFIES]
    return {
        "script": "ingest_usage",
        "status": "PARTIAL",
        "missing_inputs": missing,
        "rows": rows,
    }


def _parse_map(pairs):
    mapping = {}
    for pair in pairs or []:
        field, sep, header = pair.partition("=")
        if not sep or not field or not header:
            raise SystemExit("--map expects field=Header, got: " + pair)
        mapping[field] = header
    return mapping


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ingest the snapshot, and optionally a Copilot usage-by-user export. "
        "The salt is read from the COWORK_INFERENCE_SALT environment variable.",
    )
    parser.add_argument("--export", help="path to the Copilot usage export (CSV or JSON)")
    parser.add_argument("--as-of", help="reference date, YYYY-MM-DD (default: report refresh date)")
    parser.add_argument("--window-days", type=int, help="report window in days (default: Report Period)")
    parser.add_argument("--idle-days", type=int, help="idle threshold in days; set by the data owner")
    parser.add_argument("--map", action="append", metavar="FIELD=HEADER",
                        help="override a column, e.g. user_id=Principal")
    args = parser.parse_args(argv)
    try:
        result = ingest(
            export_path=args.export, as_of=args.as_of, window_days=args.window_days,
            idle_days=args.idle_days, column_map=_parse_map(args.map),
        )
    except (ValueError, OSError) as exc:
        print("ingest_usage: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
