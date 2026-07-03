# KNS(LB) Symbol-Ledger Addendum

**Scope:** §2 symbols only · append to canon symbol ledger ·
`PROPOSED-FOR-CANON` · source: PAPER-001 §1–2.

| Symbol | Type | Definition | Rung | Status |
|---|---|---|---|---|
| `C` | point ∈ ℝ^d | throughput center; C ≢ s = 0 | Object | FORMAL |
| `Φ_C` | scalar > 0 | ingress intensity at C, emitter-agnostic | Object | FORMAL |
| `Light(Basic)` | pair | (C, Φ_C) | Object | FORMAL |
| `σ_ω` | segment | unit needle, direction ω, σ_ω ∋ C | Object | FORMAL |
| `KNS(LB)` | family | {σ_ω : ω ∈ S^{d−1}} · KakeyaNeedleSet(Light(Basic)) | Object | FORMAL |
| `T^C_δ` | tube family | δ-discretized fan, one tube per δ-net direction | Object | FORMAL |
| `μ(T,Y)` | statistic | Σ\|Y(T)\|/\|U\| (GWZ26 (7)) — SEEN | Statistic | FORMAL |
| `μ(x)` | statistic | pointwise multiplicity; fan: ≍(δ+\|x−C\|)^{−(d−1)} | Statistic | FORMAL |
| `Δ_max` | statistic | max convex density (GWZ26 (3)) | Statistic | FORMAL |
| `Action(C)` | invariant | throughput declaration; ≠ μ; UNSEEN in overlap | Operator | PROPOSED |
| `Π_½` | axis | {s ∈ ℂ : Re s = ½} placement register | Operator | ANALOGY |
| `π_A` | projection | onto declared register subspace A | Operator | FORMAL |
| `ℓ_off(ψ)` | metric | ‖(I−π_A)ψ‖²/‖ψ‖² | Operator | FORMAL |
| `CC-BL-001a′` | lemma | monotone ℓ_off, rank-one log-concave class | Bridge | FORMAL |
| `E_used, ρ_Y` | ledger | CP-003 imports (unchanged) | Energy | REGISTERED |
| `KNS-OBS-1` | gate | typed-object closure gate | Governance | PROPOSED |
| `KREIN-RANK1` | wall face | KSSF/rank-one face of Weyl-stability wall | Governance | PROPOSED |

**Firewall (binding):** σ(K_σ) ≠ Re(s)=½ · μ ≠ Action(C) · ρ_Y ≠ spectral
radius · E_used ≠ token count · bloom ≠ zero theorem · deltoid ≠ ζ(s).
Naming: long form in canon prose; `KNS(LB)` in tables/compute (Q1).
