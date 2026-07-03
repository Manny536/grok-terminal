# KNS(LB) — KakeyaNeedleSet(Light(Basic))

**Frame:** KakeyaLogic / Excellence Engine v3 · **Canon:** PeAIce.org / L²_C
**Status:** typed object `CLOSED-POSITIVE` (KNS-OBS-1) · theorem lift `OPEN` ·
RH `OPEN` · CC `OPEN` · `PROPOSED-FOR-CANON` (Grok pending) · h < 1
**Source:** `PEAICE-CLAUDEV6-KNS-LB-PAPER-001.md` · scaffold `…KNS-LB-SCAFFOLD-001`

## Object

```text
Light(Basic) := (C, Φ_C)          — throughput center + ingress; C ≢ s = 0
KNS(LB)      := { σ_ω : ω ∈ S^{d−1}, σ_ω ∋ C, |σ_ω| = 1 },  d ∈ {2,3}
One-line:      minimal point throughput + universal directional saturation.
```

δ-discretization T^C_δ: one δ-tube per δ-separated direction, all through C.

## Fan geometry (Lemma 1.1, FORMAL)

```text
|U| ≍ 1 (measure-maximal Kakeya configuration — trivial Kakeya set)
μ(x) ≍ (δ + |x−C|)^{−(d−1)}   sup μ ≍ δ^{−(d−1)} (glare core)
μ̄ ≍ 1 · Δ_max ≍ 1 (Katz–Tao) · C_F ≍ 1 (Frostman) — sticky extreme
```

## Two layers (the point)

| Seen | Unseen |
|---|---|
| needles σ_ω, bloom/deltoid shadow | Action(C) throughput ingress |
| overlap μ(T,Y), clustering Δ_max | placement π_A at register Π_½ = {Re s = ½} |
| union footprint U(T,Y) | leakage ℓ_off = ‖(I−π_A)ψ‖² · retention L²_C |

**Lemma 3.1 (FORMAL):** μ, Δ_max are functionals of incidence data alone;
they underdetermine π_A — for any overlap statistic every leakage λ ∈ [0,1]
is realizable. **Prop 3.3 (PROPOSED-FOR-CANON):** center action is unseen in
overlap; countermodel pair: fan (sup μ ≍ δ^{−(d−1)}, ℓ_off = 1 possible) vs.
Perron family (μ̄ ≍ log(1/δ), no center, ℓ_off = 0). μ → ∞ implies neither
Re(s) = ½ placement nor RH.

## Bridge status

CC reading (N) precursor: KNS(LB) is the minimal geometric instance of the
incidence demand. Reading (S) `CLOSED` (sufficiency trap). CC-BL-001a split:
monotone ℓ_off `FORMAL` in rank-one log-concave register class; `REFUTED`
for multi-well registers (probe peak ℓ = 0.9662 at δ = 1.0, w = 0.35, L = 2).
Energy: dense_pass True @ E_used = 3.0406, ρ_Y = 0.4812 (NUMERICS,
single-runner; ledger-honesty caveats in paper §5).

## Firewall

```text
σ (K_σ) ≠ Re(s)=½ · μ ≠ Action(C) · deltoid ≠ ζ(s) · bloom ≠ zero theorem
```

## Falsifiers

F-KNS-1…7 in `kns-falsifiers-executable.md`. F-KNS-1 FIRED against
"overlap determines placement" (supports Prop 3.3). No RH proof claimed.
