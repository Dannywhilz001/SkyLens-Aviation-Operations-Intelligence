
from pathlib import Path
import subprocess
import sys
import re

# ==========================================================
# SKYLENS | MASTER VALIDATION RUNNER
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

VALIDATION_SCRIPTS = [
    "validate_analytical_outputs.py",
    "validate_carrier_metrics.py",
    "validate_airport_metrics.py",
    "validate_route_metrics.py",
    "validate_delay_causes.py",
    "validate_daily_metrics.py"
]

print("=" * 70)
print("SKYLENS | MASTER VALIDATION RUNNER")
print("=" * 70)

results = []
total_failures = 0

# ----------------------------------------------------------
# 1. RUN EACH VALIDATION MODULE
# ----------------------------------------------------------

for script_name in VALIDATION_SCRIPTS:

    script_path = SRC_DIR / script_name

    print(f"\n{'=' * 70}")
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    if not script_path.exists():
        print(f"[FAIL] Validation script missing: {script_name}")
        results.append((script_name, False))
        total_failures += 1
        continue

    process = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True
    )

    print(process.stdout)

    if process.stderr:
        print("ERROR OUTPUT:")
        print(process.stderr)

    # ------------------------------------------------------
    # 2. INSPECT VALIDATION RESULT
    # ------------------------------------------------------

    failure_match = re.search(
        r"Checks failed:\s*(\d+)",
        process.stdout
    )

    if failure_match is None:
        failure_match = re.search(
            r"Checks failed:\s*(\d+)",
            process.stderr
        )

    if process.returncode != 0:
        passed = False

    elif failure_match is None:
        passed = False

    elif int(failure_match.group(1)) != 0:
        passed = False

    else:
        passed = True

    if passed:
        print(f"[PASS] {script_name}")
    else:
        print(f"[FAIL] {script_name}")
        total_failures += 1

    results.append((script_name, passed))

# ----------------------------------------------------------
# 3. MASTER SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 70)
print("SKYLENS | MASTER VALIDATION SUMMARY")
print("=" * 70)

for script_name, passed in results:

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {script_name}")

successful_modules = sum(
    1 for _, passed in results if passed
)

print("-" * 70)
print(f"Validation modules: {len(results)}")
print(f"Modules passed:    {successful_modules}")
print(f"Modules failed:    {total_failures}")

if total_failures == 0:
    print("\nSKYLENS MASTER VALIDATION: ALL MODULES PASSED.")
else:
    print("\nSKYLENS MASTER VALIDATION: INVESTIGATION REQUIRED.")

print("=" * 70)

# ----------------------------------------------------------
# 4. RETURN A FAILURE EXIT CODE IF ANY MODULE FAILS
# ----------------------------------------------------------

if total_failures > 0:
    sys.exit(1)
