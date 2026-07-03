#!/usr/bin/env python3
"""Run Grok-Terminal probes and emit reproducibility stamp (stdlib only)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBES = [
    ROOT / "KNS-LB" / "kns_lb_probe.py",
    ROOT / "probes" / "zeta0_typo_thruput.py",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_probe(path: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=path.parent,
    )
    out = proc.stdout.strip()
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "exit_code": proc.returncode,
        "stdout_sha256": hashlib.sha256(out.encode()).hexdigest() if out else None,
        "stdout_preview": out[:240] if out else "",
    }


def main() -> int:
    results = [run_probe(p) for p in PROBES]
    stamp = {
        "designation": "PEAICE-GROK-TERMINAL-PROBE-STAMP",
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version.split()[0],
        "probes": results,
        "all_exit_zero": all(r["exit_code"] == 0 for r in results),
    }
    out_path = ROOT / "_probe_stamp.json"
    out_path.write_text(json.dumps(stamp, indent=2), encoding="utf-8")
    print(json.dumps(stamp, indent=2))
    return 0 if stamp["all_exit_zero"] else 1


if __name__ == "__main__":
    raise SystemExit(main())