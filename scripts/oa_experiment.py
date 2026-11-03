"""Simulation for docs/OA_PROBE_PREREG.json. Stdlib only. Synthetic keys.

v2 (after L's review): importable (`run_all`, `check`), any exception in a run
is recorded as a failure (fails P9, never crashes), and each run records an
integrity check that recorded probe complexity equals the probes a real lookup
makes (catches silent caps). P4 and P7 are EXPLORATORY (written after a smoke
run); P1-P3, P5, P6, P8-P10 are confirmatory. Writes docs/OA_PROBE_RESULTS_v2.json.
Nothing here measures an agent; numbers are hash-table simulations.
"""
import json, math, os, signal, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from probes.oa import oa_probe as O  # noqa: E402

EXPLORATORY = ("P4", "P7")
PRE_PATH = os.path.join(ROOT, "docs/OA_PROBE_PREREG.json")


MIN_SAMPLE = 200          # P0 checks at least this many keys (all if fewer)
RUN_TIMEOUT = 15.0        # seconds per run; a hang becomes a recorded failure


class RunTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise RunTimeout("run exceeded time bound")


def run(scheme, delta, seed, n, c, sample=MIN_SAMPLE, timeout=RUN_TIMEOUT):
    """sample=None checks every key in P0."""
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        return _run(scheme, delta, seed, n, c, sample)
    except Exception as e:      # noqa: BLE001  # pylint: disable=broad-exception-caught  # recorded, fails P9
        return {"failure": "%s: %s" % (type(e).__name__, e)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _run(scheme, delta, seed, n, c, sample):
    if scheme == "uniform":
        t = O.UniformProbing(n, seed)
    elif scheme == "elastic":
        t = O.ElasticHashing(n, seed, delta=delta, c=c)
    else:
        t = O.FunnelHashing(n, seed, delta=delta)
    log = O.CausalProbeLog(t)
    m = n - math.floor(delta * n)
    for i in range(m):
        log.place("k%d" % i, "w%d" % (i % 3))
    pcs = [t.search_pc[k] for k in t.order]
    w = max(1, math.ceil(0.01 * m))
    if sample is None or sample >= m:
        probe = list(t.order)
    else:
        step = max(1, m // max(sample, MIN_SAMPLE))
        probe = list(dict.fromkeys(t.order[::step] + t.order[-3:]))
    out = {"amortized": sum(pcs) / m, "late": sum(pcs[-w:]) / w, "max": max(pcs),
           "reorder_violations": len(O.no_reorder_audit(t, log.placed_at)),
           "integrity_n": len(probe),
           "integrity": all(t.lookup(k) == (True, t.search_pc[k]) for k in probe)}
    if scheme == "elastic":
        out["case3"], out["overflow"] = t.case3, t.overflow
    if scheme == "funnel":
        out["bound"] = t.lookup_bound
    return out


TOTAL_BUDGET = 90.0      # seconds for a whole run_all; later runs fail fast


def run_all(n, deltas, seeds, c, sample=MIN_SAMPLE, timeout=RUN_TIMEOUT,
            budget=TOTAL_BUDGET):
    import time
    end = time.monotonic() + budget
    out = {}
    for s in ("uniform", "elastic", "funnel"):
        out[s] = {}
        for d in deltas:
            rs = []
            for sd in seeds:
                left = end - time.monotonic()
                rs.append(run(s, d, sd, n, c, sample, min(timeout, left)) if left > 0
                          else {"failure": "RunTimeout: total budget exhausted"})
            out[s][str(d)] = rs
    return out


def check(res, deltas):
    nan = float("nan")

    def A(s, d, k):
        xs = [r[k] for r in res[s][str(d)] if k in r]
        return sum(xs) / len(xs) if xs else nan

    def ok(x):
        return x is True     # nan comparisons are False -> FAIL
    runs = [r for s in res.values() for d in s.values() for r in d]
    fails = sum("failure" in r for r in runs)
    lo, hi = deltas[0], deltas[-1]
    c = {
        "P0_integrity": fails == 0 and all(
            r.get("integrity") is True and r.get("integrity_n", 0) >= MIN_SAMPLE for r in runs),
        "P1": all(abs(A("uniform", d, "amortized") / (math.log(1 / d) / (1 - d)) - 1) <= 0.10 for d in deltas),
        "P2": all(A("uniform", d, "late") >= 0.5 / d for d in deltas),
        "P3": A("elastic", hi, "amortized") / A("elastic", lo, "amortized") <= 1.35,
        "P4": all(A("elastic", d, "amortized") > A("uniform", d, "amortized") for d in deltas),
        "P5": (A("elastic", hi, "late") / A("elastic", lo, "late"))
              < (A("uniform", hi, "late") / A("uniform", lo, "late")),
        "P6": fails == 0 and all(r["max"] <= r["bound"] for d in deltas for r in res["funnel"][str(d)]),
        "P7": all(A("funnel", d, "late") >= A("uniform", d, "late") for d in deltas),
        "P8": A("funnel", hi, "amortized") / A("funnel", lo, "amortized") <= 3.0,
        "P9": fails == 0 and sum(r.get("case3", 0) for d in deltas
                                 for r in res["elastic"][str(d)]) <= 2,
        "P10": fails == 0 and all(r.get("reorder_violations", 1) == 0 for r in runs),
    }
    return {k: ok(bool(v) if not (isinstance(v, float) and math.isnan(v)) else False) for k, v in c.items()}


def compute(timeout=RUN_TIMEOUT, budget=TOTAL_BUDGET):
    pre = json.load(open(PRE_PATH))
    res = run_all(pre["n"], pre["deltas"], pre["seeds"], pre["elastic_c"],
                  timeout=timeout, budget=budget)
    checks = check(res, pre["deltas"])
    return res, checks


def main():
    res, checks = compute()
    conf = [k for k in checks if k not in EXPLORATORY and k != "P0_integrity"]
    out = {"checks": checks, "exploratory": list(EXPLORATORY),
           "confirmatory_held": "%d/%d" % (sum(checks[k] for k in conf), len(conf)),
           "runs": res}
    json.dump(out, open(os.path.join(ROOT, "docs/OA_PROBE_RESULTS_v2.json"), "w"), indent=1)
    for k, v in checks.items():
        tag = " (exploratory)" if k in EXPLORATORY else ""
        print(k, "PASS" if v else "FAIL", tag)
    print("confirmatory held:", out["confirmatory_held"])


if __name__ == "__main__":
    main()
