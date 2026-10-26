"""Tests for the Copilot usage-export reader. All fixtures are synthetic."""

import codecs
import json
from pathlib import Path

import pytest

from cowork_inference.copilot_usage import (
    ExportError,
    SALT_ENV,
    pseudonymize,
    summarize_export,
)
from cowork_inference.ingest_usage import ingest, main

FIXTURES = Path(__file__).parent / "fixtures" / "copilot_usage"
V1 = FIXTURES / "synthetic_graph_v1.csv"
MESSY = FIXTURES / "synthetic_messy.csv"
BETA = FIXTURES / "synthetic_graph_beta.json"
ADMIN = FIXTURES / "synthetic_admin_center_labels.csv"
HEADER_ONLY = FIXTURES / "synthetic_header_only.csv"
SALT = "test-salt-not-a-secret"


@pytest.fixture(autouse=True)
def _no_ambient_salt(monkeypatch):
    monkeypatch.delenv(SALT_ENV, raising=False)


def test_happy_path_accounting_and_known_counts():
    out = summarize_export(V1, salt=SALT)
    acc = out["accounting"]
    assert (acc["input_rows"], acc["accepted"], acc["excluded"]) == (10, 10, 0)
    assert acc["balanced"] is True
    assert out["as_of"] == "2026-10-20" and out["as_of_source"] == "report_refresh_date"
    assert out["window_days"] == 28 and out["window_days_source"] == "report_period"
    assert out["status"] == "PARTIAL" and out["org_optimization"] == "OPEN"
    # Counts below are known from the fixture file, the way an admin center total would be.
    agg = out["aggregates"]
    assert agg["enabled_users"] == 10
    assert agg["users_with_activity_date"] == 8
    assert agg["never_active"] == 2
    assert agg["active_users_in_window"] == 6
    per_app = agg["active_per_app"]
    assert {k: v["with_activity_date"] for k, v in per_app.items() if k in (
        "teams", "word", "excel", "powerpoint", "outlook", "onenote", "loop", "copilot_chat",
    )} == {
        "teams": 2, "word": 3, "excel": 1, "powerpoint": 1,
        "outlook": 2, "onenote": 1, "loop": 1, "copilot_chat": 3,
    }
    assert {k: per_app[k]["active_in_window"] for k in (
        "teams", "word", "excel", "powerpoint", "outlook", "onenote", "loop", "copilot_chat",
    )} == {
        "teams": 2, "word": 3, "excel": 0, "powerpoint": 1,
        "outlook": 2, "onenote": 1, "loop": 0, "copilot_chat": 3,
    }
    # Graph-documented headers resolve as VERIFIED, v2-only fields are absent here.
    cols = out["column_resolution"]
    assert cols["user_id"]["status"] == "VERIFIED"
    assert cols["teams"]["header"] == "Microsoft Teams Copilot Last Activity Date"
    assert cols["edge"]["status"] == "ABSENT"


def test_report_partitions_are_consistent():
    # Every enabled user either has an activity date or never had one.
    out = summarize_export(V1, salt=SALT)["aggregates"]
    assert out["users_with_activity_date"] + out["never_active"] == out["enabled_users"]
    assert out["active_users_in_window"] <= out["users_with_activity_date"]


def test_idle_seats_use_a_caller_supplied_threshold_and_have_no_default():
    default = summarize_export(V1, salt=SALT)["aggregates"]
    assert default["idle_days"] is None
    assert default["idle_seats"] is None
    assert default["idle_policy"] == "value to be set by the data owner"
    assert summarize_export(V1, salt=SALT, idle_days=30)["aggregates"]["idle_seats"] == 4
    assert summarize_export(V1, salt=SALT, idle_days=7)["aggregates"]["idle_seats"] == 7
    users = summarize_export(V1, salt=SALT, idle_days=30)["users"]
    assert sum(1 for user in users if user["idle"]) == 4


def test_idle_needs_a_reference_date():
    out = summarize_export(ADMIN, salt=SALT, idle_days=7)
    assert out["as_of"] is None
    assert out["aggregates"]["idle_seats"] is None
    with_date = summarize_export(ADMIN, salt=SALT, idle_days=7, as_of="2026-10-20")
    assert with_date["aggregates"]["idle_seats"] == 2


