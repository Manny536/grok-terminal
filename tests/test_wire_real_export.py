"""Tests for wiring a Copilot usage export into license_rightsizer and run_all.

All fixtures are invented. Emails use the reserved example.invalid domain.
"""

import json
from pathlib import Path

import pytest

from cowork_inference import run_all
from cowork_inference.copilot_usage import APP_FIELDS, SALT_ENV, summarize_export
from cowork_inference.ingest_usage import ingest
from cowork_inference.license_rightsizer import rightsizer
from cowork_inference.prompt_compressor import compressor

HERE = Path(__file__).parent / "fixtures"
GOLDEN = HERE / "cowork_inference" / "snapshot_receipt.json"
IDENTITIES = HERE / "cowork_inference" / "synthetic_usage_with_identities.csv"
BY_USER = HERE / "copilot_usage" / "synthetic_admin_center_usage_by_user.csv"
V1 = HERE / "copilot_usage" / "synthetic_graph_v1.csv"
SALT = "test-salt-not-a-secret"


@pytest.fixture(autouse=True)
def _salt(monkeypatch):
    monkeypatch.setenv(SALT_ENV, SALT)


def _seats(path, **kwargs):
    return run_all.receipt(copilot_export=path, **kwargs)["sections"][1]


# --- no argument: snapshot behaviour is unchanged ---------------------------


def test_no_argument_receipt_is_the_snapshot_receipt():
    assert run_all.receipt() == json.loads(GOLDEN.read_text(encoding="utf-8"))


def test_no_argument_cli_prints_the_snapshot_receipt(capsys):
    assert run_all.main([]) == 0
    assert json.loads(capsys.readouterr().out) == json.loads(GOLDEN.read_text(encoding="utf-8"))


def test_rightsizer_without_usage_is_the_snapshot_row():
    row = rightsizer()
    assert row["status"] == "NOT_EVALUATED"
    assert row["utilization"] == 0.2007
    assert row["reassignments"] == []


# --- seats and idle seats from an export -------------------------------------


def test_export_gives_seat_counts_and_partial_status():
    row = _seats(IDENTITIES)
    assert row["status"] == "PARTIAL"
    assert row["org_optimization"] == "OPEN"
    assert row["seat_definition"] == "one assigned Microsoft 365 Copilot license"
    assert (row["seats_in_export"], row["never_active"]) == (4, 1)
    assert (row["active_seats_in_window"], row["seats_not_active_in_window"]) == (2, 2)
    assert row["accounting"]["balanced"] is True
    assert row["reassignments"] == []


def test_idle_seats_stay_null_when_no_threshold_is_given():
    row = _seats(IDENTITIES)
    assert row["idle_days"] is None
    assert row["idle_seats"] is None
    assert row["idle_seat_pseudonyms"] is None
    assert row["idle_policy"] == "value to be set by the data owner"


def test_idle_seats_use_the_caller_supplied_threshold():
    # Bob (49 days) and Carol (never active) are idle at 30 days.
    row = _seats(IDENTITIES, idle_days=30)
    assert (row["idle_days"], row["idle_seats"]) == (30, 2)
    assert len(row["idle_seat_pseudonyms"]) == 2
    # Dave's last activity is exactly 10 days before as-of: idle at 10, not at 11.
    assert _seats(IDENTITIES, idle_days=10)["idle_seats"] == 3
    assert _seats(IDENTITIES, idle_days=11)["idle_seats"] == 2
    assert "OPEN" in row["idle_boundary"]


def test_unassigned_licenses_are_never_inferred():
    row = _seats(IDENTITIES, idle_days=30)
    assert row["unassigned_licenses"] is None
    assert "not inferred" in row["unassigned_licenses_note"]


def test_no_money_savings_or_sponsorship_in_the_export_row():
    row = _seats(BY_USER, idle_days=7)
    dumped = json.dumps(row)
    for key in ("cap_usd", "used_usd", "utilization", "cowork_savings_usd", "savings_usd", "cost_usd"):
        assert key not in row
    assert "sponsorship total is not a Copilot seat cost" in dumped
    assert row["prompt_counts_label"] == "admin center count, not tokens, not cost, not savings"
    for field in row["prompt_counts"].values():
        assert field["label"] == row["prompt_counts_label"]
    receipt = run_all.receipt(copilot_export=BY_USER, idle_days=7)
    assert receipt["org_optimization"] == "OPEN"
    burn = receipt["sections"][5]
    assert burn["cowork_savings_usd"] is None and burn["status"] == "PROPOSED"


def test_prompt_counts_come_from_the_export():
    counts = _seats(BY_USER)["prompt_counts"]
    # Known from the invented file: one prompts_all_apps value is "n/a" and left out.
    assert counts["prompts_all_apps"]["sum"] == 16
    assert counts["prompts_all_apps"]["values_excluded_from_sum"] == 1
    assert counts["prompts_chat_work"]["sum"] == 7


# --- per-app reconciliation ---------------------------------------------------


