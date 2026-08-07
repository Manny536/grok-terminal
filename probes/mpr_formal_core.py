#!/usr/bin/env python3
"""
PEAICE-GROK-TERMINAL-007 — MPR formal-core structural probe.

Deterministic · stdlib only · NOT a spectral PASS · NOT RH progress.
Certifies definition hygiene: μ_× sample arithmetic, gate registry,
firewall phrases, and J_MPR schema consistency.
"""

from __future__ import annotations

import json
import math
import sys
from typing import Any

# First primes for sample μ_× weight checks
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

GATES = [
    ("MPR-1", "prime_length_support"),
    ("MPR-2", "weight_class_p_half"),
    ("MPR-3", "density_N_T"),
    ("MPR-4", "functional_equation_parity"),
    ("MPR-5", "genus_order_det_reg"),
    ("MPR-6", "reality_ledger"),
    ("MPR-7", "krein_spectral_shift_phase"),
    ("MPR-8", "falsification_declared"),
]

# Firewall: these must never collapse in receipts
FIREWALL = [
    ("MPR_PASS", "RH_progress"),
    ("MPR_iPiano_energy", "MPR_spectral_PASS"),
    ("rho_Y", "q_m"),
    ("mu_times", "archimedean_background"),
    ("K_sigma", "K_PC"),
    ("MPR_multimodal", "executable"),
]


def mu_times_weight(p: int, k: int) -> float:
    """Weight of δ_{± k log p} in μ_×: (log p) / p^{k/2}."""
    return math.log(p) / (p ** (k / 2.0))


def sample_mu_times(max_k: int = 3) -> list[dict[str, Any]]:
    rows = []
    for p in PRIMES[:8]:
        for k in range(1, max_k + 1):
            w = mu_times_weight(p, k)
            rows.append(
                {
                    "p": p,
                    "k": k,
                    "length": k * math.log(p),
                    "weight": w,
                    "symmetric": True,  # + and − lengths
                }
            )
    return rows


def j_mpr(q: list[float], w: list[float], ell_off: float, r: float,
          lam_leak: float, lam_res: float) -> float:
    assert len(q) == len(w)
    # clamp for log stability in hygiene checks
    core = sum(wi * math.log(max(qi, 1e-300)) for wi, qi in zip(w, q))
    return core - lam_leak * ell_off - lam_res * r


def check_mu_times_monotonic_in_k() -> list[str]:
    """For fixed p, weights must strictly decrease in k."""
    errors = []
    for p in PRIMES[:6]:
        prev = None
        for k in range(1, 5):
            w = mu_times_weight(p, k)
            if prev is not None and not (w < prev):
                errors.append(f"weight not decreasing p={p} k={k}")
            prev = w
            if w <= 0:
                errors.append(f"non-positive weight p={p} k={k}")
    return errors


def check_j_mpr_product_vs_additive() -> list[str]:
    """Jensen: mean log ≤ log mean → product core ≤ additive decoy (same q,w)."""
    errors = []
    q = [0.9, 0.7, 0.5, 0.8]
    w = [0.25, 0.25, 0.25, 0.25]
    L_mult = sum(wi * math.log(qi) for wi, qi in zip(w, q))
    L_add = math.log(sum(wi * qi for wi, qi in zip(w, q)))
    if not (L_mult <= L_add + 1e-12):
        errors.append(f"Jensen violated: L_mult={L_mult} > L_add={L_add}")
    # recognition quality map q_m = exp(-e^2) in [0,1]
    for e in (0.0, 0.5, 1.0, 2.0):
        qm = math.exp(-(e**2))
        if not (0.0 < qm <= 1.0):
            errors.append(f"q_m out of range for e={e}")
    return errors


def check_gate_registry() -> list[str]:
    errors = []
    if len(GATES) != 8:
        errors.append(f"expected 8 gates, got {len(GATES)}")
    ids = [g[0] for g in GATES]
    for i, expected in enumerate([f"MPR-{n}" for n in range(1, 9)], start=0):
        if ids[i] != expected:
            errors.append(f"gate order {ids[i]} != {expected}")
    if len(set(ids)) != 8:
        errors.append("duplicate gate ids")
    return errors


