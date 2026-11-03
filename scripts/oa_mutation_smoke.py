"""Score each OA fault variant by named pytest result. Stdlib only.

A clean run has to pass before any variant is scored. DETECTED means pytest
named a failing test. A crash or import error is CRASHED, not DETECTED.
UNDETECTED means the suite passed.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from oa_mutants import MUTANTS  # noqa: E402

_NAMED_FAIL = re.compile(r"^FAILED\s+(\S+)")


def run(name=None):
    env = dict(os.environ)
    env.pop("OA_MUTANT", None)
    if name:
        env["OA_MUTANT"] = name
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "tests/test_oa_probe.py"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    named = []
    seen = set()
    combined = proc.stdout + "\n" + proc.stderr
    for line in combined.splitlines():
        match = _NAMED_FAIL.match(line.strip())
        if not match:
            continue
        node = match.group(1)
        if node not in seen:
            seen.add(node)
            named.append(node)
    tail = (proc.stdout.strip().splitlines() or [""])[-1]
    return proc.returncode, named, tail


def main():
    code, named, tail = run()
    if code != 0 or named:
        print("clean: FAIL (%s)" % tail)
        return 1
    print("clean: PASS (%s)" % tail)
    detected = undetected = crashed = 0
    for name in MUTANTS:
        variant_code, nodes, variant_tail = run(name)
        if nodes:
            detected += 1
            print("FAULT_VARIANT %-26s DETECTED %s" % (name, " ".join(nodes)))
        elif variant_code == 0:
            undetected += 1
            print("FAULT_VARIANT %-26s UNDETECTED (%s)" % (name, variant_tail))
        else:
            crashed += 1
            print("FAULT_VARIANT %-26s CRASHED (%s)" % (name, variant_tail))
    total = len(MUTANTS)
    print(
        "DETECTED %d of %d fault variants; UNDETECTED %d; CRASHED %d"
        % (detected, total, undetected, crashed))
    if undetected or crashed or detected != total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
