#!/usr/bin/env python3
"""
PEAICE-GROK-ZETA0-TYPO-THRUPUT-001 — prime-repurposed typo throughput along ζ(0).

Anchor: ζ(0) = -1/2. Typos map to primes in order; clean lane = CONFIRM + NO_BRUTEFORCE.
stdlib only · NOT PROOF · RH OPEN
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from typing import Any

ZETA0 = -0.5
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


def prime_for_index(k: int) -> int:
    if k < 1 or k > len(PRIMES):
        raise ValueError(f"typo index {k} exceeds prime table ({len(PRIMES)})")
    return PRIMES[k - 1]


def receipt(pairs: list[tuple[str, str]]) -> dict[str, Any]:
    if not pairs:
        return {
            "designation": "PEAICE-GROK-ZETA0-TYPO-THRUPUT-001",
            "zeta0": ZETA0,
            "lane": "clean",
            "E_typo": 0,
            "prime_tuple": [],
            "P_zeta": 1,
            "T_zeta": 0.0,
            "confirm": True,
            "no_bruteforce": True,
            "typos": [],
        }

    prime_tuple = [prime_for_index(i + 1) for i in range(len(pairs))]
    P_zeta = 1
    T_zeta = 0.0
    for p in prime_tuple:
        P_zeta *= p
        T_zeta += math.log(p)

    typos = [
        {"k": i + 1, "surface": s, "intended": t, "p_k": prime_tuple[i]}
        for i, (s, t) in enumerate(pairs)
    ]

    body = json.dumps(
        {"zeta0": ZETA0, "prime_tuple": prime_tuple, "P_zeta": P_zeta},
        sort_keys=True,
    )
    sha = hashlib.sha256(body.encode()).hexdigest()

    return {
        "designation": "PEAICE-GROK-ZETA0-TYPO-THRUPUT-001",
        "zeta0": ZETA0,
        "lane": "typo",
        "E_typo": len(pairs),
        "prime_tuple": prime_tuple,
        "P_zeta": P_zeta,
        "T_zeta": round(T_zeta, 6),
        "confirm": True,
        "no_bruteforce": True,
        "typos": typos,
        "sha256": sha,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="ζ(0) typo-throughput receipt")
    ap.add_argument("--clean", action="store_true", help="clean lane (zero typos)")
    ap.add_argument("--pairs", type=str, default="[]", help='JSON list of [surface,intended] pairs')
    args = ap.parse_args()

    if args.clean:
        out = receipt([])
    else:
        raw = json.loads(args.pairs)
        pairs = [(str(a), str(b)) for a, b in raw]
        out = receipt(pairs)

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())