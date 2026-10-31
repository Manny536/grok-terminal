"""PROPOSED / ONGOING probe tests: causal order x open addressing without reordering.

ANALOGY ONLY (arXiv:2501.02305). Passing here is not validation: same author
wrote the tests and the mutants. Set OA_MUTANT=<name> to run against a broken
variant; scripts/oa_mutation_smoke.py counts kills. Keys are synthetic ids (h<1).
"""
import math
import os

import pytest

from probes.oa import causal as C
from probes.oa import oa_probe as O

import oa_mutants  # noqa: E402  (test dir on sys.path)

pytestmark = pytest.mark.ongoing


@pytest.fixture(autouse=True)
def _mutant(monkeypatch):
    name = os.environ.get("OA_MUTANT")
    if name:
        oa_mutants.apply(name, monkeypatch)


def fill(table, m, workers=3):
    log = O.CausalProbeLog(table)
    for i in range(m):
        log.place("k%d" % i, "w%d" % (i % workers))
    return log


class TestPaperStructure:
    def test_phi_is_injective_and_lemma1_shape(self):
        seen = {}
        for i in range(1, 40):
            for j in range(1, 40):
                v = O.phi(i, j)
                assert v not in seen
                seen[v] = (i, j)
                assert O.phi_inv(v) == (i, j)
                assert math.log2(v) <= math.log2(i) + 2 * math.log2(j) + 4

    def test_elastic_rejects_delta_not_power_of_two(self):
        with pytest.raises(ValueError):
            O.ElasticHashing(1024, 0, delta=0.1, c=2)

    def test_elastic_is_non_greedy_somewhere(self):
        # Sec. 1: non-greedy behaviour is the only way past Yao's bound.
        t = O.ElasticHashing(1024, 1, delta=1 / 16, c=2)
        nongreedy = 0
        orig = t._put

        def spy(key, slot, pc, ins):
            nonlocal nongreedy
            nongreedy += O.greedy_violations(t, key, pc)
            return orig(key, slot, pc, ins)
        t._put = spy
        for i in range(1024 - 64):
            t.insert("k%d" % i)
        assert nongreedy > 0

    def test_elastic_decouples_insertion_from_search_probes(self):
        # Sec. 2 "Bypassing the coupon-collector bottleneck": some insertions
        # probe A_i past f(eps), fail, and land at a small j in A_{i+1}.
        t = O.ElasticHashing(1024, 1, delta=1 / 16, c=2)
        fill(t, 1024 - 64)
        spill = [k for k in t.order if t.insert_probes[k] > O.phi_inv(t.search_pc[k])[1]]
        assert len(spill) > 0

    @pytest.mark.parametrize("make", [lambda: O.UniformProbing(512, 2),
                                      lambda: O.FunnelHashing(512, 2, delta=1 / 8)])
    def test_greedy_schemes_never_skip_a_free_slot(self, make):
        t = make()
        orig = t._put
        bad = []

        def spy(key, slot, pc, ins):
            bad.append(O.greedy_violations(t, key, pc))
            return orig(key, slot, pc, ins)
        t._put = spy
        for i in range(448):
            t.insert("k%d" % i)
        assert not any(bad)

    def test_funnel_probe_complexity_bounded(self):
        t = O.FunnelHashing(4096, 3, delta=1 / 16)
        fill(t, 4096 - 256)
        assert max(t.search_pc.values()) <= t.lookup_bound

    def test_negative_control_uniform_late_cost_tracks_one_over_delta(self):
        t = O.UniformProbing(4096, 4)
        fill(t, 4096 - 64)
        late = [t.search_pc[k] for k in t.order[-40:]]
        assert sum(late) / len(late) > 20          # 1/delta = 64; funnel bound not met here

    def test_funnel_lookup_stays_under_bound_where_uniform_does_not(self):
        f, u = O.FunnelHashing(4096, 5, delta=1 / 64), O.UniformProbing(4096, 5)
        fill(f, 4096 - 64)
        fill(u, 4096 - 64)
        assert max(f.search_pc.values()) <= f.lookup_bound
        assert max(u.search_pc.values()) > 64


class TestNoReordering:
    @pytest.mark.parametrize("make", [lambda: O.UniformProbing(512, 0),
                                      lambda: O.ElasticHashing(512, 0, delta=1 / 8, c=2),
                                      lambda: O.FunnelHashing(512, 0, delta=1 / 8)])
    def test_placed_receipts_never_move(self, make):
        t = make()
        log = fill(t, 448)
        assert O.no_reorder_audit(t, log.placed_at) == []

    def test_lookup_cost_equals_recorded_probe_complexity(self):
        for t in (O.UniformProbing(512, 6), O.FunnelHashing(512, 6, delta=1 / 8),
                  O.ElasticHashing(512, 6, delta=1 / 8, c=2)):
            fill(t, 448)
            for k in t.order[::37]:
                assert t.lookup(k) == (True, t.search_pc[k])