def test_duplicates_missing_ids_and_bad_dates_are_excluded_with_a_reason():
    acc = summarize_export(MESSY, salt=SALT)["accounting"]
    assert acc["input_rows"] == 8
    assert acc["accepted"] == 2
    assert acc["excluded"] == 6
    assert acc["input_rows"] == acc["accepted"] + acc["excluded"]
    assert acc["balanced"] is True
    assert acc["excluded_by_reason"] == {
        "missing_user_id": 2,
        "duplicate_user_id": 2,
        "bad_date": 2,
        "malformed_row": 0,
    }
    assert {item["row"]: item["reason"] for item in acc["excluded_rows"]} == {
        3: "duplicate_user_id", 4: "duplicate_user_id",
        5: "missing_user_id", 6: "missing_user_id",
        7: "bad_date", 8: "bad_date",
    }


def test_first_row_wins_for_a_duplicate_id():
    users = summarize_export(MESSY, salt=SALT)["users"]
    first = next(u for u in users if u["user_pseudonym"] == pseudonymize("user-101", SALT))
    assert first["last_activity_date"] == "2026-10-19"


def test_bad_date_row_does_not_reserve_its_id():
    data = (V1.read_text().splitlines()[0] + "\n"
            "2026-10-20,user-900,x,not-a-date,,,,,,,,,28\n"
            "2026-10-20,user-900,x,2026-10-19,,,,,,,,,28\n").encode()
    acc = summarize_export(data, salt=SALT)["accounting"]
    assert (acc["accepted"], acc["excluded_by_reason"]["bad_date"]) == (1, 1)


def test_utf8_bom_and_utf16_exports_read_the_same():
    raw = V1.read_bytes()
    base = summarize_export(raw, salt=SALT)["aggregates"]
    bom = summarize_export(codecs.BOM_UTF8 + raw, salt=SALT)
    assert bom["aggregates"] == base
    assert bom["column_resolution"]["user_id"]["header"] == "User Principal Name"
    utf16 = summarize_export(V1.read_text().encode("utf-16"), salt=SALT)
    assert utf16["aggregates"] == base


def test_empty_files_do_not_crash():
    for payload in (b"", codecs.BOM_UTF8, b"\n\n"):
        out = summarize_export(payload, salt=SALT)
        assert out["warnings"] == ["empty_export"]
        assert out["accounting"]["input_rows"] == 0
        assert out["accounting"]["balanced"] is True
        assert out["aggregates"]["enabled_users"] == 0
    header_only = summarize_export(HEADER_ONLY, salt=SALT)
    assert header_only["warnings"] == ["empty_export"]
    assert header_only["accounting"]["accepted"] == 0


def test_privacy_no_raw_user_id_name_or_salt_in_output():
    for path in (V1, MESSY, BETA, ADMIN):
        dumped = json.dumps(summarize_export(path, salt=SALT, idle_days=7, as_of="2026-10-20"))
        assert "user-" not in dumped.lower()
        assert "Synthetic User" not in dumped
        assert SALT not in dumped
        assert "@" not in dumped
    out = summarize_export(V1, salt=SALT)
    assert out["salt_stored"] is False
    assert out["prompt_text_stored"] is False
    assert out["display_name_read"] is False
    assert "Display Name" not in out["columns_unrecognised"]
    for user in out["users"]:
        assert len(user["user_pseudonym"]) == 32
        assert set(user) == {"user_pseudonym", "last_activity_date", "app_last_activity", "idle"}


def test_pseudonyms_depend_on_the_salt_and_ignore_case():
    assert pseudonymize("user-001", "a") == pseudonymize(" USER-001 ", "a")
    assert pseudonymize("user-001", "a") != pseudonymize("user-001", "b")
    one = summarize_export(V1, salt="a")["users"][0]["user_pseudonym"]
    two = summarize_export(V1, salt="b")["users"][0]["user_pseudonym"]
    assert one != two


def test_salt_is_required_and_can_come_from_the_environment(monkeypatch):
    with pytest.raises(ValueError):
        summarize_export(V1)
    monkeypatch.setenv(SALT_ENV, SALT)
    assert summarize_export(V1)["users"][0]["user_pseudonym"] == pseudonymize("user-001", SALT)


