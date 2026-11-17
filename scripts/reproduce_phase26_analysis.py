"""
Phase 26 Analysis & Accounting Reproduction Script
Acoustic Gunshot Detection Research Prototype
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import subprocess

def main():
    print("=" * 80)
    print("PHASE 26 REPRODUCTION & VERIFICATION SCRIPT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print("\n[Step 1/3] Verifying Baseline Models & Historical Archives...")
    freeze_script = os.path.join(base_dir, "scripts", "freeze_phase26_baseline.py")
    res = subprocess.run([sys.executable, freeze_script], capture_output=True, text=True)
    if res.returncode != 0:
        print("[FAIL] Baseline verification failed:")
        print(res.stderr)
        sys.exit(1)
    print(res.stdout.strip())

    print("\n[Step 2/3] Rebuilding Phase 26 Acquisition & Accounting Datasets...")
    build_script = os.path.join(base_dir, "scripts", "build_phase26_acquisition_and_sources.py")
    res = subprocess.run([sys.executable, build_script], capture_output=True, text=True)
    if res.returncode != 0:
        print("[FAIL] Dataset build failed:")
        print(res.stderr)
        sys.exit(1)
    print(res.stdout.strip())

    print("\n[Step 3/3] Executing Automated Pytest Suite (20 Tests)...")
    test_file = os.path.join(base_dir, "tests", "test_phase26_acquisition.py")
    res = subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"], capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode != 0:
        print("[FAIL] Test suite failed:")
        print(res.stderr)
        sys.exit(1)

    print("\n" + "=" * 80)
    print("[SUCCESS] Phase 26 analysis and verification reproduced cleanly.")
    print("=" * 80)

if __name__ == "__main__":
    main()
