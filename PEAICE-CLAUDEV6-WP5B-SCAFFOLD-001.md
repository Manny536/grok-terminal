# WP5b — Krein Spectral Shift: Proof-Obligation Scaffold

**Designation:** `PEAICE-CLAUDEV6-WP5B-SCAFFOLD-001` *(token pending principal sign-off — §12 Q-RETURN 2)*
**Program:** PeAIce Research Program · Love Labs LCA · KakeyaLogic · Claude V6 lane
**Status header:** RH `OPEN` · Coleman Conjecture `OPEN` · WP5b `ACTIVE` · no proof claimed · `h < 1`
**Canon anchors:** `claude-v6 @ 2954261` (`docs/research/wp5b-spectral-shift-roadmap.md`, `docs/canon/v6-theorems.md`, `docs/canon/wall-registry.md`) · `kakeyalogic @ a4e1cea` (`docs/prime-carrying-trace-architecture.md`, relocation target)
**Terminal:** Claude Fable 5 (Max effort) · cross-derivation requested: Grok (xAI)
**β-Protocol markers:** `FORMAL` / `PROPOSED` / `PROPOSED-FOR-CANON` / `KNOWN` / `NUMERICS` / `OPEN` / `CLOSED-NEGATIVE`

---

## 0. Question, and verdict preview

Roadmap question (verbatim): *Does relative determinant data escape Theorem F heat-trace rigidity, or does it inherit the same obstruction?*

Roadmap gate **WP5-OBS-2** (verbatim): *WP5b closes if the relative determinant is coupling-rigid in the same way as the heat trace, or if its asymptotics remain incompatible with the Ξ-side explicit formula.*

**Preview of verdict.** For the corridor **as stated** in the roadmap setup — `A = D + γ_K K_σ^{reg}` with `σ > 1/2`, hence a *bounded* self-adjoint coupling — the answer is **no escape**, and provably so at a level *stronger* than Theorem F: the Krein spectral shift function of the pair is uniformly bounded (Proposition H below), and every functional the roadmap names — heat trace, relative zeta, relative determinant, determinant ratios — is a transform of that one bounded function. The gate's first disjunct fires.

For the corridor **as intended** — Krein/relative-determinant machinery as the container for a Ξ-faithful operator — the frame survives intact in the widened *resolvent-comparison* category (unbounded modifications with trace-class resolvent difference), and the requirements it imposes land exactly on the prime-carrying relocation target. Section 8 converts this into a design specification.

Nothing in this document proves, approaches, or evidences RH. The deliverable is a wall-sharpening plus a transfer interface.

---

## 1. Imports from canon

| Object | Status in canon | Source |
|---|---|---|
| Theorem A — weighted symmetry, `K^{reg}(n,n) = 0` | FORMAL | `v6-theorems.md` |
| Theorem B — isometry `V`, transferred kernel `T_{mn} = \|m²−n²\|^{−σ}`, HS ⟺ `σ > 1/2` | FORMAL | `v6-theorems.md` |
| Theorem C — trace neutrality (zero weighted diagonal) | FORMAL | `v6-theorems.md` |
| Theorem D — exact Φ heat trace `Θ_Φ(t) = Γ(5/4)(ct)^{−1/4} − 1/2 + O(t^M)`; model eigenvalues `λ_n = c n⁴` | FORMAL | `v6-theorems.md` |
| Theorem E — first order vanishes; `Δ(t) = (γ²/2)‖K‖²_HS t² + o(t²)`; `κ₂` | FORMAL | `v6-theorems.md` |
| Theorem F — heat-trace rigidity `O(t^{3/4})` under bounded coupling | FORMAL | `v6-theorems.md` |
| L2-5 — eigenvalue route closed: `N_L(T) ~ T^{1/4}` vs `(T/2π)log(T/2π)` | FORMAL, closed | `wall-registry.md` |
| WP5-OBS-1 — bounded heat route closed (`t^{−1/2}log(1/t)` + prime sector unreachable) | FORMAL, closed | `wall-registry.md` |
| Theorem G / Corollary G.1 — singular-value law `s_n ~ c_σ n^{−σ}` (PROPOSED); `det₂(I − zK_σ) = CΞ` pincer (FORMAL closure) | PROPOSED / FORMAL | `v6-theorems.md` |
| HS-CORRIDOR — determinant lane closed for `K_σ`; relative compactness ⟹ `N(Λ) ~ Λ^{1/4}` preserved | FORMAL / CLOSED-NEGATIVE | `wall-registry.md` |
| LINDELÖF CEILING — bound-only lineage cannot close GAP-001 | KNOWN (background) | `wall-registry.md` |
| Relocation target — prime-carrying lengths `log p^k`, weights `Λ(p^k)p^{−k/2}` | OPEN (live frontier) | `kakeyalogic/docs/prime-carrying-trace-architecture.md` |

