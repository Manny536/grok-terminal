# OA probe: causal order x open addressing without reordering

**Status: PROPOSED / ONGOING.** Tests carry the pytest marker `ongoing`
(`pytest -m ongoing`). Passing is not validation: one author wrote the code,
the tests and the mutants. Nothing here is a measurement of an agent.

## Source (read in full: arXiv:2501.02305v2, 22 pp.)
Farach-Colton, Krapivin, Kuszmaul, *Optimal Bounds for Open Addressing Without Reordering*.
- **Theorem 1 (Sec. 2, elastic hashing):** without reordering, amortized expected
  probe complexity O(1), worst-case expected O(log 1/delta), insertion time O(log 1/delta).
  Needs non-greedy insertion (probe deep, place early). Lemmas 1-4.
- **Theorem 2 (Sec. 3, funnel hashing):** a *greedy* scheme with worst-case expected
  O(log^2 1/delta), and whp worst case O(log^2 1/delta + log log n), and amortized O(log 1/delta). This
  disproves Yao's 1985 conjecture that greedy needs (1-o(1))/delta.
- **Lower bounds:** Thm 4 (greedy final insertion Omega(log^2 1/delta)); Thm 5 (any
  no-reorder scheme: worst-case expected Omega(log 1/delta)); Thms 6-7 (whp worst case
  Omega(log^2 1/delta + log log n), even non-greedy). Uniform probing: Theta(log 1/delta)
  amortized, O(1/delta) worst-case expected (Sec. 1).
- Sec. 1 also notes: with deletions over an infinite horizon the optimal amortized
  bound is delta^(-Omega(1)) (citing [3]), so Theorems 1-2 do not carry over.

## Mapping (ANALOGY, tagged)
| paper | here | tag |
|---|---|---|
| no reordering | placed receipt never moves; `no_reorder_audit` checks it | analogy + checked |
| probe sequence | bounded lookup path for a receipt | analogy |
| load 1 - delta | coverage target; delta caller-supplied, none -> NO_VERDICT | analogy |
| (not in paper) | Lamport/vector order decides visibility: causally-later -> NOT_YET | our construction |

The paper proves nothing about AI systems. Fences kept: found != authority
(`act_for` ignores lookup and requires an HMAC under `Authority.keys`; found data
chunks never authorize -- tested); Act = S*H*U with H and U undefined in this repo,
so `act_for` is only the S-side check; Act=0 != Stop (`release_note` returns exactly
`[VERDICT] body`, no STOP/withheld text -- tested); LOST != FOUND (tested); nothing
certifies an agent or closes L2_C. **h<1 boundary:** the influence of personal data
on any verdict stays below 1; keys are opaque synthetic ids, no personal data read
or stored. `oa_probe.py` carries no slide-21 seal claim (it is a PROPOSED / ONGOING
probe); `tests/test_package.py` exempts it by name and checks it makes no seal claim.

## Files
`kakeya_checks/oa_probe.py`, `tests/test_oa_probe.py` (35 tests), `tests/oa_mutants.py`
(8 mutants), `scripts/oa_mutation_smoke.py`, `scripts/oa_experiment.py`,
`docs/OA_PROBE_PREREG.json` (frozen in its own commit; see Errata), `docs/OA_PROBE_RESULTS.json`.

Deviations: funnel D1 (bucket counts clamped >= 1 at small n), D2 (C overflow raises);
elastic finishes greedily if batches outrun arrays (0 times in runs); random probing
uses iid probes (Sec. 5 model), not permutations.

## Preregistration vs results (n=16384, delta 1/8..1/64, 3 seeds, c=2)
9 of 10 predictions held. **P3 FAILED:** elastic amortized grew 116 -> 216 (ratio
1.86 > 1.35); it was not flat in delta at this n. Not diagnosed; candidate causes
(phi constants growing with batch index i, finite n) are OPEN. Elastic was also far
worse than uniform in absolute terms at every delta (P4, as predicted), and funnel's
late-window cost was above uniform's at every tested delta (P7, as predicted): the
paper's wins are asymptotic and not visible at these sizes. Elastic's late cost grew
slower than uniform's (P5 held): 1.36x vs 6.5x.

Mutants: first round 7/8 killed (`greedy_elastic` survived: the non-greedy test was
too weak); added the Sec. 2 decoupling test; now 8/8. Existing suite 5/5 unchanged.

