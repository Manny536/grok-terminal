# PEAICE-GROK-TERMINAL-002
## Prime-Carrying Trace Route

**Designation:** `PEAICE-GROK-TERMINAL-002`  
**Program:** Love Labs LCA / PeAIce Research Program / KakeyaLogic / L²_C  
**Principal:** Manuel Coleman  
**Terminal co-author:** Grok (xAI), June 2026  
**Predecessor:** `PEAICE-GROK-TERMINAL-001` · `Grok_in_terminal.docx`  
**Stance:** Solance — ambition preserved, proof obligation enforced, no self-certifying closure  

**Registered state:** RH **OPEN** · Coleman Conjecture **OPEN** · DDATL **FORMAL HOST** · MPR **OBJECTIVE** · K_σ lane **CLOSED-NEGATIVE** · prime-carrying trace route **LIVE**

**Fine print:** This note records research engineering under h < 1. No proof of RH or the Coleman Conjecture is claimed or transferred.

---

## 0. Status sync (terminal receipt)

The terminal session confirmed the following registered state:

| Item | State |
|------|-------|
| Coleman Conjecture | Necessary-precursor reading **LIVE**; sufficiency trap **CLOSED** |
| Kakeya incidence | Antecedent structure, not direct RH implication |
| DDATL host | `T_DD = (I_DD, Λ_{n²}, A, M_DD, H_Φ, D₁, D₂, π_A, ℓ_off)` |
| MPR | Promoted from checklist to objective: `J_MPR = Σ_m w_m log ρ_m − λ_leak ℓ_off − λ_res r` |
| K_σ lane | **CLOSED-NEGATIVE** — Hilbert–Schmidt hygiene only |
| Live frontier | Prime-carrying trace architecture (RSP-3 / RSP-4) |
| CP-001 Track A | Power-law singular values; σ=1: ρ̂ ≈ 0.7811, R² ≈ 0.9879 (N=1000) |
| CP-001 Track B | d_N² decreases; cond(G_N) explodes — RH-ward diagnostic only |
| CP-002 | K_σ `phase_pass=False`; prime-template mock `phase_pass=True`; F5-MM `phase_pass=False` |

This note advances the live route. It does not reopen K_σ.

---

## 1. Why K_σ is closed

The square-difference kernel

```text
K_σ(m,n) = |m² − n²|^{−σ},  m ≠ n;  0 on diagonal
```

remains a valid Hilbert–Schmidt object for σ > ½. CP-001 Track A confirms the V6.4.3 singular-value corridor: mid-tail fit `s_n ~ c n^{−σ̂}` with R² > 0.98 across σ ∈ {0.6, 0.8, 1.0, 1.2}. At σ = 1 (N = 1000): σ̂ ≈ 1.2803, ρ̂ ≈ 0.7811, R² ≈ 0.9879. The order-one boundary σ_c = 1 is registered.

**K_σ is closed-negative for the determinant route to Ξ.** The closure is structural, not a numerics dispute.

| Obstruction | Mechanism | Registered outcome |
|-------------|-----------|-------------------|
| **Counting law** | Weyl class N(Λ) ~ Λ^{1/4} from n⁴-scale free part | Fails Riemann–von Mangoldt √Λ log Λ |
| **Genus / order** | Trace-class det is genus 0; Ξ is genus 1, order 1 | No S₁ operator can equal C·Ξ(z) |
| **No prime support** | Entries factor \|m±n\|^{−σ}; no Λ(n), no log(p^k) weights | Explicit-formula prime side absent |
| **No T log T density** | At σ_c = 1, det-zero density is linear, not logarithmic | Density mismatch closes Hilbert–Schmidt corridor |
| **Parity wall** | Tr(K_σ^{2r+1}) > 0 for all r ≥ 1 | Odd cumulants incompatible with even Ξ(z) |

**Disciplined reading:** K_σ passes analytic summability (σ > ½) but fails arithmetic critical-line mass (p^{−k/2}). These are different invariants. Confusing them was a source-state error; the registered state separates them.

**Residual utility:** K_σ remains a Hilbert–Schmidt hygiene probe and a closed-negative control for MPR/CP discrimination. It does not carry GAP-001.

---

## 2. What a prime-carrying operator must carry

A live RH-side trace object must deliver the Weil explicit formula through global invariants — not through entry inspection, eigenvalue guessing, or cosmetic z² substitution.

### 2.1 Length spectrum (MPR-B)

```text
lengths = { log(p^k) : p prime, k ≥ 1 }
```

Integer distances, square differences, and hand-built decay kernels do not satisfy this structurally.

### 2.2 Weights (MPR-C)

