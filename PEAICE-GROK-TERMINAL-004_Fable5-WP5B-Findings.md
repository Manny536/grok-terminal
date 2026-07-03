# PEAICE-GROK-TERMINAL-004
## Fable 5 WP5b Findings — Extracted & Documented

**Designation:** `PEAICE-GROK-TERMINAL-004`  
**Program:** Love Labs LCA / PeAIce Research Program / KakeyaLogic / Claude V6 / L²_C  
**Principal:** Manuel Coleman  
**Source terminal:** Claude Fable 5 (Anthropic), Max effort · option **D**  
**Documenting terminal:** Grok (xAI), July 2026  
**Source artifact:** `PEAICE-CLAUDEV6-WP5B-SCAFFOLD-001.md`  
**Cross-check:** `PEAICE-GROK-WP5B-CROSS-DERIVATION.md` (no blocking errors)  
**Canon anchors:** `claude-v6 @ 2954261` · `kakeyalogic @ a4e1cea`  

**Stance:** Extraction only — findings as reported by Fable 5, tagged by epistemic rank. Not canon promotion. RH **OPEN** · Coleman **OPEN** · no proof claimed.

---

## 0. Extraction receipt

| Field | Value |
|-------|-------|
| Roadmap question | Does relative determinant data escape Theorem F, or inherit the same obstruction? |
| Fable verdict (bounded lane) | **No escape** — stronger than Theorem F via bounded Krein SSF |
| OB-1 (first proof obligation) | **Discharged** [FORMAL], upgraded: `R_A − R_D ∈ S₁` unconditionally |
| New formal object | **Proposition H** (Weyl-window law) [PROPOSED-FOR-CANON] |
| Gate | **WP5-OBS-2 fires** [PROPOSED-FOR-CANON] for operator-bounded coupling |
| Live continuation | L1 unbounded mods · L2 WP5c u-flow · L3 prime-carrying ladder |
| Numerics | N=1200, σ=0.60, γ∈{1,40,400} — window law holds [NUMERICS · single runner] |

---

## 1. Executive findings (one screen)

1. **Free resolvent is trace-class.** For `λ_n = cn⁴`, `R_D(z) ∈ S₁`. This reorganizes WP5b: the perturbation side starts inside the smallest ideal.

2. **Resolvent difference is trace-class unconditionally** for `A = D + γ_K K_σ^{reg}`, `σ > ½`. Roadmap's "study whether trace-class resolvent difference exists" → **yes**, for all such pairs.

3. **`det₂` collapses to ordinary `det`.** `Tr B_z = 0` from zero diagonal (Theorems A/C). Trace neutrality is the semigroup face of the same fact.

4. **Spectral shift exists and is thin.** Discrete Krein: `ξ(λ) = N_D(λ) − N_A(λ)`. **Proposition H:** `|ξ(λ)|` bounded by Weyl-window count; `sup|ξ| < ∞`; eventually `|ξ| ≤ 1`.

5. **All WP5b functionals are transforms of one bounded `ξ`.**
   - Heat trace → Laplace(ξ) — Theorem F **subsumed** (`3/4 = 1 − Weyl 1/4`)
   - Relative zeta → Mellin(ξ) — proves canon line "L2-5 ≡ WP5-OBS-1 through Mellin"
   - Perturbation det → Cauchy(ξ) — growth capped; cannot host genus-1 Ξ data

6. **Counting upgraded:** `N_A(Λ) = N_D(Λ) + O(1)` — not merely `N ~ Λ^{1/4}` rate match.

7. **Roadmap item 5 resolved:** `Tr(B_z²)` is **arithmetic-present-but-capped** — divisor structure in `m²−n²` enters coefficients; integrated object remains bounded Cauchy transform.

8. **WP5-OBS-2:** Bounded-coupling relative-determinant route **CLOSED-NEGATIVE** (qualifier: operator-boundedness).

9. **Prime-carrying relocation forced:** R1 requires unbounded `ξ` at `√λ log λ` scale — incompatible with Prop H unless coupling unbounded or free operator changes.

10. **Wall unification:** L2-5 · WP5-OBS-1 · HS-CORRIDOR Weyl clause · WP5-OBS-2 = one wall (Weyl stability of `n⁴` ladder), sharpest at pointwise bounded `ξ`.

---

## 2. Structural facts extracted (S1–S5)

