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


def test_missing_prompt_ledger_blocks_the_other_scripts():
    assert ingest()["status"] == "PARTIAL"
    assert "exact user prompts" in ingest()["missing_inputs"]
    assert rightsizer()["reassignments"] == []
    assert rightsizer()["teams"]["Delivery"] == "UNRESOLVED"
    assert cache_report()["september_task_count"] == 1
    assert cache_report()["repeat_rate"] is None
    assert compressor()["prompts_on_hand"] == 0
    assert router()["routes"] == []