def test_per_app_reconciliation_lists_every_app_with_counts():
    rec = _seats(BY_USER)["per_app_reconciliation"]
    assert [item["app"] for item in rec["per_app"]] == list(APP_FIELDS)
    by_app = {item["app"]: item for item in rec["per_app"]}
    assert (rec["enabled_users"], rec["active_users"], rec["window_days"]) == (4, 2, 28)
    # Counts known from the invented file (as of 2026-10-26, 28-day window).
    assert by_app["teams"]["active_users"] == 1
    assert by_app["copilot_chat_work"]["active_users"] == 1
    assert by_app["edge"]["active_users"] == 2
    assert by_app["word"]["active_users"] == 0
    assert by_app["word"]["column_status"] == "OBSERVED"
    assert by_app["word"]["label"] == "Word Copilot"
    assert "data owner" in rec["compare_with"]


def test_app_without_a_column_is_unknown_not_zero():
    rec = _seats(V1)["per_app_reconciliation"]
    by_app = {item["app"]: item for item in rec["per_app"]}
    assert by_app["edge"]["column_status"] == "ABSENT"
    assert by_app["edge"]["active_users"] is None
    assert by_app["edge"]["users_with_activity_date"] is None
    assert by_app["teams"]["active_users"] == 2
    agg = summarize_export(V1, salt=SALT)["aggregates"]["active_per_app"]
    assert agg["edge"] == {"with_activity_date": None, "active_in_window": None}


# --- safe by construction -----------------------------------------------------


def test_receipt_holds_no_names_emails_users_list_or_salt():
    receipt = run_all.receipt(copilot_export=IDENTITIES, idle_days=30)
    dumped = json.dumps(receipt)
    for value in ("@example.invalid", "invented@", "Alice", "Bob", "Carol", "Dave", SALT):
        assert value not in dumped
    usage_row = next(r for r in receipt["sections"][0]["rows"] if r["source"] == "copilot_usage_export")
    assert "users" not in usage_row
    assert usage_row["salt_stored"] is False
    assert usage_row["display_name_read"] is False
    assert usage_row["user_id_stored"] == "salted_hmac_sha256_pseudonym"


def test_pseudonyms_are_salted_hmac_values():
    row = _seats(IDENTITIES, idle_days=30)
    assert all(len(p) == 32 and set(p) <= set("0123456789abcdef") for p in row["idle_seat_pseudonyms"])
    other = summarize_export(IDENTITIES, salt="another-salt", idle_days=30)["idle_seat_pseudonyms"]
    assert set(other).isdisjoint(row["idle_seat_pseudonyms"])


def test_salt_comes_only_from_the_environment(monkeypatch, capsys):
    monkeypatch.delenv(SALT_ENV)
    with pytest.raises(ValueError, match=SALT_ENV):
        run_all.receipt(copilot_export=IDENTITIES)
    assert run_all.main(["--copilot-export", str(IDENTITIES)]) == 2
    assert SALT_ENV in capsys.readouterr().err
    with pytest.raises(SystemExit):
        run_all.main(["--copilot-export", str(IDENTITIES), "--salt", "x"])


def test_include_users_false_drops_only_the_per_user_list():
    full = summarize_export(IDENTITIES, salt=SALT, idle_days=30)
    slim = summarize_export(IDENTITIES, salt=SALT, idle_days=30, include_users=False)
    assert "users" in full and "users" not in slim
    assert {k: v for k, v in full.items() if k != "users"} == slim
    empty = summarize_export(b"", salt=SALT, include_users=False)
    assert "users" not in empty


# --- run_all and ingest wiring ------------------------------------------------


def test_cli_with_export_prints_one_receipt(capsys):
    code = run_all.main([
        "--copilot-export", str(IDENTITIES), "--idle-days", "30", "--map", "word=Word Copilot Last Activity Date",
    ])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert [s["script"] for s in out["sections"]] == [
        "ingest_usage", "license_rightsizer", "response_cache", "prompt_compressor", "model_router", "savings_report",
    ]
    assert out["sections"][1]["idle_seats"] == 2


def test_cli_options_need_an_export():
    with pytest.raises(SystemExit):
        run_all.main(["--idle-days", "30"])


def test_missing_inputs_drop_the_report_once_an_export_is_given():
    plain = run_all.receipt()["sections"]
    wired = run_all.receipt(copilot_export=IDENTITIES)["sections"]
    assert "Graph Copilot usage reports" in plain[0]["missing_inputs"]
    assert "Graph Copilot usage reports" not in wired[0]["missing_inputs"]
    assert "Graph Copilot usage reports" in plain[3]["reason"]
    assert "Graph Copilot usage reports" not in wired[3]["reason"]
    assert "exact user prompts" in wired[3]["reason"]
    assert wired[3]["prompts_on_hand"] == 0


def test_compressor_default_is_unchanged():
    assert "Graph Copilot usage reports" in compressor()["reason"]


def test_ingest_accepts_a_summary_it_did_not_read_itself():
    usage = summarize_export(IDENTITIES, salt=SALT, include_users=False)
    result = ingest(usage=usage)
    assert result["rows"][-1] is usage
    assert "Graph Copilot usage reports" not in result["missing_inputs"]
    assert result["status"] == "PARTIAL"
