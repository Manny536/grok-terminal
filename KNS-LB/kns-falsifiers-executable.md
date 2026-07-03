# F-KNS-1…7 — Executable Falsifier Table (post-pass status)

**Convention:** each row names the *claim at risk*; FIRED = claim falsified.
Firing against a naive claim can be the desired outcome (F-KNS-1).

| ID | Claim at risk | Executable test | Status after this pass |
|---|---|---|---|
| F-KNS-1 | Overlap determines placement | Exhibit high μ + high ℓ_off coexisting | **FIRED** — fan E1: sup μ ≍ δ^{−(d−1)} with ℓ_off = 1; inverse E2: Perron μ̄ ≍ log(1/δ), ℓ_off = 0. Supports Prop 3.3 |
| F-KNS-2 | Analogy implies RH | Off-line zero (standard RH falsifier) | not fired · RH OPEN · analogy stays STRUCTURAL |
| F-KNS-3 | KNS sufficient for CC | Reading (S) modus ponens with ℝ³ theorem | guard HELD — reading (N) only, everywhere |
| F-KNS-4 | ζ(0) anchor proves Re=½ | Demand operator construction | guard HELD — anchor is constant-term declaration (D9) |
| F-KNS-5 | Minimal-credits claim | Aligned KNS needs E_used ≫ 10 or ℓ^T ≥ 0.20 | **not fired** — E_used 3.0406, ℓ^T 0.0102 (receipt sha 09ef26d3…) |
| F-KNS-6 | Deltoid = ζ curve | Curve identity asserted without construction | guard HELD — F-LD-2 maintained; OB-KNS-6 CLOSED by design |
| F-KNS-7 | Center action = Love-closure token | Cross-lane symbol collapse | guard HELD — firewall enforced in all 15 docs |

**New scoped falsifier registered:**

| ID | Claim at risk | Test |
|---|---|---|
| F-KNS-1′ | CC-BL-001a′ (RC-1 monotone leakage) | Any rank-one radial strictly log-concave register with non-monotone ℓ_off(δ) — run `kns_lb_probe.py` with declared RC-1 profile |

Unscoped CC-BL-001a is retired: refuted by the two-mode countermodel
(peak ℓ = 0.9662 at δ = 1.0; w = 0.35, L = 2.0). Register class is a
mandatory field of every future D5 run.