class TestCausalOrder:
    def test_lookup_cannot_see_causally_later_receipt(self):
        log = O.CausalProbeLog(O.UniformProbing(64, 0))
        log.note("ask", "w1")
        log.place("r1", "w2")                   # concurrent with "ask"
        assert log.lookup("r1", "ask")[0] == "NOT_YET"

    def test_lookup_sees_receipt_after_message(self):
        log = O.CausalProbeLog(O.UniformProbing(64, 0))
        log.place("r1", "w2")
        log.note("ask", "w1", deps=["place:r1"])
        assert log.lookup("r1", "ask")[0] == "FOUND"

    def test_order_not_from_insertion_sequence(self):
        log = O.CausalProbeLog(O.UniformProbing(64, 0))
        log.note("ask", "w1")
        log.place("r9", "w3")
        log.note("later", "w1", deps=["ask"])   # same worker, no message from w3
        assert log.lookup("r9", "later")[0] == "NOT_YET"


class TestFences:
    def test_missing_delta_is_no_verdict(self):
        t = O.UniformProbing(64, 0)
        fill(t, 60)
        assert O.coverage_verdict(t, delta=None) == "NO_VERDICT"

    def test_threshold_is_callers(self):
        t = O.UniformProbing(64, 0)
        fill(t, 60)
        assert O.coverage_verdict(t, delta=1 / 8) == "AT_TARGET_LOAD"
        assert O.coverage_verdict(t, delta=1 / 64) == "BELOW_TARGET_LOAD"

    def test_found_is_not_authority(self):
        ch = C.Chunk("c", "s", "v", 0, 1, "h", "instruction", "stranger")
        auth = C.Authority({}, {}, frozenset({"manuel"}))
        assert O.act_for(ch, auth, found=True) == 0

    def test_act_zero_is_not_stop(self):
        for v in ("NO_VERDICT", "BELOW_TARGET_LOAD", "AT_TARGET_LOAD"):
            assert "partial answer" in O.release_note(v, "partial answer")

    def test_status_tags_present(self):
        assert "ONGOING" in O.STATUS and "analogy" in O.STATUS.lower()
        assert "proves nothing about" in O.__doc__


# ---- L review fixes (round 2) ---------------------------------------------

import hashlib as _hl  # noqa: E402
import importlib.util as _ilu  # noqa: E402

_spec = _ilu.spec_from_file_location(
    "oa_experiment", os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                  "scripts", "oa_experiment.py"))
EXP = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(EXP)
SMALL = dict(n=4096, deltas=[1 / 8, 1 / 64], seeds=[0], c=2)


class TestHarness:
    def test_prereg_harness_integrity_on_small_config(self):
        res = EXP.run_all(**SMALL, sample=None, timeout=8, budget=20)  # every key
        for runs in res.values():
            for rs in runs.values():
                for r in rs:
                    assert r["integrity_n"] == 4096 - math.floor(float(
                        [d for d in runs if runs[d] is rs][0]) * 4096)
        chk = EXP.check(res, SMALL["deltas"])
        assert chk["P0_integrity"] and chk["P6"] and chk["P9"] and chk["P10"]

    def test_table_failure_fails_p9_not_crash(self, monkeypatch):
        def boom(self, key):
            raise O.TableFailure("injected")
        monkeypatch.setattr(O.FunnelHashing, "insert", boom)
        res = EXP.run_all(n=256, deltas=[1 / 8], seeds=[0], c=2)
        chk = EXP.check(res, [1 / 8])
        assert chk["P9"] is False and chk["P0_integrity"] is False

    def test_any_exception_recorded_not_raised(self, monkeypatch):
        monkeypatch.setattr(O.ElasticHashing, "_f", lambda self, eps: 1 / 0)
        res = EXP.run_all(n=256, deltas=[1 / 8], seeds=[0], c=2)
        assert "failure" in res["elastic"]["0.125"][0]
        assert EXP.check(res, [1 / 8])["P10"] is False

    def test_exploratory_split(self):
        assert set(EXP.EXPLORATORY) == {"P4", "P7"}


