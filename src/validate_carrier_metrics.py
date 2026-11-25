
from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# SKYLENS | CARRIER METRICS VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"

CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "analytics"
    / "carrier_performance.csv"
)

print("=" * 65)
print("SKYLENS | CARRIER METRICS VALIDATION")
print("=" * 65)

# ----------------------------------------------------------
# 1. LOAD EXPORTED RESULTS
# ----------------------------------------------------------

if not DB_PATH.exists():
    raise FileNotFoundError(DB_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

exported = pd.read_csv(CSV_PATH)

# ----------------------------------------------------------
# 2. INDEPENDENTLY RECALCULATE FROM DUCKDB
# ----------------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=True)

recalculated = con.execute("""
    SELECT
        reporting_carrier_code AS carrier,

        COUNT(*) AS total_flights,

        COUNT(arrival_delayed_15)
            AS evaluated_arrivals,

        SUM(
            CASE
                WHEN arrival_delayed_15 = 1 THEN 1
                ELSE 0
            END
        ) AS delayed_arrivals,

        100.0 * SUM(
            CASE
                WHEN arrival_delayed_15 = 1 THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(arrival_delayed_15), 0)
            AS delay_rate_pct,

        AVG(arrival_delay_minutes)
            AS avg_signed_delay_minutes

    FROM fact_flights

    GROUP BY reporting_carrier_code

    ORDER BY reporting_carrier_code
""").df()

con.close()

# ----------------------------------------------------------
# 3. COMPARE EXPORTED AND RECALCULATED RESULTS
# ----------------------------------------------------------

merged = exported.merge(
    recalculated,
    on="carrier",
    how="outer",
    suffixes=("_exported", "_database"),
    indicator=True
)

checks = 0
failures = 0


def check(condition, description):
    global checks, failures

    checks += 1

    if condition:
        print(f"[PASS] {description}")
    else:
        print(f"[FAIL] {description}")
        failures += 1


check(
    len(merged) == 14,
    "All 14 carriers are represented in both datasets"
)

check(
    (merged["_merge"] == "both").all(),
    "Exported carrier codes match database carrier codes"
)

# ----------------------------------------------------------
# 4. VALIDATE NUMERIC METRICS
# ----------------------------------------------------------

metrics = [
    ("total_flights", 0.0),
    ("evaluated_arrivals", 0.0),
    ("delayed_arrivals", 0.0),
    ("delay_rate_pct", 0.01),
    ("avg_signed_delay_minutes", 0.01)
]

for metric, tolerance in metrics:

    exported_values = pd.to_numeric(
        merged[f"{metric}_exported"],
        errors="coerce"
    )

    database_values = pd.to_numeric(
        merged[f"{metric}_database"],
        errors="coerce"
    )

    differences = (
        exported_values - database_values
    ).abs()

    valid = (
        differences.notna()
        & (differences <= tolerance)
    )

    check(
        valid.all(),
        f"{metric} matches independent database calculation"
    )

# ----------------------------------------------------------
# 5. VALIDATION SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("CARRIER VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks performed: {checks}")
print(f"Checks failed:    {failures}")

if failures == 0:
    print("\nCARRIER METRICS VALIDATED SUCCESSFULLY.")
else:
    print("\nCARRIER METRICS REQUIRE INVESTIGATION.")

print("=" * 65)
