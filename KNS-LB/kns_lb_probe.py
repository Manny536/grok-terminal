#!/usr/bin/env python3
# kns_lb_probe.py - PEAICE-CLAUDEV6-KNS-LB - OB-KNS-1 / OB-KNS-2 hook
# Status: NUMERICS - single-runner - deterministic (no RNG, stdlib only)
# Model class: rank-one / two-mode Gaussian registers in carrier R^d.
#
# Honesty notes (load-bearing):
#  (H1) l_off in the rank-one register model depends ONLY on center placement
#       delta - the direction fan does not enter it. That is the typed point:
#       placement is register data, not glare data (Prop 3.3). Fan data enters
#       L2_C dimension bookkeeping only.
#  (H2) Aligned-lane E_used is ledger-determined by CP-003 arithmetic
#       (E = sum(1+2*l_off+r) with l_off ~ 0), not an independent empirical
#       discovery. CP-001 Track-B class caveat applies.
#  (H3) Y*compress = 1.463 is a calibration import from the CP-003 seed-7
#       receipt (rho_Y ~ 0.438 at E_used ~ 3.34, MPR+iPiano lane).
#       Independent Y measurement is a CP-004 obligation.

import math, hashlib, sys, json

W   = 0.35    # register mode width
L   = 2.0     # two-mode register separation
R_T = 0.5     # CP-003 residual term r_t (imported convention; probe input)
YC  = 1.463   # Y*compress calibration (H3)

def g(x, w=W):                 # unit-Gaussian overlap <phi_0, phi_x>
    return math.exp(-(x * x) / (4.0 * w * w))

def ell_unimodal(d):           # A = span{phi_C0}; psi = phi_{C0 + d e}
    return 1.0 - g(d) ** 2     # = 1 - exp(-d^2 / (2 w^2)), strictly increasing

def ell_twomode(d, l=L):       # A = span{phi_C0, phi_{C0 + L e}} (Gram-corrected)
    a, b, s = g(d), g(l - d), g(l)
    proj = (a * a - 2 * a * b * s + b * b) / (1.0 - s * s)
    return 1.0 - proj          # zero at d=0 AND d=L -> non-monotone by design

def monotone_strict(vals):
    return all(y > x for x, y in zip(vals, vals[1:]))

def ledger(ell_seq, r=R_T):    # CP-003 action ledger: E_used = sum_t(1+2*l_off+r)
    return sum(1.0 + 2.0 * e + r for e in ell_seq)

def retention(kappa=0.1, delta=1.0, tmax=6.0, n=13):
    # two-level protected-sector toy: ||P_A exp(-itH) psi||^2, Rabi closed form
    Om = math.sqrt(delta * delta + kappa * kappa)
    ts = [tmax * i / (n - 1) for i in range(n)]
    return [(t, 1.0 - (kappa * kappa / (Om * Om)) * math.sin(Om * t) ** 2)
            for t in ts]

def probe(delta_align=0.05, steps=2):
    grid = [i * 0.05 for i in range(0, 41)]            # offsets 0.00 .. 2.00
    uni  = [ell_unimodal(d) for d in grid]
    two  = [ell_twomode(d) for d in grid]
    ellT = ell_unimodal(delta_align)
    E    = ledger([ellT] * steps)
    rho  = YC / E
    curve = retention()
    dense = (E <= 10.0) and (ellT < 0.20) and (rho >= 0.4)
    return {
        "delta_align": delta_align, "steps": steps,
        "ell_off_T": round(ellT, 6),
        "E_used": round(E, 4), "rho_Y": round(rho, 4), "dense_pass": dense,
        "D5_unimodal_monotone": monotone_strict(uni),
        "D5_twomode_monotone": monotone_strict(two),
        "twomode_peak_ell": round(max(two), 4),
        "twomode_peak_at": round(grid[two.index(max(two))], 2),
        "retention_min": round(min(v for _, v in curve), 5),
        "retention_curve": [(round(t, 2), round(v, 5)) for t, v in curve],
    }

if __name__ == "__main__":
    out = probe()
    print("=== KNS-LB PROBE RECEIPT (seedless / deterministic) ===")
    print(json.dumps(out, indent=1))
    print("script_sha256:", hashlib.sha256(open(__file__, "rb").read()).hexdigest())
    print("python:", sys.version.split()[0])
    # D5 expectation: unimodal register monotone TRUE, two-mode monotone FALSE,
    # aligned lane dense_pass TRUE. Any deviation falsifies the scoped claims.
    ok = (out["D5_unimodal_monotone"]
          and not out["D5_twomode_monotone"]
          and out["dense_pass"])
    print("D5_expectation_met:", ok)
    sys.exit(0 if ok else 1)