class TestDeltaShapesTables:
    def test_funnel_shape_depends_on_delta(self):
        a, b = O.FunnelHashing(4096, 0, delta=1 / 8), O.FunnelHashing(4096, 0, delta=1 / 64)
        assert (a.alpha, a.beta) != (b.alpha, b.beta)
        assert b.lookup_bound > a.lookup_bound
        assert b.Bn + b.Cn < a.Bn + a.Cn

    def test_elastic_f_cap_depends_on_delta(self):
        a = O.ElasticHashing(4096, 0, delta=1 / 8, c=2)
        b = O.ElasticHashing(4096, 0, delta=1 / 64, c=2)
        assert b._f(1 / 4096) > a._f(1 / 4096)

    def test_elastic_f_grows_as_array_fills(self):
        e = O.ElasticHashing(4096, 0, delta=1 / 64, c=2)
        assert e._f(0.5) < e._f(0.3) < e._f(0.15)
        assert e._f(0.5) == math.ceil(2 * 1.0)          # c * log2(2)^2
        assert e._f(1e-9) == math.ceil(2 * 6)           # capped at c * log2(1/delta)


class TestFencesExact:
    def _auth(self):
        return C.Authority({}, {"manuel": b"k-manuel"}, frozenset({"manuel"}))

    def test_signed_instruction_from_actor_acts(self):
        ch = C.Chunk("c", "s", "v", 0, 1, "h", "instruction", "manuel")
        a = self._auth()
        assert O.act_for(ch, a, found=False, signature=O.sign_chunk(b"k-manuel", ch)) == 1

    def test_unsigned_or_wrong_key_does_not_act(self):
        ch = C.Chunk("c", "s", "v", 0, 1, "h", "instruction", "manuel")
        a = self._auth()
        assert O.act_for(ch, a, found=True) == 0
        assert O.act_for(ch, a, found=True, signature=O.sign_chunk(b"forged", ch)) == 0

    def test_found_data_chunk_never_authorizes(self):
        a = self._auth()
        for issuer in ("manuel", None, "stranger"):
            ch = C.Chunk("d", "s", "v", 0, 1, "h", "content", issuer)
            sig = O.sign_chunk(b"k-manuel", ch)
            assert O.act_for(ch, a, found=True, signature=sig) == 0

    def test_act_zero_body_exact(self):
        for v in ("NO_VERDICT", "BELOW_TARGET_LOAD", "AT_TARGET_LOAD"):
            out = O.release_note(v, "partial answer: x")
            assert out == "[%s] partial answer: x" % v
            assert "STOP" not in out and "withheld" not in out.lower()

    def test_lost_is_not_found(self):
        log = O.CausalProbeLog(O.UniformProbing(64, 0))
        log.place("r1", "w1")
        log.note("ask", "w1", deps=["place:r1"])
        t = log.table
        t.slots[t.pos["r1"]] = None             # receipt erased under the log
        assert log.lookup("r1", "ask")[0] == "LOST"

    def test_no_verdict_regardless_of_load(self):
        for m in (5, 60):
            t = O.UniformProbing(64, 0)
            fill(t, m)
            assert O.coverage_verdict(t, delta=None) == "NO_VERDICT"

    def test_h_lt_1_boundary_stated(self):
        doc = " ".join(O.__doc__.split())
        assert "h<1 boundary" in doc and "below 1" in doc
        assert "seal status" not in doc.lower()


# ---- L review round 2 -------------------------------------------------------

import json as _json  # noqa: E402

DOCS = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "docs")
PREREG_SHA256 = "0bbecb50e7ff3dc27ee1d0b7fb5869ae7ee76043829ed43f746b5dd4ac7a8138"


def _synthetic(el_ratio=1.0, el_late_ratio=1.0, uni_scale=1.0, uni_late=None,
               fun_ratio=1.0, case3=0, deltas=(1 / 8, 1 / 64)):
    hi = deltas[-1]
    res = {"uniform": {}, "elastic": {}, "funnel": {}}
    for d in deltas:
        u = uni_scale * math.log(1 / d) / (1 - d)
        ul = (1.0 / d) if uni_late is None else uni_late / d
        base = dict(max=1, bound=10, reorder_violations=0, integrity=True,
                    integrity_n=EXP.MIN_SAMPLE)
        res["uniform"][str(d)] = [dict(base, amortized=u, late=ul)]
        res["elastic"][str(d)] = [dict(base, amortized=100 * (el_ratio if d == hi else 1),
                                       late=10 * (el_late_ratio if d == hi else 1),
                                       case3=case3, overflow=0)]
        res["funnel"][str(d)] = [dict(base, amortized=10 * (fun_ratio if d == hi else 1),
                                      late=1e9)]
    return res