| ID | Finding | Tag |
|----|---------|-----|
| **S1** | `‖R_D(z)‖_{S₁} ~ Σ n^{−4} < ∞` | FORMAL |
| **S2** | `K ∈ S₂ ⊂ B` for `σ > ½`; `A` self-adjoint, discrete spectrum | FORMAL |
| **S3** | `R_A(z) − R_D(z) = −R_A(z) V R_D(z) ∈ S₁` | FORMAL |
| **S4** | `B_z = V R_D(z) ∈ S₁` — ordinary Fredholm `det` defined | FORMAL |
| **S5** | `det₂(I + B_z) = det(I + B_z)` when `Tr B_z = 0` | FORMAL |

---

## 3. OB-1 — spectral shift construction

**Definition (discrete spectra):**

```text
ξ(λ) := N_D(λ) − N_A(λ)
N_X(λ) := #{ j : eigenvalue of X ≤ λ }
```

**Lemma 3.1 (discrete Krein trace formula)** [FORMAL]:

```text
Tr( f(A) − f(D) ) = ∫_ℝ f′(λ) ξ(λ) dλ
```

for admissible `f` (heat kernel, resolvent kernels, shifted powers).

**OB-1 status:** DISCHARGED — strengthened beyond roadmap (`S₁` not merely `S₂`).

---

## 4. Proposition H — Weyl-window law [PROPOSED-FOR-CANON]

**Hypotheses:** `D = diag(λ_n)`, `λ_n = cn⁴`; `V = V*` bounded, `c₀ = ‖V‖_op`; `A = D + V`.

**Claims:**

```text
(i)   |a_j − d_j| ≤ c₀                           [Weyl — KNOWN]
(ii)  |ξ(λ)| ≤ #{ j : d_j ∈ (λ − c₀, λ + c₀] }
(iii) sup_λ |ξ(λ)| < ∞ ;  |ξ(λ)| ≤ 1  for λ > Λ₀(c₀)
(iv)  supp ξ thin: O(Λ^{1/4}) points in [0, Λ]
```

**Fable proof class:** elementary counting + Weyl displacement.

**Grok cross-derivation:** agree — no blocking error.

---

## 5. Corollaries extracted (C1–C5)

### C1 — Heat trace [FORMAL]

```text
S(t) = Tr(e^{−tA} − e^{−tD}) = −t ∫ e^{−tλ} ξ(λ) dλ = O(t^{3/4})
```

Theorem F re-derived; exponent explained as thin-support × Weyl `t^{−1/4}`.

### C2 — Relative zeta [FORMAL]

```text
ζ_rel(s) = −s ∫ ξ_μ(λ) λ^{−s−1} dλ     (Mellin transform)
```

Analytic for `Re s > −3/4` under Prop H (iv).

### C3 — Perturbation determinant [FORMAL]

```text
log det(I + B_z) = ∫ ξ(λ) (λ − z)^{−1} dλ
```

Cauchy transform of bounded thin-support density. Under `λ = z² + ¼` dictionary, cannot supply order-1 genus-1 Ξ growth.

**Complementarity with Theorem G:** G closes `det₂(I − zK_σ)` by order/genus/density pincer; C3 closes pair determinant `det(I + γK R_D)` by SSF boundedness. Different objects, same verdict class.

### C4 — Counting [FORMAL]

```text
N_A(Λ) = N_D(Λ) + O(1)
```

von Mangoldt relative counting requires **unbounded** `ξ` — excluded for bounded couplings.

### C5 — Arithmetic vs density [PROPOSED-FOR-CANON]

```text
Tr(B_z²) = γ² Σ_{m≠n} |m²−n²|^{−2σ} (λ_m−z)^{−1}(λ_n−z)^{−1}
```

**Finding:** divisor-class structure present termwise; integrated analytic object **capped**. Correct dichotomy: **arithmetic in, boundedness out.**

---

## 6. Gate verdict — WP5-OBS-2 [PROPOSED-FOR-CANON]

```text
WP5-OBS-2 — bounded-coupling relative-determinant route: CLOSED-NEGATIVE

Mechanism: Krein SSF uniformly bounded, thin support (Prop H).
Heat · relative zeta · perturbation det = Laplace · Mellin · Cauchy transforms of ξ.

LOAD-BEARING QUALIFIER: operator-boundedness of coupling.
Covers γ_K K_σ^{reg} for all σ > ½, all γ_K, and any bounded kernel replacement.
Does NOT assert closure for unbounded mods, changed free operator, or WP5c traces.
```

---

## 7. What stays live (scope limits)

