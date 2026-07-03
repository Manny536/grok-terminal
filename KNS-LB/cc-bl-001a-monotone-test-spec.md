# CC-BL-001a — D5 Monotone Placement Test Specification

**Status:** split verdict this pass — unscoped claim `REFUTED`; scoped claim
`CC-BL-001a′` `FORMAL` (rank-one radial log-concave register class),
`PROPOSED-FOR-CANON`. Simulator hook: `kns_lb_probe.py`.

## Claim under test

Original (scaffold §5): misalign center C under π_A; ℓ_off increases
monotonically with offset δ. Falsifier: no monotone growth ⇒
placement=leakage map fails.

## Verdict structure (binding for all D5 runs)

1. **Theorem (scoped, FORMAL).** Register A = span{τ_{C₀}φ}, φ radial,
   log-concave, unit norm; ψ_δ = τ_{C₀+δe}φ. Then
   ℓ_off(δ) = 1 − [(φ⋆φ̌)(δe)]² is monotone nondecreasing (strict for
   strictly log-concave φ; Gaussian: 1 − e^{−δ²/(2w²)}). Proof: convolution
   preserves log-concavity (Prékopa 1973); radial log-concave ⇒ max at 0,
   nonincreasing along rays.
2. **Countermodel (FORMAL + NUMERICS).** Multi-well register
   A = span{φ_{C₀}, φ_{C₀+Le}}: ℓ_off(0) = ℓ_off(L) = 0, interior peak
   ≈ 1 − 2e^{−L²/(8w²)}. Receipt (w=0.35, L=2.0): peak 0.9662 at δ=1.0;
   monotone = FALSE. Physical: multi-detector array re-acquires at second
   head; the smoke-detector picture is the unimodal case.

## Test protocol (D5)

```text
Inputs:   C0, offset direction e, grid {δ_i} (≥ 40 pts, span ≥ 4w),
          REGISTER CLASS declaration (mandatory field):
            RC-1  rank-one radial log-concave (w)      — monotone REQUIRED
            RC-k  multi-well (k ≥ 2 heads, spacing L)  — monotone NOT required
Outputs:  ℓ_off(δ_i) table · monotone_strict boolean · peak (value, location)
Pass/fail:
  RC-1: monotone_strict = TRUE  → CC-BL-001a′ holds; FALSE → FALSIFIED
  RC-k: report peak; monotone FALSE is EXPECTED, not a failure
Receipts: script sha256 · interpreter version · deterministic (no RNG)
```

## Current receipts (kns_lb_probe.py, sha 09ef26d3…8211b011)

```text
RC-1 (w=0.35):        D5_unimodal_monotone = true   (41-pt grid, δ ∈ [0,2])
RC-2 (w=0.35, L=2.0): D5_twomode_monotone  = false · peak 0.9662 @ δ=1.0
```

**Consequences.** Every future CC-BL-001a citation must carry the register
class. Unscoped statements of the bridge lemma are non-canon. Falsifier for
the scoped lemma: any RC-1 register with non-monotone ℓ_off(δ).