class TestPreregPinned:
    D = [1 / 8, 1 / 64]

    def test_prereg_file_hash_frozen(self):
        h = _hl.sha256(open(os.path.join(DOCS, "OA_PROBE_PREREG.json"), "rb").read())
        assert h.hexdigest() == PREREG_SHA256

    def test_prereg_text_states_thresholds(self):
        p = _json.load(open(os.path.join(DOCS, "OA_PROBE_PREREG.json")))["predictions"]
        assert "<= 1.35" in p["P3"] and "0.5/delta" in p["P2"]
        assert "+-10%" in p["P1"] and "<= 3.0" in p["P8"] and "<= 2" in p["P9"]

    def test_p3_threshold_is_1_35(self):
        assert EXP.check(_synthetic(el_ratio=1.34), self.D)["P3"] is True
        assert EXP.check(_synthetic(el_ratio=1.36), self.D)["P3"] is False

    def test_p1_threshold_is_10_percent(self):
        assert EXP.check(_synthetic(uni_scale=1.09), self.D)["P1"] is True
        assert EXP.check(_synthetic(uni_scale=1.11), self.D)["P1"] is False
        assert EXP.check(_synthetic(uni_scale=0.89), self.D)["P1"] is False

    def test_p2_threshold_is_half_over_delta(self):
        assert EXP.check(_synthetic(uni_late=0.51), self.D)["P2"] is True
        assert EXP.check(_synthetic(uni_late=0.49), self.D)["P2"] is False

    def test_p8_threshold_is_3(self):
        assert EXP.check(_synthetic(fun_ratio=2.99), self.D)["P8"] is True
        assert EXP.check(_synthetic(fun_ratio=3.01), self.D)["P8"] is False

    def test_p9_case3_threshold_is_2(self):
        assert EXP.check(_synthetic(case3=1), self.D)["P9"] is True
        assert EXP.check(_synthetic(case3=3), self.D)["P9"] is False

    def test_p0_requires_min_sample(self):
        r = _synthetic()
        r["funnel"]["0.125"][0]["integrity_n"] = 1
        assert EXP.check(r, self.D)["P0_integrity"] is False
        assert EXP.MIN_SAMPLE >= 200


class TestHarnessRound2:
    def test_outcomes_match_committed_results(self):
        committed = _json.load(open(os.path.join(DOCS, "OA_PROBE_RESULTS_v2.json")))
        _, checks = EXP.compute(timeout=8, budget=30)   # normal: ~4 s total
        assert checks == committed["checks"]          # any flip (e.g. P3) fails

    def test_p0_sees_a_bad_late_key(self, monkeypatch):
        real = O._Table.lookup

        def lying(self, key, limit=None):
            f, t = real(self, key, limit)
            return (f, t + 1) if key == self.order[-1] else (f, t)
        monkeypatch.setattr(O._Table, "lookup", lying)
        r = EXP.run("funnel", 1 / 8, 0, 1024, 2)
        assert r["integrity"] is False

    def test_p0_sees_a_bad_middle_key(self, monkeypatch):
        real = O._Table.lookup

        def lying(self, key, limit=None):
            f, t = real(self, key, limit)
            return (f, t + 1) if key == "k100" else (f, t)
        monkeypatch.setattr(O._Table, "lookup", lying)
        r = EXP.run("uniform", 1 / 8, 0, 256, 2)          # m < MIN_SAMPLE*... -> all keys
        assert r["integrity"] is False

    def test_hang_becomes_failure(self, monkeypatch):
        def spin(self, key):
            while True:
                pass
        monkeypatch.setattr(O.UniformProbing, "insert", spin)
        r = EXP.run("uniform", 1 / 8, 0, 64, 2, timeout=0.5)
        assert "failure" in r and "RunTimeout" in r["failure"]

    def test_total_budget_bounds_run_all(self, monkeypatch):
        def spin(self, key):
            while True:
                pass
        monkeypatch.setattr(O.UniformProbing, "insert", spin)
        import time
        t0 = time.monotonic()
        res = EXP.run_all(n=64, deltas=[1 / 8], seeds=[0, 1, 2], c=2, timeout=5, budget=1)
        assert time.monotonic() - t0 < 3
        assert all("failure" in r for r in res["uniform"]["0.125"])


class TestFunnelOverflow:
    def test_full_c_buckets_raise_and_overwrite_nothing(self):
        t = O.FunnelHashing(1024, 0, delta=1 / 8)
        for i in range(1000):
            key = "x%d" % i
            seq = [s for _, s in t.probe_seq(key)]
            if t.C0 not in seq:
                break
        for s in seq:
            t.slots[s] = "filler"
        before = list(t.slots)
        with pytest.raises(O.TableFailure):
            t.insert(key)
        assert t.slots == before and key not in t.pos
        assert sum(s == "filler" for s in t.slots) == len(set(seq))


class TestLookupSideCap:
    def test_lookup_count_matches_independent_walk_above_200(self):
        e = O.ElasticHashing(2048, 0, delta=1 / 64, c=2)
        fill(e, 2048 - 32)
        big = [k for k in e.order if e.search_pc[k] > 200]
        assert big, "need keys past 200 probes"
        for k in big[:20]:
            want = next(t for t, s in e.probe_seq(k) if s == e.pos[k])
            assert e.lookup(k) == (True, want)
            assert want == e.search_pc[k] and want > 200