def test_graph_beta_json_shape():
    out = summarize_export(BETA, salt=SALT)
    assert out["window_days"] == 7
    agg = out["aggregates"]
    assert (agg["enabled_users"], agg["users_with_activity_date"], agg["active_users_in_window"]) == (4, 3, 2)
    assert agg["active_per_app"]["teams"] == {"with_activity_date": 2, "active_in_window": 1}
    assert agg["active_per_app"]["word"] == {"with_activity_date": 1, "active_in_window": 1}
    assert out["column_resolution"]["last_activity"]["status"] == "VERIFIED"


def test_admin_center_labels_are_marked_open_not_verified():
    out = summarize_export(ADMIN, salt=SALT, as_of="2026-10-20", window_days=28)
    cols = out["column_resolution"]
    assert cols["user_id"] == {"header": "User name", "status": "OPEN"}
    assert cols["last_activity"]["status"] == "OPEN"
    assert cols["copilot_chat_work"]["status"] == "OPEN"
    agg = out["aggregates"]
    assert (agg["enabled_users"], agg["users_with_activity_date"], agg["active_users_in_window"]) == (3, 2, 2)
    assert agg["active_per_app"]["teams"]["with_activity_date"] == 1
    assert agg["active_per_app"]["copilot_chat_work"]["with_activity_date"] == 1
    assert "Display name" not in out["columns_unrecognised"]


def test_column_map_overrides_and_rejects_typos():
    data = b"Principal,Seen\nuser-1,2026-10-01\nuser-2,\n"
    out = summarize_export(data, salt=SALT, column_map={"user_id": "Principal", "last_activity": "Seen"})
    assert out["column_resolution"]["user_id"] == {"header": "Principal", "status": "CONFIGURED"}
    assert out["aggregates"]["users_with_activity_date"] == 1
    with pytest.raises(ExportError):
        summarize_export(data, salt=SALT, column_map={"user_id": "Nope"})
    with pytest.raises(ExportError):
        summarize_export(data, salt=SALT, column_map={"not_a_field": "Principal"})
    with pytest.raises(ExportError):
        summarize_export(data, salt=SALT)  # no recognisable user id column


def test_bad_parameters_are_rejected():
    for kwargs in ({"idle_days": 0}, {"window_days": -1}, {"idle_days": True}, {"as_of": "20-10-2026"}):
        with pytest.raises(ValueError):
            summarize_export(V1, salt=SALT, **kwargs)


def test_malformed_json_rows_are_accounted_for():
    data = json.dumps({"value": [
        {"userPrincipalName": "user-1", "lastActivityDate": "2026-10-01"}, "oops", 7,
    ]}).encode()
    acc = summarize_export(data, salt=SALT)["accounting"]
    assert (acc["input_rows"], acc["accepted"], acc["excluded_by_reason"]["malformed_row"]) == (3, 1, 2)
    with pytest.raises(ExportError):
        summarize_export(b'{"value": [', salt=SALT)


def test_snapshot_fallback_is_unchanged_without_an_export():
    out = ingest()
    assert out["status"] == "PARTIAL"
    assert [row["source"] for row in out["rows"]] == [
        "azure_sponsorship_balance_card",
        "azure_sponsorship_usage_table",
        "cowork_my_tasks",
    ]
    assert out["missing_inputs"] == [
        "Graph Copilot usage reports",
        "Analytics CSV",
        "Studio/AOAI logs",
        "exact user prompts",
        "cross-team prompt corpus",
    ]


def test_ingest_with_an_export_adds_one_row_and_stays_partial():
    out = ingest(export_path=V1, salt=SALT, idle_days=30)
    assert out["status"] == "PARTIAL"
    assert out["rows"][:3] == ingest()["rows"]
    row = out["rows"][3]
    assert row["source"] == "copilot_usage_export"
    assert row["aggregates"]["idle_seats"] == 4
    assert "Graph Copilot usage reports" not in out["missing_inputs"]
    assert "exact user prompts" in out["missing_inputs"]
    dumped = json.dumps(out).lower()
    for word in ("proved", "confirmed", "savings_usd"):
        assert word not in dumped


def test_cli_prints_json_and_needs_a_salt(monkeypatch, capsys):
    assert main(["--export", str(V1)]) == 2
    assert "salt is required" in capsys.readouterr().err
    monkeypatch.setenv(SALT_ENV, SALT)
    assert main(["--export", str(V1), "--idle-days", "30"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["rows"][3]["accounting"]["accepted"] == 10
    assert main(["--export", str(V1.with_name("missing.csv"))]) == 2