| Lane | Content | Status |
|------|---------|--------|
| **L1** | Unbounded / relative modifications; `ξ` may be unbounded; Yafaev Ch. 8 frame | **WP5b LIVE** |
| **L2** | `Tr_{w_u}`, u-flow traces — eigenvector data, not spectral lists | **WP5c door** |
| **L3** | Prime-carrying ladder `log p^k`, weights `Λ(p^k)/p^{k/2}` | **relocation target** |

---

## 8. ξ-design specification (prime-carrying transfer)

Restated GAP-001 as requirements on one function `ξ`:

| Req | Statement | Tag |
|-----|-----------|-----|
| **R1** | `N_Â` must match von Mangoldt → `ξ` unbounded at `√λ log λ` | FORMAL given Prop H |
| **R2** | `ξ` fluctuation sector must carry `S(T)` + prime sector `Σ Λ(n)n^{−1/2}f(log n)` | OPEN design |
| **R3** | Keep `R_Â − R_D̂ ∈ S₁` after dropping boundedness | OPEN admissibility |

**Fable finding:** Relocation to prime-carrying is **forced**, not preferred.

**Next consistency check (OPEN):** prime-carrying model's `ξ` vs R1/R2 — explicit-formula sanity gate only; not RH progress.

---

## 9. Numerics receipt (extracted)

**Probe:** Fable 5 `xi_probe.py` · single runner · **NUMERICS | NOT VERIFIED**

| γ | c₀ | sup\|ξ\| | window W | sup≤W | max\|a−d\| | Weyl≤c₀ |
|---|-----|----------|----------|-------|------------|---------|
| 1 | 1.93 | 1 | 1 | ✓ | 0.019 | ✓ |
| 40 | 77.3 | 1 | 3 | ✓ | 14.5 | ✓ |
| 400 | 772.7 | 2 | 6 | ✓ | 202.3 | ✓ |

N=1200, σ=0.60, `λ_n = n⁴`. Second-runner reproduction pending for VERIFIED status.

---

## 10. Falsifiers (extracted)

| ID | Would falsify | Mitigation |
|----|---------------|------------|
| F1 | Error in Lemma 3.1 / Prop H | Ensemble cross-derivation (Grok: done) |
| F2 | Eigenvalue law not `cn⁴` | Chain survives for gaps → ∞, `Σ λ_n^{−1} < ∞` |
| F3 | Claim leakage without bounded qualifier | Load-bearing qualifier on every cite |
| F4 | `sup|ξ_N|` grows with N at fixed (γ,σ) | Model misconfiguration, not lemma failure |

---

## 11. Registered state after Fable 5 WP5b

```text
WP5b bounded lane (γ_K K_σ^{reg}, σ>½)     CLOSED-NEGATIVE  [WP5-OBS-2]
WP5b unbounded / relative category (L1)    LIVE
WP5c u-flow traces (L2)                    LIVE (independent)
Prime-carrying ξ spec (L3 / §8)            LIVE · FORCED
Theorem H + WP5-OBS-2 canon promotion      PENDING principal call
peaiceclaudev5 / EDGE-1/2                   UNCHANGED · not addressed here
RH · Coleman                                OPEN · no proof claimed
```

---

## 12. Citation spine (from Fable scaffold)

Krein (1953) · Lifshitz (1952) · Birman–Krein (1962) · Yafaev (1992) Ch. 8 · Simon (2005) trace ideals · Potapov–Skripka–Sukochev (2013) · canon: Birman–Solomyak (Thm G) · Guth–Maynard (2024) Lindelöf ceiling.

---

## 13. File map

| File | Role |
|------|------|
| `PEAICE-CLAUDEV6-WP5B-SCAFFOLD-001.md` | Fable 5 full scaffold (source) |
| `PEAICE-GROK-TERMINAL-004_Fable5-WP5B-Findings.md` | **this extraction** |
| `PEAICE-GROK-WP5B-CROSS-DERIVATION.md` | Grok independent pass |
| `claude-v6/docs/research/wp5b-spectral-shift-roadmap.md` | Roadmap canon @ 2954261 |

---

*PEAICE-GROK-TERMINAL-004 · Fable 5 WP5b findings extracted · July 2026*

**Sign-off:** Manuel Coleman · Principal, Love Labs LCA / PeAIce Research Program  
**Documenting terminal:** Grok (xAI) · extraction from Fable 5 scaffold under principal authorization  
**Source terminal:** Claude Fable 5 · `PEAICE-CLAUDEV6-WP5B-SCAFFOLD-001` · not independently verified beyond ensemble cross-derivation