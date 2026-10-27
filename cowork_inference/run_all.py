"""Run the six potential scripts and print one receipt.

No argument: the snapshot receipt, unchanged.
``--copilot-export FILE``: also read a Copilot usage-by-user export and feed
its aggregates to ingest_usage and license_rightsizer. The salt comes only from
the COWORK_INFERENCE_SALT environment variable. The receipt holds counts and
salted pseudonyms, never display names or user principal names.
"""

import argparse
import json
import sys

from cowork_inference.copilot_usage import summarize_export
from cowork_inference.ingest_usage import _parse_map, ingest
from cowork_inference.license_rightsizer import rightsizer
from cowork_inference.model_router import router
from cowork_inference.prompt_compressor import compressor
from cowork_inference.response_cache import cache_report
from cowork_inference.savings_report import burn


def receipt(copilot_export=None, as_of=None, window_days=None, idle_days=None,
            column_map=None):
    if copilot_export is None:
        ingested = ingest()
        seats = rightsizer()
    else:
        usage = summarize_export(
            copilot_export, as_of=as_of, window_days=window_days,
            idle_days=idle_days, column_map=column_map,
        )
        seats = rightsizer(usage)
        # Counts only from here on: the per-user list stays out of the receipt.
        ingested = ingest(usage={k: v for k, v in usage.items() if k != "users"})
    sections = [
        ingested,
        seats,
        cache_report(),
        compressor(ingested["missing_inputs"]),
        router(),
        burn(),
    ]
    return {
        "observer": "grok-terminal",
        "not_observer": "grok-bot",
        "org_optimization": "OPEN",
        "sections": sections,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the six scripts and print one receipt. With --copilot-export, "
        "also read a Copilot usage-by-user export. The salt is read from the "
        "COWORK_INFERENCE_SALT environment variable.",
    )
    parser.add_argument("--copilot-export", help="path to the Copilot usage export (CSV or JSON)")
    parser.add_argument("--as-of", help="reference date, YYYY-MM-DD (default: report refresh date)")
    parser.add_argument("--window-days", type=int, help="report window in days (default: Report Period)")
    parser.add_argument("--idle-days", type=int, help="idle threshold in days; set by the data owner")
    parser.add_argument("--map", action="append", metavar="FIELD=HEADER",
                        help="override a column, e.g. user_id=Principal")
    args = parser.parse_args(argv)
    if args.copilot_export is None and (
        args.as_of or args.window_days or args.idle_days or args.map
    ):
        parser.error("--as-of, --window-days, --idle-days and --map need --copilot-export")
    try:
        result = receipt(
            copilot_export=args.copilot_export, as_of=args.as_of,
            window_days=args.window_days, idle_days=args.idle_days,
            column_map=_parse_map(args.map),
        )
    except (ValueError, OSError) as exc:
        print("run_all: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