Convention throughout: work on the transferred side of Theorem B's isometry, so `D = diag(λ_n)`, `λ_n = c n⁴` in the index basis, and `K` denotes the transferred kernel `T` (zero diagonal). `V := γ_K K`, `A := D + V`, `c₀ := ‖V‖_op = |γ_K|·‖K‖_op ≤ |γ_K|·‖K‖_HS < ∞` for `σ > 1/2`.

---

## 2. Standing structural facts

**S1 (resolvent of D is trace class).** `FORMAL`. For `z ∉ spec(D)`,
```text
‖R_D(z)‖_{S₁} = Σ_n |λ_n − z|^{−1} ≲ Σ_n n^{−4} < ∞ ,   R_D(z) := (D − z)^{−1} ∈ S₁ .
```
This single fact reorganizes the whole corridor: the *free* resolvent already lives in the smallest ideal.

**S2 (coupling is bounded).** `FORMAL`. By Theorem B, `K ∈ S₂ ⊂ B(ℓ²)` for `σ > 1/2`; `A` is self-adjoint on `dom(D)` with discrete spectrum, and `R_A(z) ∈ S₁` for `z ∉ spec(A)` (second resolvent identity: `R_A = R_D − R_A V R_D`, ideal property).

**S3 (resolvent difference is trace class).** `FORMAL`.
```text
R_A(z) − R_D(z) = −R_A(z) V R_D(z) ∈ S₁      (bounded · bounded · S₁).
```
This is the roadmap's "study whether a trace-class resolvent difference exists" — answered affirmatively, unconditionally, for all `σ > 1/2` and all `γ_K`.

**S4 (roadmap step 2, upgraded).** `FORMAL`. `B_z := V R_D(z) ∈ S₁`, not merely `S₂`: bounded times trace class. The ordinary Fredholm determinant `det(I + B_z)` is defined; no `det₂` regularization is required.

