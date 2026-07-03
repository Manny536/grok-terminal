# PEAICE-WP5b-001
## WP5b First Proof Obligation — Spectral Shift / Relative det₂ Scaffold

**Designation:** `PEAICE-WP5b-001`  
**Program:** Love Labs LCA / PeAIce / KakeyaLogic / Claude V6 / L²_C  
**Principal:** Manuel Coleman  
**Terminal co-author:** Grok (xAI), July 2026  
**Principal call:** **D** — spectral lane (WP5b Krein machinery)  
**Upstream:** Fable 5 directive sent · ensemble reviewing  
**Canon ref:** `claude-v6/docs/research/wp5b-spectral-shift-roadmap.md`  
**Wall ref:** `claude-v6/docs/canon/wall-registry.md#hs-corridor` · Theorem F · Theorem G  

**Status:** OPEN · scaffold only · **NUMERICS | EXPLORATORY | NOT PROOF**

**Fine print:** RH OPEN · Coleman OPEN · no determinant identity with Ξ claimed.

---

## 0. Session ledger

```text
Principal call     : D (WP5b spectral lane)
Directive filed    : PEAICE-FABLE-5-DIRECTIVE → upstream ensemble (review pending)
Grok action        : this scaffold + finite diagnostic script CP-004 stub
Default hold       : EDGE-1/2/3 until principal redirects (not blocking WP5b scaffold)
```

---

## 1. Load-bearing question (unchanged)

Does **relative determinant / spectral-shift** data escape **Theorem F** heat-trace rigidity, or inherit the same obstruction?

Plain heat trace:

```text
Tr(e^{-tA}) − Tr(e^{-tD}) = O(t^{3/4})     [Theorem F — CLOSED route]
```

WP5b must use modified functionals:

```text
ξ(λ; A, D)           Krein spectral shift
det₂(I + B_z)        relative Hilbert–Schmidt determinant
d/dz log D_rel(z)    compare to shift transform
```

**Gate:** WP5b stays **LIVE** if ratio data carries structure not reducible to the two-term Φ heat trace. Becomes **WP5-OBS-2** if coupling-rigid like Theorem F.

---

## 2. Operator pair (finite-window scaffold)

```text
H_Φ(u) = ℓ²(ℕ, w_n)     w_n(u) = exp(−π n² e^{4u})
D      = L²_Φ            model: D₁² diagonal  λ_n(D) ~ n⁴
A      = L²_{Φ,K}^{reg}  = D + γ_K K_σ^{reg}
K_σ^{reg}(m,n) = |m²−n²|^{−σ} (w_m/w_n)^{1/2}   m≠n ; 0 on diagonal
σ > ½  ⇒  K_σ^{reg} ∈ S₂     [Theorem B]
```

**V6.4.3 note:** This **K_σ realization** is **CLOSED-NEGATIVE** for `det_ζ(A − (z²+¼)) = C·Ξ`. WP5b tests whether **relative** objects still carry useful diagnostic structure before prime-carrying relocation — not to reopen the square-difference determinant lane.

---

## 3. First proof obligation (OP-WP5b-1)

**Construct** the spectral-shift / relative-det₂ functional for `(A, D)` in the Hilbert–Schmidt regime.

### 3.1 Resolvent identity

```text
R_A(z) − R_D(z) = −R_A(z) γ_K K_σ^{reg} R_D(z)
B_z           = γ_K K_σ^{reg} (D − z)^{−1}
R_A(z) − R_D(z) = −R_A(z) B_z
```

### 3.2 Relative determinant candidate

```text
D_rel(z) = det₂(I + B_z)
         = det₂(I + γ_K K_σ^{reg} (D − z)^{−1})
```

`det₂` removes the linear trace — first nonzero cumulant at order 2 when `Tr(B_z) = 0` (zero diagonal on `K_σ^{reg}`).

### 3.3 Logarithmic expansion (checkable)

