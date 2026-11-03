# Handoff for Solance/GPT: Open-Addressing Causal Probe

Status tags: **PROPOSED / ONGOING**. These are never upgraded by this document. Nothing here is a proof, and nothing certifies an agent. The paper is used only as an analogy.

## What the probe is
It is based on Farach-Colton, Krapivin, Kuszmaul, *Optimal Bounds for Open Addressing Without Reordering* (arXiv:2501.02305v2):
- Elastic hashing (Thm 1, non-greedy): O(1) amortized, O(log 1/δ) worst-case expected probes.
- Funnel hashing (Thm 2, greedy): O(log² 1/δ). This disproves Yao's conjecture.
- Uniform probing is the baseline.

How the paper maps onto agent frame logic (`probes/oa/oa_probe.py` + vendored `probes/oa/causal.py`):
- **Receipts never move.** A placed receipt keeps its slot, and an audit checks this.
- **NOT_YET.** A causal-order lookup made before the receipt exists returns NOT_YET.
- **δ is required.** The caller must supply δ (the empty fraction of the table). With no δ, the result is **NO_VERDICT**. The probe never guesses δ.
- **LOST ≠ FOUND.** The two are distinct verdicts.
- **Act=0 ≠ Stop.** The answer is still emitted, and the output is exactly `[V] body`.
- **Authority fence.** A found entry never authorizes anything. `act_for` requires an HMAC signature from a key in `Authority.keys`.

## Where it lives
| Repo | PR | Merge commit |
|---|---|---|
| grok-terminal | https://github.com/Manny536/grok-terminal/pull/15 | f6e4876eb32b535e043fc40414183d8b6054587b |
| AIce | https://github.com/Manny536/AIce/pull/11 | cd94a2044b7179c82a5dbfae40f2d179215f6a3b |
| kakeyalogic | https://github.com/Manny536/kakeyalogic/pull/29 | 58f55a2792dd6c325750738e5eec8521141f33b1 |

The source is `feat/oa-probe` at 97064b1 (local cwi-main). The files are `docs/OA_PROBE*.{md,json}`, `probes/oa/`, the tests (`tests/` or `probe_tests/oa/`), `scripts/oa_experiment.py` and `scripts/oa_mutation_smoke.py`. Run pytest; the script alone misses some faults.

The last commits on #15 (3b7dbf8) and #11 (8b8efc9) were CI-only. They switched Pylint to a single Python 3.12 job and edited `.pylintrc`. They did not change the probe, the tests or the prereg.

## Results
- The predictions were pre-registered (prereg hash pinned). One smoke run was seen before freezing, and the prereg discloses this.
- v2 results: **7/8 confirmatory predictions hold.** P3 (elastic amortized cost stays flat) **fails**, and its cause is **OPEN**. An exploratory sweep over c (not pre-registered) made P3 worse, so n being too small is the more likely explanation. That explanation is unconfirmed.

## Blind review (L)
- Round 1: 11 fault variants and 9 fixes, all applied.
- Round 2: 18 fault variants. 15 were detected at first; after 7 more fixes, all 18 make pytest fail.

## Known flaw (identified by Solance): NOT YET APPLIED
`scripts/oa_mutation_smoke.py` treats any nonzero pytest exit as KILLED, so a crash or an import error counts as a detection. That means the "18/18" count cannot tell real detections from errors. The main test suite is not affected.

Proposed fix, pending Manuel's okay:
1. Run a passing baseline against the unmodified probe first.
2. Classify each variant as DETECTED (named failing test), UNDETECTED, or EXECUTION_ERROR.
3. Adopt the PTP-001 vocabulary: FAULT_VARIANT / DETECTED / UNDETECTED.
4. Recount, then send the counts to L for blind review.

## Open items
- AIce prereg shipped as `.gz` (needs Manuel's decision).
- The vendored `probes/oa/causal.py` still carries Kakeyalogic's slide-21 seal line, unchanged and kept byte-identical. Whether to reword it is Manuel's call.
- kakeyalogic CI has no pytest step for `probe_tests/oa` yet. Adding one requires a `.github/workflows` edit, which needs the GitHub `workflow` scope.
- kakeyalogic PR #26 (Solance's SIUS protected-tokens and Pylint fix) is still a draft and was not touched.