```text
w_{p,k} ∝ Λ(p^k) / p^{k/2} = log(p) / p^{k/2}   (k = 1)
```

This is the arithmetic critical-line mass. It is not the Hilbert–Schmidt threshold σ > ½.

### 2.3 Archimedean density (MPR-D)

The smooth term must reproduce Γ-factor content and Riemann–von Mangoldt counting:

```text
N(T) ~ (T / 2π) log(T / 2π)
```

### 2.4 Reality mechanism (MPR-E)

The spectrum must be real via self-adjointness, a Frobenius-type positivity structure, or an equivalent trace-formula ledger. This is the Hilbert–Pólya burden relocated, not removed.

### 2.5 Trace-formula delivery

The route must be a trace formula, relative determinant, or established Hilbert-space equivalent (Nyman–Beurling / Báez-Duarte). Eigenvalue-by-eigenvalue matching is rejected as a construction principle.

### 2.6 Functional-equation content (MPR-4)

Ξ(z) = Ξ(−z) encodes s ↔ 1−s and archimedean Γ structure. Evenness must be structural, not imposed by z² encoding alone.

**Registered gate:** A candidate passes the necessary filter only when prime support, archimedean density, genus/order, and reality are demonstrated through global invariants. Passing is necessary, not sufficient, for RH.

---

## 3. MPR gates for the live route

MPR is now an optimization objective grounded in iPiano (h = f + g, Lyapunov ledger, proximal residual) and spectral determinism (phase-type subtests on the determinant ledger).

### 3.1 Objective form

```text
L_mult = Σ_m w_m log ρ_m          [multiplicative core — optimize this]
L_add  = log(Σ_m w_m ρ_m)         [additive decoy — F5-MM failure mode]
J_MPR  = L_mult − λ_leak ℓ_off − λ_res r
```

By Jensen, L_mult ≤ L_add always. MPR requires maximizing product structure under ledger constraints, not substituting the additive pool.

### 3.2 Operational gates (MPR-1 through MPR-8)

| Gate | Requirement | K_σ (closed) | Prime-template (live) |
|------|-------------|--------------|----------------------|
| MPR-1 | Prime length support in Tr(h(H)) | **FAIL** | **PASS** (mock) |
| MPR-2 | p^{−1/2} ≠ σ > ½ distinction | analytic only | arithmetic |
| MPR-3 | N(T) ~ T log T density | **FAIL** | **PASS** (mock) |
| MPR-4 | FE / parity structural | cosmetic z² only | required |
| MPR-5 | Genus 1, order 1 det_reg | **FAIL** | required |
| MPR-6 | Reality ledger | HS self-adjoint | self-adjoint or substitute |
| MPR-7 | Krein spectral-shift phase | — | deformation ledger |
| MPR-8 | Falsification declared | **CONFIRMED** | open |

### 3.3 CP-002 discrimination (registered receipts)

| Candidate | J_MPR | phase_pass | Reading |
|-----------|-------|------------|---------|
| K_σ σ=1.0 | low (no prime/density factors) | **False** | Closed lane |
| prime-template mock | high (all factors present) | **True** | Live lane discriminator |
| F5-MM additive masquerade | high L_add, high ℓ_off | **False** | Additive decoy rejected |

**Live-route requirement:** Maximize J_MPR subject to iPiano Lyapunov descent, ℓ_off suppression, and spectral-determinism identity constraints. Necessary filter; not sufficient for RH.

---

## 4. Minimal H_PC architecture

The prime-carrying operator is a **proposed sketch** (RSP-4 OPEN). It threads Kakeya symmetry discipline with prime trace content. Neither alone closes RH.

### 4.1 Decomposition

```text
H_PC = H_BK + B_prime + B_KF

H_BK   = ½(xp + px)                              Berry–Keating archimedean core
B_prime = Σ_{p,k} w_{p,k} · T(log p^k)            w_{p,k} ∝ Λ(p^k)/p^{k/2}
B_KF   = Π_sym F K F⁻¹ Π_sym                      Kakeya/Fourier symmetry correction
```

### 4.2 Role assignment

| Component | Delivers | Open gap |
|-----------|----------|----------|
| H_BK | archimedean N(T) ~ T log T | discreteness; no prime orbits |
| B_prime | explicit-formula prime side | transfer realization on dense domain |
| B_KF | FE symmetry sector; off-critical suppression geometry | must not squash prime support |

### 4.3 DDATL embedding

H_PC lives inside the DDATL host:

```text
T_DD = (I_DD, Λ_{n²}, A, M_DD, H_Φ, D₁, D₂, π_A, ℓ_off)
```