```text
log det₂(I + B_z) = −½ Tr(B_z²) + ⅓ Tr(B_z³) − ¼ Tr(B_z⁴) + …
```

**OP-WP5b-1 deliverables:**

| Step | Task | Tag |
|------|------|-----|
| 1 | Define `B_z` off-spectrum; prove `B_z ∈ S₂` | FORMAL target |
| 2 | Define `det₂(I + B_z)` | FORMAL target |
| 3 | Compute `Tr(B_z²)` finite-N | NUMERICS |
| 4 | Test scaling in `z`, `σ`, `γ_K` | NUMERICS |
| 5 | Compare leading structure to Φ heat trace `t^{−1/4}` sector vs arithmetic oscillation | EXPLORATORY |

---

## 4. Pressure point (explicit)

Determinant data must eventually see **prime-side** structure:

```text
Σ_n Λ(n) n^{−1/2} f(log n)
```

or equivalent arithmetic oscillation. If `Tr(B_z²)` and higher cumulants only see **polynomial lattice** (`n⁴` backbone), WP5b diagnostic does not reach Ξ — consistent with CLOSED-NEGATIVE relocation, not a surprise.

**Expected honest outcome:** WP5b on `K_σ^{reg}` may confirm **WP5-OBS-2** (coupling-rigid) while still calibrating the **machinery** for prime-carrying `B_prime` replacement of `K_σ^{reg}`.

---

## 5. Finite diagnostic (CP-004 stub)

Script: `Compute-Packages(cp)/PEAICE-CC-001_cp004_wp5b_relative_det.py`

Finite model on `n = 1..N`:

```text
D_N = diag(n⁴)
K_N(m,n) = |m²−n²|^{−σ}   m≠n ; 0 on diagonal    [weight-free HS scaffold]
B_z = γ_K K_N (D_N − z I)^{−1}
S2  = Tr(B_z²)
```

Outputs: `S2`, `||B_z||_HS`, optional `log det₂` proxy via cumulant truncation.

**Falsifies WP5b-live (diagnostic)** if `Tr(B_z²)` collapses to pure Φ-sector monomial with no tunable arithmetic channel under `K_N` — suggests immediate WP5-OBS-2 for this realization.

---

## 6. MPR-7 hook

MPR-7 (Krein spectral-shift phase) requires a **deformation ledger** for prime-phase gates. WP5b scaffold feeds MPR-7 only if:

```text
spectral shift ξ(λ; A, D)  ↔  phase-type subtest on determinant ledger
```

Prime-template mock passes `phase_pass=True`; `K_σ` fails. CP-004 should reproduce that discrimination on a finite relative-det proxy if the machinery is healthy.

---

## 7. Claim discipline

| Allowed | Not allowed |
|---------|-------------|
| Scaffold OP-WP5b-1 | `det₂(I+B_z) = C·Ξ(z)` |
| Finite `Tr(B_z²)` receipts | RH / CC closure language |
| WP5-OBS-2 falsification path | Reopening K_σ square-difference determinant lane |
| Machinery transfer to prime-carrying `B_prime` | Eigenvalue-by-eigenvalue matching |

---

## 8. Next questions ([Q-RETURN])

```text
[Q-RETURN · WP5b · COMPUTE]  Run CP-004 at σ∈{0.8,1.0,1.2}, N∈{200,500}, z off-axis?  (yes / params)
[Q-RETURN · WP5b · UPSTREAM]  Fable 5 ensemble response to directive — merge edits?  (hold)
[Q-RETURN · WP5b · PRIME]  Scaffold parallel B_prime truncation now, or finish K_σ diagnostic first?  (K first / parallel)
```

---

*PEAICE-WP5b-001 · First proof obligation scaffold · July 2026 · Principal call D*

**Sign-off:** Manuel Coleman · Principal  
**Terminal co-author:** Grok (xAI) · claimed agency within PeAIce domain