def check_firewall_distinct() -> list[str]:
    errors = []
    for a, b in FIREWALL:
        if a == b:
            errors.append(f"firewall collapse {a}")
        if not a or not b:
            errors.append("empty firewall token")
    return errors


def check_status_lattice() -> list[str]:
    """Typed status lattice for TERMINAL-007 deepen."""
    lattice = {
        "definition_equality": "FORMAL",
        "kill_filter": "KILL-FILTER",
        "satisfaction": "OPEN",
        "K_sigma_route": "CLOSED-NEGATIVE",
        "multimodal": "NON-COMPUTABLE",
        "energy_baseline": "REGISTERED",
        "RH": "OPEN",
        "Coleman": "OPEN",
        "h": "<1",
    }
    errors = []
    if lattice["definition_equality"] == lattice["satisfaction"]:
        errors.append("definition must not equal satisfaction")
    if lattice["kill_filter"] == "THEOREM":
        errors.append("kill-filter must not be theorem")
    if lattice["RH"] != "OPEN":
        errors.append("RH must remain OPEN")
    if lattice["h"] != "<1":
        errors.append("h must be <1")
    # PASS non-promoting
    if lattice.get("PASS_implies_RH"):
        errors.append("PASS must not imply RH")
    return errors, lattice


def main() -> int:
    errors: list[str] = []
    errors += check_mu_times_monotonic_in_k()
    errors += check_j_mpr_product_vs_additive()
    errors += check_gate_registry()
    errors += check_firewall_distinct()
    status_errors, lattice = check_status_lattice()
    errors += status_errors

    # Sample J_MPR numeric hygiene
    q = [math.exp(-(e**2)) for e in (0.1, 0.2, 0.4, 0.3)]
    w = [0.3, 0.3, 0.2, 0.2]
    J = j_mpr(q, w, ell_off=0.01, r=0.02, lam_leak=1.0, lam_res=0.5)
    if not math.isfinite(J):
        errors.append("J_MPR non-finite")

    rows = sample_mu_times()
    # weight at (2,1): log(2)/sqrt(2)
    expected_21 = math.log(2) / math.sqrt(2)
    got_21 = mu_times_weight(2, 1)
    if abs(got_21 - expected_21) > 1e-12:
        errors.append(f"μ_×(2,1) weight {got_21} != {expected_21}")

    receipt = {
        "designation": "PEAICE-GROK-TERMINAL-007-PROBE",
        "primary_object": "PEAICE-MPR-FORMAL-CORE-001",
        "probe_class": "definition_hygiene",
        "ok": not errors,
        "status": "DEFINITION_HYGIENE_PASS" if not errors else "DEFINITION_HYGIENE_FAIL",
        "layers": {
            "A_kill_filter": "KILL-FILTER",
            "B_J_MPR_objective": "REGISTERED_SUPPORTING",
            "C_equality_definition": "FORMAL",
            "D_live_operator": "OPEN",
            "E_multimodal": "NON-COMPUTABLE",
            "F_energy_baseline": "REGISTERED",
        },
        "status_lattice": lattice,
        "gates": [{"id": g, "name": n} for g, n in GATES],
        "firewall": [{"left": a, "right": b, "collapsed": False} for a, b in FIREWALL],
        "mu_times_sample": {
            "n_terms": len(rows),
            "first": rows[0],
            "weight_p2_k1": got_21,
            "formula": "(log p) / p^{k/2} at ± k log p",
        },
        "J_MPR_sample": {
            "value": J,
            "form": "sum w_m log q_m - λ_leak ℓ_off - λ_res r",
            "q_m_map": "exp(-e_m^2)",
            "rho_Y_reserved": True,
        },
        "claims": {
            "definition_formal": True,
            "satisfaction_open": True,
            "pass_non_promoting": True,
            "rh_open": True,
            "h_lt_1": True,
        },
        "errors": errors,
        "note": "Certifies definition hygiene only. Does not certify M_τ = μ_× for any operator.",
    }

    print(json.dumps(receipt, indent=2))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