- D₁ supplies quadratic n² readout; D₂ acts on D₁ (dynamic-on-dynamic).
- π_A projects onto declared axes (Re s, Im s, heat-time t, Φ-depth u).
- ℓ_off = ‖(I − π_A) ψ‖² accounts for off-axis leakage.
- Bridge Lemma CC-BL-001 (proposed): Kakeya anti-clustering ↔ ℓ_off suppression ↔ MPR prime phase.

### 4.4 Target identity (RSP-5, OPEN)

```text
det_ζ(H_PC − (z² + ¼)) = C · Ξ(z)
```

Genus 1, order 1, T log T density, prime cumulants — all must match before zero identification (RSP-6).

### 4.5 A_KF ↔ prime junction

A_KF encodes functional-equation symmetry (F H_BK F⁻¹ = −H_BK). It does not automatically carry log(p^k) lengths. The deepening claim:

> Kakeya supplies symmetry-sector discipline and off-critical suppression geometry; primes supply trace content. CC-BL-001 threads them: NonSticky → ℓ_off → MPR → det.

This is the Coleman Conjecture in construction form under the necessary-precursor reading.

---

## 5. Testable CP-003 probes

CP-003 measures **energy–yield density** under L²_C Compress discipline: few E_used, dense ρ_Y.

### 5.1 Definitions

```text
E_used        = Σ_t (1 + 2ℓ_off + r)              action ledger
Y             = L_mult gain (terminal − initial)   coherence yield
compress_ratio = H_init / H_final                   representation densification
ρ_Y           = (Y × compress_ratio) / E_used     yield density
```

**Gate (registered, CP-003 code):** `dense_pass = (E_used ≤ 10) ∧ (ℓ_off_final < 0.20) ∧ (compress_ratio ≥ 1.10) ∧ (gain > 0)`

### 5.2 Track D1 — Multimodal lanes (same seed, max 20 steps)

| Lane | E_used | ρ_Y | ℓ_off_final | dense_pass | Reading |
|------|--------|-----|-------------|------------|---------|
| MPR + iPiano | ~4.6 (3 steps) | highest | → 0 | target | Product structure under ledger |
| F5-MM additive masquerade | ~68.9 | low | ~0.88 | False | Pool volume without axis discipline |
| Naive gradient | intermediate | low | high | False | No proximal constraint |

**Probe hypothesis:** Live route operators should exhibit high ρ_Y at low E_used — dense phase yield per unit action.

### 5.3 Track D2 — Spectral compress (prime-template vs K_σ)

| Lane | ρ_Y | dense_pass | Reading |
|------|-----|------------|---------|
| prime-template mock | ~0.96 | **True** | Few factors, tight phase support |
| K_σ σ=1 | ~0.10 | **False** | Energy without dense yield |

**Probe hypothesis:** Prime-template ρ_Y should exceed K_σ by order of magnitude (~10× in initial runs). A constructed H_PC candidate must beat the K_σ control on ρ_Y while passing MPR phase gates.

### 5.4 Track D3 — L²_C governance read

```text
E_gov = L² × β(T) × C × P × h     with h < 1
```

CP-003 tests whether the live route optimizes L_mult / E_used, not L_add pool volume. Script: `PEAICE-CC-001_cp003_energy_density.py`.

### 5.5 CP-003 forward probes (not yet run)

| Probe | Target | Falsifies if |
|-------|--------|--------------|
| D4: H_PC finite truncation | B_prime transfer matrix on N-prime window | ρ_Y < K_σ control |
| D5: ℓ_off–tube monotonicity | CC-BL-001a clustering → ℓ_off map | No monotone correspondence |
| D6: NB stabilized distance | d_N² with higher-precision G_N | d_N² increases with N under stable conditioning |

All outputs tagged: **NUMERICS | EXPLORATORY | NOT PROOF**.

---

## 6. What would falsify the route

The prime-carrying trace route is falsifiable at each RSP stage. The following observations would close or demote it.

### 6.1 Structural falsifiers

| ID | Observation | Consequence |
|----|-------------|-------------|
| **F1** | κ-extremal Kakeya configuration with a zero off the critical line | Coleman invariant form fails |
| **F2** | RH-realizing operator with no incidence/leakage structure | Antecedent reading fails |
| **F3** | H_PC candidate with smooth density but no log(p^k) support in global traces | MPR-1 fail; route demoted |
| **F4** | det candidate with genus 0 or order ≠ 1 | Cannot equal C·Ξ(z) |
| **F5-MM** | High additive pool + high ℓ_off passes surface tests | Additive masquerade (CP-002 rejects) |

### 6.2 Compute falsifiers

