# KNS(LB) × CP-003 Energy Table (OB-KNS-2 exhibit)

**Status:** `NUMERICS` · single-runner · deterministic ·
run: `python3 kns_lb_probe.py` · sha256 `09ef26d3a2eb…8211b011` · py 3.12.3

| Lane | Steps | ℓ_off^T | E_used | ρ_Y | dense_pass |
|---|---|---|---|---|---|
| **KNS(LB) aligned (this pass)** | 2 | 0.010152 | **3.0406** | **0.4812** | **True** |
| MPR+iPiano (CP-003 seed-7, REGISTERED) | 2 | low | ≈ 3.34 | ≈ 0.438 | True |
| F5-MM pool (CP-003 seed-7, REGISTERED) | many | ≈ 0.88 | ≈ 68.93 | ≈ 0.054 | False |

Proposition 6.1 clauses: (i) E_used = 3.04 ≤ E_KNS* = 10 ✅ ·
(ii) ℓ_off^T = 0.0102 < 0.20 ✅ · (iii) ρ_Y = 0.481 ≥ 0.4 ✅ ·
(iv) L²_C retention min 0.99014 over t ∈ [0,6] (two-level toy, κ=0.1) ✅.
F-KNS-5 did **not** fire. KNS(LB) lands in the MPR+iPiano action class
(~20.7× below pooling masquerade), per design intent.

## Honesty block (mandatory reading)

- **H1** — ℓ_off in the rank-one register model depends only on center
  placement; the direction fan enters L²_C dimension bookkeeping, not
  leakage. That *is* the typed point (Prop 3.3), not a model gap.
- **H2** — Aligned-lane E_used is **ledger-determined**: with ℓ_off ≈ 0,
  E ≈ steps·(1+r) by arithmetic. CP-001 Track-B class caveat: the exhibit
  demonstrates the accounting; it is not independent empirical evidence.
- **H3** — Calibration imports: r_t = 0.5 and Y·compress = 1.463 are
  back-solved from the CP-003 seed-7 MPR+iPiano receipt (ρ_Y ≈ 0.438 @
  E ≈ 3.34). Independent measurement of Y is a **CP-004 stamped-re-run
  obligation** (`cp_verify.py` harness).
- Single-runner honesty: one machine, one interpreter; portability claim
  limited to stdlib determinism.
