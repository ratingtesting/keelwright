#!/usr/bin/env python3
"""Run RED-BATTERY: swap implementation under test and verify tests fail on buggy version.

Usage:
    python scripts/red_battery.py test_module.py correct_impl.py buggy_impl.py
"""
import sys
import subprocess
import pathlib

def run_pytest(test_file: str, impl_file: str) -> tuple[bool, str]:
    """Run pytest on test_file with impl_file as the implementation."""
    here = pathlib.Path(__file__).parent.parent
    env = dict(PYTHONPATH=str(here))
    r = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-q", "--tb=no"],
        cwd=here,
        capture_output=True,
        text=True,
        env=env
    )
    out = r.stdout + r.stderr
    all_green = "FAILED" not in out
    return all_green, out

def main():
    if len(sys.argv) != 4:
        print("Usage: red_battery.py <tests.py> <correct_impl.py> <buggy_impl.py>")
        sys.exit(2)

    test_file, correct_impl, buggy_impl = sys.argv[1:4]
    here = pathlib.Path(__file__).parent.parent

    # Phase 1: correct implementation should PASS
    (here / correct_impl).rename(here / "implementation.py")
    green1, out1 = run_pytest(test_file, "implementation.py")
    print(f"Phase 1 ({correct_impl}): {'PASS' if green1 else 'FAIL'}")
    print(out1[:800])

    # Phase 2: buggy implementation should FAIL
    (here / "implementation.py").rename(here / buggy_impl)
    green2, out2 = run_pytest(test_file, buggy_impl)
    print(f"Phase 2 ({buggy_impl}): {'RED on buggy' if not green2 else 'GREEN on buggy — trap weak'}")
    print(out2[:1200])

    # Restore correct
    (here / buggy_impl).rename(here / correct_impl)

    if green1 and not green2:
        print("\nRED-BATTERY RESULT: PASS — tests derived from spec, not tautological")
        sys.exit(0)
    elif green1 and green2:
        print("\nRED-BATTERY RESULT: FAIL — tests green on both, likely tautological")
        sys.exit(1)
    else:
        print("\nRED-BATTERY RESULT: INCONCLUSIVE — tests fail on correct impl")
        sys.exit(2)

if __name__ == "__main__":
    main()
