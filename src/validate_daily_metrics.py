
from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# SKYLENS | DAILY METRICS VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"
CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "analytics"
    / "daily_performance.csv"
)

print("=" * 65)
print("SKYLENS | DAILY METRICS VALIDATION")
print("=" * 65)

if not DB_PATH.exists():
    raise FileNotFoundError(DB_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

exported = pd.read_csv(CSV_PATH)
exported["flight_date"] = pd.to_datetime(exported["flight_date"])

# ----------------------------------------------------------
# 1. INDEPENDENT DATABASE CALCULATION
# ----------------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=True)

recalculated = con.execute("""
    SELECT
        flight_date,

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
            AS delay_rate_pct

    FROM fact_flights

    GROUP BY flight_date

    ORDER BY flight_date
""").df()

con.close()

recalculated["flight_date"] = pd.to_datetime(
    recalculated["flight_date"]
)

# ----------------------------------------------------------
# 2. MATCH DAILY RECORDS
# ----------------------------------------------------------

merged = exported.merge(
    recalculated,
    on="flight_date",
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
    len(merged) == 31,
    f"Expected 31 reporting dates (found {len(merged)})"
)

check(
    (merged["_merge"] == "both").all(),
    "Exported dates match database reporting dates"
)

# ----------------------------------------------------------
# 3. VALIDATE DAILY METRICS
# ----------------------------------------------------------

metrics = [
    ("evaluated_arrivals", 0.0),
    ("delayed_arrivals", 0.0),
    ("delay_rate_pct", 0.01)
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
# 4. VALIDATE NETWORK TOTALS
# ----------------------------------------------------------

total_evaluated = merged[
    "evaluated_arrivals_exported"
].sum()

total_delayed = merged[
    "delayed_arrivals_exported"
].sum()

check(
    total_evaluated == 522269,
    f"Daily evaluated arrivals reconcile to 522,269 "
    f"(found {total_evaluated:,.0f})"
)

check(
    total_delayed == 98130,
    f"Daily delayed arrivals reconcile to 98,130 "
    f"(found {total_delayed:,.0f})"
)

# ----------------------------------------------------------
# 5. VALIDATION SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("DAILY VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks performed: {checks}")
print(f"Checks failed:    {failures}")

if failures == 0:
    print("\nDAILY METRICS VALIDATED SUCCESSFULLY.")
else:
    print("\nDAILY METRICS REQUIRE INVESTIGATION.")

print("=" * 65)