**S5 (the roadmap's `det₂` object equals the classical perturbation determinant).** `FORMAL`. In the index basis, `Tr B_z = γ_K Σ_n K(n,n)(λ_n − z)^{−1} = 0` by the zero diagonal (Theorems A/C). Hence
```text
det₂(I + B_z) = det(I + B_z) · e^{−Tr B_z} = det(I + B_z) .
```
This also *explains* the roadmap's expansion `log det₂(I + B_z) = −½Tr(B_z²) + ⅓Tr(B_z³) − …`: the linear term that `det₂` removes was already zero. Trace neutrality (Theorem C) is the semigroup-side face of the same fact.

---

## 3. OB-1 — existence of the spectral shift function (roadmap first proof obligation)

Both spectra are discrete (S1/S2), so the Krein machinery collapses to counting. Define
```text
ξ(λ) := N_D(λ) − N_A(λ) ,    N_X(λ) := #{ j : x_j ≤ λ } ,
```
an integer-valued step function. Sign convention agrees with Krein's: for `V ≥ 0` rank-one, eigenvalues move up, so `ξ ≥ 0`.

**Lemma 3.1 (discrete Krein trace formula).** `FORMAL`. Let `d₁ ≤ d₂ ≤ …` and `a₁ ≤ a₂ ≤ …` be the sorted spectra of `D` and `A`, and let `f ∈ C¹(ℝ)` satisfy `Σ_j sup_{I_j} |f′| < ∞` over the displacement intervals `I_j = [min(d_j,a_j), max(d_j,a_j)]` (e.g. `f(λ) = e^{−tλ}`, `t > 0`; resolvent kernels; `λ ↦ (λ+μ)^{−s}` on shifted spectra). Then
```text
Tr( f(A) − f(D) ) = ∫_ℝ f′(λ) ξ(λ) dλ .
```
*Proof.* Weyl's inequality (min-max) gives `|a_j − d_j| ≤ c₀` for every `j` (`KNOWN`). Then `f(a_j) − f(d_j) = ∫_{d_j}^{a_j} f′(λ) dλ`, the sum over `j` converges absolutely by hypothesis, and Fubini gives
```text
Σ_j ( f(a_j) − f(d_j) ) = ∫ f′(λ) Σ_j [ 𝟙(d_j ≤ λ < a_j) − 𝟙(a_j ≤ λ < d_j) ] dλ = ∫ f′(λ) ( N_D(λ) − N_A(λ) ) dλ . ∎
```
General frame for reference: Krein 1953; resolvent-comparison invariance in Yafaev, Ch. 8 (`KNOWN`). Not needed here — discreteness delivers everything directly, with S3 as the structural license.

**OB-1 status: DISCHARGED** (`FORMAL`), with the strengthening S4 (`S₁`, not `S₂`) and the identification S5.

---

## 4. Proposition H (candidate) — the Weyl-window law

**Status:** `PROPOSED-FOR-CANON` — full proof supplied below; canon entry requires principal sign-off **and** independent ensemble re-derivation (Grok), per evaluator non-sovereignty. The terminal's own proof does not self-certify.

**Hypotheses.** `D = diag(λ_n)` with `λ_n = c n⁴` (any discrete ladder with gaps `→ ∞` suffices); `V = V*` bounded, `c₀ := ‖V‖_op`; `A = D + V`; `ξ = N_D − N_A`.

**Claims.**
```text
(i)   |a_j − d_j| ≤ c₀  for all j.                                        [Weyl; KNOWN]
(ii)  |ξ(λ)| ≤ W(λ; c₀) := #{ j : d_j ∈ (λ − c₀, λ + c₀] }  for all λ.
(iii) sup_λ |ξ(λ)| ≤ W_max(c₀) < ∞ ,  and  |ξ(λ)| ≤ 1  for  λ > Λ₀(c₀),
      with (for λ_n = c n⁴)  Λ₀(c₀) ≤ c · ( ⌈(c₀ / 2c)^{1/3}⌉ + 1 )⁴ + c₀ .
(iv)  supp ξ ⊂ ∪_j [ d_j − c₀ , d_j + c₀ ] ;   |supp ξ ∩ [0, Λ]| ≤ 2 c₀ · N_D(Λ + c₀) = O(Λ^{1/4}) .
```

*Proof.* (ii): the counting discrepancy at `λ` counts indices `j` for which exactly one of `d_j ≤ λ`, `a_j ≤ λ` holds. If `d_j ≤ λ < a_j` then by (i) `d_j > λ − c₀`; if `a_j ≤ λ < d_j` then `d_j < λ + c₀`. Either way `d_j ∈ (λ − c₀, λ + c₀]`. (iii): the ladder gaps `λ_{n+1} − λ_n ≈ 4cn³ → ∞`, so any interval of length `2c₀` eventually contains at most one ladder point; the stated `Λ₀` bounds where this begins, and `W_max` is finite because low-`λ` windows contain finitely many points. (iv): outside every displacement window, `N_D = N_A`. ∎

The proof is elementary. Its consequences below are not cosmetic: they close the corridor as stated.

---

## 5. Corollaries — every WP5b functional is a transform of one bounded ξ

**C1 (heat: Theorem F subsumed and localized).** `FORMAL` (given Lemma 3.1 + Prop H). With `f(λ) = e^{−tλ}`,
```text
S(t) := Tr(e^{−tA} − e^{−tD}) = −t ∫ e^{−tλ} ξ(λ) dλ ,
|S(t)| ≤ t · W_max · Σ_j ∫_{d_j − c₀}^{d_j + c₀} e^{−tλ} dλ ≤ 2 c₀ W_max · t e^{c₀ t} · Θ_Φ(t) = O(t^{3/4}) .
```
The exponent `3/4 = 1 − 1/4` is exposed as (thin support per rung) × (Weyl density `t^{−1/4}`, Theorem D). Theorem F is re-derived and *explained*. Theorem E's `t²` law is the refined statement inside the zero-diagonal class (first moment of the per-rung displacement vanishes with the diagonal).

**C2 (relative zeta = Mellin of ξ).** `FORMAL` (routine). Fix a common shift `μ > max(0, c₀ − d₁)` so both operators are strictly positive; `ξ` is shift-equivariant. Then
```text
ζ_rel(s) := Σ_j ( (a_j + μ)^{−s} − (d_j + μ)^{−s} ) = −s ∫_0^∞ ξ_μ(λ) λ^{−s−1} dλ ,
```
absolutely convergent for `Re s > −3/4` by Prop H (iv) (`∫ |ξ_μ| λ^{−Re s − 1} dλ ≲ c₀ Σ_j d_j^{−Re s − 1}`), so `ζ_rel` is analytic there and `det_rel := exp(−ζ_rel′(0))` is well-defined. The Mellin identity is the precise content of the canon line "L2-5 and WP5-OBS-1 are the same wall seen through Mellin."

**C3 (perturbation determinant = Stieltjes transform of ξ; growth cap).** `FORMAL`. For `z ∉ spec(A) ∪ spec(D)`,
```text
det(I + B_z) = ∏_j (a_j − z)/(d_j − z)      (absolutely convergent: Σ_j |a_j − d_j| · |d_j − z|^{−1} ≤ c₀ Σ_j |d_j − z|^{−1} < ∞),
log det(I + B_z) = ∫ ξ(λ) (λ − z)^{−1} dλ    (exact in the discrete case; branch fixed by z → −∞).
```
Growth cap: for real `x → −∞`, `|log det(I + B_x)| ≤ c₀ Σ_j (d_j + |x| − c₀)^{−1} → 0`. The perturbation determinant is the Cauchy transform of a *uniformly bounded, thin-support* density. Under the GAP-001 dictionary `λ = z² + 1/4`, such an object cannot represent order-1, genus-1 `Ξ` data: the required log-magnitude `~ |z| log |z|` on rays is unavailable. Note the complementarity with Corollary G.1: G.1 closes `det₂(I − zK_σ)` (spectral parameter multiplying the kernel) by the order/genus/density pincer; C3 closes `det(I + γK R_D(z))` (the pair determinant) by SSF boundedness. Different objects, different mechanisms, same verdict.

**C4 (counting with O(1) precision).** `FORMAL`. `N_A(Λ) = N_D(Λ) + O(1)`. This upgrades L2-5 and the HS-CORRIDOR relative-compactness clause from *rate preservation* (`N ~ Λ^{1/4}`) to *bounded discrepancy*. Riemann–von Mangoldt relative counting `(√Λ/2π) log √Λ` requires `ξ` unbounded — excluded outright for bounded couplings.

**C5 (roadmap item 5 answered: is `Tr(B_z²)` density-only or arithmetic?).** Resolution: **arithmetic-present-but-capped.**
```text
Tr(B_z²) = γ² Σ_{m≠n} |m² − n²|^{−2σ} (λ_m − z)^{−1} (λ_n − z)^{−1} .
```
The constraint surface `m² − n² = k` carries divisor-class structure (`k = (m−n)(m+n)`, same-parity factorizations), so the Taylor data of the determinant genuinely contains arithmetic — consistent with the prime-carrying doc's Jacobi-theta caution: entrywise prime-freeness proves nothing about invariants. But by C3 the analytic object all coefficients assemble into is a bounded-density Cauchy transform. Whatever divisor arithmetic enters term-by-term, its integrated effect is capped strictly below the `Ξ` threshold. "Density-only vs arithmetic" was the wrong dichotomy; the right statement is: arithmetic in, boundedness out.

---

## 6. Gate verdict — WP5-OBS-2

The gate's first disjunct — *the relative determinant is coupling-rigid in the same way as the heat trace* — is established by Prop H + C1–C4 for **every** bounded self-adjoint coupling. This covers `γ_K K_σ^{reg}` for all `σ > 1/2` and all `γ_K`, and also every bounded re-weighting or bounded replacement of the square-difference kernel: no bounded modification of the coupling escapes.

**Proposed ledger entry** (`PROPOSED-FOR-CANON`, pending §12 gates):
```text
WP5-OBS-2 — bounded-coupling relative-determinant route: CLOSED-NEGATIVE.
Mechanism: Krein SSF of the pair is uniformly bounded with thin support
(Weyl-window law); heat trace, relative zeta, and perturbation determinant
are respectively the Laplace, Mellin, and Cauchy transforms of that one
function, hence inherit the cap. Scope qualifier (load-bearing): the
hypothesis is OPERATOR-BOUNDEDNESS of the coupling. Nothing is asserted
about unbounded/relative modifications or a changed free operator.
```

**Wall unification.** L2-5 (counting rate), WP5-OBS-1 (heat singularity), the HS-CORRIDOR full-operator clause (Weyl-class invariance), and this verdict are one wall — the Weyl stability of the `n⁴` ladder — now expressed at its sharpest point (pointwise bounded `ξ`), from which the other three follow as transforms. The canon conjecture that L2-5 ≡ WP5-OBS-1 "through Mellin" is hereby proved, and extended to the Cauchy/determinant face.

---

## 7. What stays live — scope limits (read carefully; the qualifier is load-bearing)

**L1 — unbounded / relative modifications.** Prop H's hypothesis is operator-boundedness. The Krein frame itself survives whenever `R_A − R_D ∈ S₁` — a far weaker condition, automatically friendly here because `R_D ∈ S₁` (S1) absorbs a great deal. In that widened resolvent-comparison category, `ξ` may be unbounded, Lemma 3.1's general analogues hold (Yafaev Ch. 8), and nothing in this document obstructs a Ξ-faithful `ξ`. **This is the live continuation of WP5b.** WP5a (`σ ≤ 1/2`, kernel leaves HS/boundedness) is untouched — consistent with its held status.

**L2 — non-spectral functionals.** Everything above factors through the eigenvalue lists. Weighted and flow traces (`Tr_{w_u}`-type, `u`-dependent) use eigenvector data and do **not** factor through `ξ`. Prop H says nothing about them. That is precisely WP5c's door, which explains post hoc why WP5c is an independent corridor.

**L3 — different free operator.** Replacing `D` itself — the prime-carrying ladder with lengths `log p^k` and weights `Λ(p^k) p^{−k/2}` — changes the ladder, and nothing here constrains that move. This is the relocation target, and §8 states what the Krein frame demands of it.

---

## 8. ξ-design specification — transfer interface to the prime-carrying route

**Status:** `OPEN` (this is the relocated GAP-001, restated as requirements on one function).

For any future pair `(Â, D̂)` intended to realize the BK-HP-CC target under the dictionary `λ = z² + 1/4`:

**R1 (counting; necessary condition, `FORMAL` given Prop H).** With `T = √(λ − 1/4)`,
```text
N_Â(λ) = (T/2π) log(T/2πe) + 7/8 + S(T) + O(1/T) ,
```
so `ξ = N_D̂ − N_Â` is unbounded at scale `√λ log λ`. By Prop H, `Â − D̂` **cannot** be operator-bounded relative to a polynomial ladder: the modification must be unbounded, or the free operator itself must change. The relocation is therefore not a preference — it is forced.

**R2 (oscillation).** The fluctuation sector of `ξ` must reproduce `S(T) = π^{−1} arg ζ(1/2 + iT)`; equivalently, the Laplace side `𝓛[ξ](t)` must contain the `t^{−1/2} log(1/t)` singularity **and** the prime sector `Σ_n Λ(n) n^{−1/2} f(log n)` (WP5-OBS-1 / roadmap pressure point). What were previously requirements on three separate functionals are now requirements on one function.

**R3 (admissibility).** Retain `R_Â − R_D̂ ∈ S₁`, so that trace formula, relative zeta, and perturbation determinant remain defined after boundedness is dropped. The Krein frame is the correct *container* for the prime-carrying construction, even though it just closed the bounded lane.

**Sanity gate (first calculation for the prime-carrying lane; `OPEN`).** Verify that the canonical prime-carrying model's `ξ` satisfies R1/R2 *formally*. This is a restatement of the explicit formula and should be run as a consistency check — passing it is not progress toward RH and must not be ledgered as such.

---

## 9. Numerics receipt — `NUMERICS | EXPLORATORY | NOT PROOF`

Probe `xi_probe.py` (this session's sandbox): `N = 1200`, `σ = 0.60`, `λ_n = n⁴` (`c = 1`), `T` per Theorem B; dense `eigvalsh`; `ξ` computed exactly by merged-spectrum sweep. `‖T‖_op = 1.9319`.

| `γ` | `c₀ = γ‖T‖` | `sup|ξ|` | window bound `W` | `sup|ξ| ≤ W` | last `|ξ| ≥ 2` at `λ` | predicted `Λ₀` | `max|a_j − d_j|` | Weyl `≤ c₀` |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.93 | 1 | 1 | ✓ | — | ~1 | 0.019 | ✓ |
| 40 | 77.3 | 1 | 3 | ✓ | — | ~256 | 14.5 | ✓ |
| 400 | 772.7 | 2 | 6 | ✓ | −54.7 | ~4096 | 202.3 | ✓ |

All runs satisfy the window law and the Weyl displacement bound; `|ξ| ≤ 1` holds well before the conservative `Λ₀` prediction. Single runner (this terminal, authored-and-run); per IDB discipline this is a determinism receipt, not verification — second-runner reproduction required for VERIFIED status. `cp_verify`-style stamp attachable on request.

---

## 10. Failure modes and falsifiers

**F1.** Error in Lemma 3.1 / Prop H proofs. Mitigation: ensemble re-derivation gate (§12) before any canon write.
**F2.** Canon revision of the eigenvalue law (`λ_n ≠ c n⁴`). The chain survives for any ladder with `Σ λ_n^{−1} < ∞` and gaps `→ ∞`; only constants and `Λ₀` change.
**F3.** Claim leakage. If any downstream document cites this as "determinant route closed" **without** the bounded-coupling qualifier, that is a misstatement. The qualifier is load-bearing; L1–L3 are part of the result.
**F4.** Numerical `sup|ξ_N|` growth with `N` at fixed `(γ, σ)` would indicate model misconfiguration (truncation-scheme mismatch), not a counterexample — the lemma's proof is unconditional. Investigate the model, not the lemma.

---

## 11. Citation ledger — `KNOWN` anchors

- M. G. Krein (1953), *Mat. Sbornik* — spectral shift function, trace formula, perturbation determinant.
- I. M. Lifshitz (1952) — physical origin of the SSF.
- M. Sh. Birman, M. G. Krein (1962), *Dokl. Akad. Nauk SSSR* — SSF and scattering; `det S = e^{−2πiξ}`.
- L. S. Koplienko (1984) — second-order SSF `η` and the `det₂` frame. (Context only: unnecessary here because `R_D ∈ S₁`, per S4/S5.)
- D. Potapov, A. Skripka, F. Sukochev (2013), *Invent. Math.* 193 — higher-order spectral shift functions (Koplienko conjecture resolved).
- D. R. Yafaev, *Mathematical Scattering Theory: General Theory*, AMS (1992), Ch. 8 — resolvent-comparison Krein theory.
- B. Simon, *Trace Ideals and Their Applications*, 2nd ed., AMS (2005) — `det`/`det₂`, SSF.
- Already in canon: Birman–Solomyak (Theorem G route); Guth–Maynard arXiv:2405.20552 (Lindelöf ceiling).

---

## 12. Q-RETURN block

```text
[Q-RETURN · WP5B-1]
Blocker   : Prop H + WP5-OBS-2 verdict are new formal claims by this terminal.
Options   : (a) promote to canon (v6-theorems as Theorem H; wall-registry entry
            WP5-OBS-2) after Grok cross-derivation · (b) hold as scaffold-local ·
            (c) revise.
Default   : HOLD — no canon write without sign-off + independent re-derivation.
Referent  : principal call + Grok pass.

[Q-RETURN · WP5B-2]
Blocker   : designation token PEAICE-CLAUDEV6-WP5B-SCAFFOLD-001 is new.
Options   : approve / rename / reject.
Default   : HOLD (governance: no new canon tokens without referent).
Referent  : one line.

[Q-RETURN · WP5B-3]
Blocker   : next Max-effort spend fork after this scaffold.
Options   : (a) §8 sanity gate — prime-carrying model's ξ vs R1/R2 (explicit-
            formula consistency check) · (b) WP5c u-flow — the one door ξ does
            not close (L2) · (c) CP-004 — full ξ probe with cp_verify stamp,
            second-runner protocol.
Default   : (a) if silent.
Referent  : a / b / c / redirect.
```

---

**Sign-off:** authored by Claude Fable 5 terminal under principal directive `PEAICE-FABLE-5-DIRECTIVE`, option D. Authored-and-run, single-runner (§9). **Not independently verified.** RH `OPEN` · Coleman Conjecture `OPEN` · no proof claimed.
