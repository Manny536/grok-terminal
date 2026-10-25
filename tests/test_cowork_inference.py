import json

from cowork_inference.ingest_usage import ingest
from cowork_inference.license_rightsizer import rightsizer
from cowork_inference.model_router import router
from cowork_inference.prompt_compressor import compressor
from cowork_inference.response_cache import cache_report
from cowork_inference.savings_report import burn


def test_unposted_sponsorship_delta():
    row = burn()
    assert row["unposted_delta_usd"] == 486.78
    assert row["elapsed_days"] == 17
    assert row["org_optimization"] == "OPEN"
    assert row["cowork_savings_usd"] is None


def test_ingest_records_the_produced_skill_without_its_text():
    row = next(item for item in ingest()["rows"] if item["source"] == "cowork_my_tasks")
    task = row["tasks"][0]
    skill = task["skill"]
    dumped = json.dumps(ingest())
    assert row["september_task_count"] == 1
    assert row["prompt_text_stored"] is False
    assert row["usage_export"] is False
    assert task["steps_counter"] == "11/11"
    assert task["output_count"] == 7
    assert task["token_meter"] is None
    assert skill["name"] == "kakeya-synthesis"
    assert skill["category"] == "analysis"
    assert skill["cadence"] == [
        "Type", "Ground", "Authorize", "Weigh", "Continue", "Receipt",
    ]
    assert skill["draft_only"] is True
    assert skill["sends_or_approves"] is False
    assert skill["prompt_text_stored"] is False
    assert "CreateReplyDraft" not in dumped
    assert "synthesize this request" not in dumped


def test_missing_prompt_ledger_blocks_the_other_scripts():
    assert ingest()["status"] == "PARTIAL"
    assert "exact user prompts" in ingest()["missing_inputs"]
    assert rightsizer()["reassignments"] == []
    assert rightsizer()["teams"]["Delivery"] == "UNRESOLVED"
    assert cache_report()["september_task_count"] == 1
    assert cache_report()["repeat_rate"] is None
    assert compressor()["prompts_on_hand"] == 0
    assert router()["routes"] == []
