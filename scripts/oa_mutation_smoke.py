"""Run tests/test_oa_probe.py once per OA mutant; report kills. Stdlib only."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
from oa_mutants import MUTANTS  # noqa: E402


def run(m=None):
    env = dict(os.environ); env.pop("OA_MUTANT", None)
    if m:
        env["OA_MUTANT"] = m
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "tests/test_oa_probe.py"], cwd=ROOT, env=env, capture_output=True, text=True)
    return p.returncode, (p.stdout.strip().splitlines() or [""])[-1]


def main():
    code, tail = run()
    print("clean: %s (%s)" % ("PASS" if code == 0 else "FAIL", tail))
    k = 0
    for m in MUTANTS:
        c, t = run(m); k += c != 0
        print("%-26s %s (%s)" % (m, "KILLED" if c else "SURVIVED", t))
    print("killed %d of %d mutants" % (k, len(MUTANTS)))
    return 0 if code == 0 and k == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