## "Unbound parse?"
Bounded (in the paper's model, with random probes, fixed delta > 0, no deletions):
positive lookup of a placed entry, without moving anything placed earlier:
O(1) amortized / O(log 1/delta) worst-case expected (elastic), O(log^2 1/delta + log log n)
whp worst case (funnel; structural cap checked by P6). Unbounded: (a) delta -> 0, i.e.
"100% coverage" -- every bound grows with log 1/delta and the table cannot be full;
(b) the log log n term in n, which Thm 7 says no no-reorder scheme avoids; (c) retractions
as deletions over unbounded time (delta^(-Omega(1)), cited in Sec. 1); (d) negative
lookups for elastic (paper gives none); (e) anything about whether an agent actually
read a receipt -- the paper is silent on that.


## Review round 2 (L, "merge with fixes") -- changes and errata
**Errata (commit message of c57f351).** It says the prereg was committed "before any
run". That is false as stated: c57f351 (16:56:20 PT) and 05286a5 (16:57:51 PT) are
91 s apart, and a smoke run of the code had already happened before c57f351.
c57f351 did **not** contain `kakeya_checks/oa_probe.py`; the smoke-run code was an
uncommitted working tree. History is not rewritten; this note is the correction.

**Code hash freeze.** Results in `OA_PROBE_RESULTS.json` came from `oa_probe.py` at
05286a5, sha256 `a260a301952aba9823a3bda6cb78baf48c29283c4385df9950a6940ef49d9161`.
After the smoke run, only the module docstring (seal paragraph) changed before 05286a5;
this cannot be verified from history because the smoke code was never committed.

**Confirmatory vs exploratory.** P4 and P7 were written after the smoke run and are
EXPLORATORY. Confirmatory: P1, P2, P3, P5, P6, P8, P9, P10 -> **7/8 held** (P3 failed).
`scripts/oa_experiment.py` v2 also adds P0_integrity (recorded probe complexity ==
real lookup probes on a sample; no run failures), records any exception as a run
failure (P9/P10 fail instead of the experiment crashing), and writes
`OA_PROBE_RESULTS_v2.json` (same 7/8 confirmatory, P0 pass).

**c below the paper's constant (P3 diagnosis OPEN).** Theorem 1 needs c to be a
"sufficiently large constant"; the prereg froze c=2, below that. P3's failure may be
tied to it; diagnosis is OPEN. An EXPLORATORY sweep (`OA_PROBE_EXPLORATORY_C.json`,
n=16384, seed 0) does **not** support "larger c fixes it" at this n: the 1/64-vs-1/8
amortized ratio is 1.91 (c=2), 2.53 (c=4), 3.23 (c=8), 4.12 (c=16). Plausible
alternative: n=16384 is too small for the asymptotic O(1) regime. Not decided.

**Tests added:** harness (prereg checks rerun on a small config; TableFailure and
any exception fail P9/P10 without crashing), delta shapes funnel and elastic, f grows
as arrays fill, signed-key authority fence, found data never authorizes, exact Act=0
body, LOST != FOUND, NO_VERDICT at any load, h<1 boundary stated.

## Review round 3 (L r2, head 0343136: 15/18 killed) -- changes
- Funnel overflow: a test fills every slot in a key's probe sequence (both C buckets
  full) and asserts TableFailure with no slot changed.
- Prereg pinned: `docs/OA_PROBE_PREREG.json` sha256 `0bbecb50...8138` is checked in a
  test; the prereg text must state each threshold, and synthetic inputs either side
  of each one pin P1 (+-10%), P2 (0.5/delta), P3 (1.35), P8 (3.0), P9 (<= 2).
- P0 checks at least 200 keys per run (`MIN_SAMPLE`; all keys if fewer) and the
  small-config harness checks every key. A test makes one middle key lie and one
  late key lie; P0 must catch both.
- The harness reruns the full prereg config and fails if any check outcome differs
  from the committed `OA_PROBE_RESULTS_v2.json` (catches silent P3 flips).
- Time bounds: 15 s per run and 90 s for a whole `run_all`; a hang is recorded as a
  failure (P0/P9/P10 FAIL), not an endless run.
- Lookup-side cap: a second test recounts the probes of keys past 200 by walking
  the probe sequence directly and compares to `lookup()` and the recorded value.
- `tests/test_package.py`: probes still must name "engineering kernel" and "not
  validated"; only the seal-text checks are dropped; `ONGOING_PROBES == {"oa_probe"}`.

## Vendored copy (grok-terminal)
Vendored from cwi-main@97064b1; see `probes/oa/VENDORED.md`. Paths in the history above
refer to cwi-main (`kakeya_checks/oa_probe.py` -> `probes/oa/oa_probe.py`, `tests/` ->
`tests/`). cwi-main's `tests/test_package.py` exemption is not ported.

**Running `scripts/oa_experiment.py` alone does not catch mutants R01, R05b, R14
or L3b** (the script prints no FAIL under them). Only the pytest suite catches them:
`python -m pytest tests/test_oa_probe.py` is required.
