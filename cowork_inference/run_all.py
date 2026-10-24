"""Run the six potential scripts and print one receipt."""

import json

from cowork_inference.ingest_usage import ingest
from cowork_inference.license_rightsizer import rightsizer
from cowork_inference.model_router import router
from cowork_inference.prompt_compressor import compressor
from cowork_inference.response_cache import cache_report
from cowork_inference.savings_report import burn


def receipt():
    sections = [
        ingest(),
        rightsizer(),
        cache_report(),
        compressor(),
        router(),
        burn(),
    ]
    return {
        "observer": "grok-terminal",
        "not_observer": "grok-bot",
        "org_optimization": "OPEN",
        "sections": sections,
    }


def main():
    print(json.dumps(receipt(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