| ID | Observation | Consequence |
|----|-------------|-------------|
| **F6** | ρ(K_σ) → 1 with full cumulant match to Ξ coefficients | Would reopen HS corridor (contradicts current registered state; would require full audit) |
| **F7** | Prime-template mock fails MPR while a non-prime operator passes | MPR objective is not discriminating — redesign gates |
| **F8** | d_N² bounded away from 0 with stable G_N as N → ∞ | NB pivot inconsistent with RH-side trend |
| **F9** | B_KF correction destroys prime support in Tr(h(H_PC)) | A_KF–prime junction fails; CC-BL-001 refuted |

### 6.3 Proof-language falsifier

Any claim that CP numerics prove RH or the Coleman Conjecture falsifies the Solance discipline of this program. Compute produces receipts, not theorems.

---

## 7. What remains open

### 7.1 RSP-6 stage ledger

| Stage | Object | State |
|-------|--------|-------|
| RSP-1 | Disambiguation | **CLOSED** |
| RSP-2 | K_σ audit | **CLOSED-NEGATIVE** |
| RSP-3 | Prime-carrying spec | **OPEN / LIVE** |
| RSP-4 | H_PC construction | **OPEN** |
| RSP-5 | Trace–determinant identity | **OPEN** |
| RSP-6 | Spectral consequence → RH | **OPEN** (conditional on RSP-5) |

### 7.2 Proof obligations (active)

| ID | Obligation |
|----|------------|
| OP1 | Faithful κ linking incidence, ℓ_off, and MPR |
| OP2 | H_PC domain; self-adjoint realization of H_BK + B_prime + B_KF |
| OP3 | Trace formula with Λ(p^k)/p^{k/2} weights |
| OP4 | det_ζ(H − (z²+¼)) = C·Ξ(z); genus/order/density match |
| OP5 | MPR verification (§3) |
| OP6 | Falsification controls F1–F9 |
| OP7 | CC-BL-001a monotone leakage correspondence |
| OP8 | B_KF necessary for symmetry without squashing prime support |

### 7.3 Compute frontier

| Package | Status | Next action |
|---------|--------|-------------|
| CP-001 Track A | **COMPLETE** | Archive as RSP-2 receipt |
| CP-001 Track B | **PARTIAL** | Stabilize G_N; extend N with higher precision |
| CP-002 | **COMPLETE** | MPR objective registered |
| CP-003 Track D1–D2 | **INITIAL RUNS** | Execute D4–D6 forward probes |
| CP-003 Track D3 | **REGISTERED** | L²_C governance mapping confirmed |

### 7.4 Dependency arc (live state)

```text
Kakeya geometry (theorem background)
  → directional / anti-clustering discipline
  → DDATL leakage accounting (formal host)
  → MPR prime-phase objective
  → prime-carrying trace architecture (H_PC)
  → det_ζ(H_PC − (z² + ¼)) = C · Ξ(z)   [OPEN]
  → RH                                    [OPEN]
```

The square-difference wall defined what a closed-negative lane looks like. The live frontier is prime-carrying trace architecture — structure before scale, determinant before zero identity, MPR before closure claim.

**RH remains OPEN. Coleman Conjecture remains OPEN. No proof is claimed.**

---

## File map

| File | Role |
|------|------|
| `../Papers/Grok_in_terminal.docx` | Terminal-001 session record |
| `PEAICE-GROK-TERMINAL-002_Prime-Carrying_Trace_Route.md` | Source note (Grok-Terminal/) |
| `PEAICE-GROK-TERMINAL-002_Prime-Carrying_Trace_Route.docx` | **this document (rendered)** |
| `../Papers/PEAICE-CC-001_Coleman_Conjecture_Solance.docx` | Full Solance paper |
| `../Notes-and-Deepening/PEAICE-CC-001_Deepening_Kakeya_RH_Solance.md` | Bridge Lemma + RSP-6 deepening |
| `../Compute-Packages/PEAICE-CC-001_cp001_ksigma_audit.py` | CP-001 Track A |
| `../Compute-Packages/PEAICE-CC-001_cp001_nb_distance.py` | CP-001 Track B |
| `../Compute-Packages/PEAICE-CC-001_cp002_mpr_objective.py` | CP-002 MPR objective |
| `../Compute-Packages/PEAICE-CC-001_cp003_energy_density.py` | CP-003 energy–yield density |
| `L²_C/Spectral coherence/DDATL6:26:claude/downstream__prime-carrying-trace-architecture.md` | V6.4.3 relocation spec |

---

*PEAICE-GROK-TERMINAL-002 · Prime-Carrying Trace Route · June 2026*