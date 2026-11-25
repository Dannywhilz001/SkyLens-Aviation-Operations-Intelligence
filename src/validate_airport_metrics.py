
from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# SKYLENS | AIRPORT METRICS VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"
CSV_PATH = BASE_DIR / "data" / "processed" / "analytics" / "airport_performance.csv"

print("=" * 65)
print("SKYLENS | AIRPORT METRICS VALIDATION")
print("=" * 65)

if not DB_PATH.exists():
    raise FileNotFoundError(DB_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

exported = pd.read_csv(CSV_PATH)

# ----------------------------------------------------------
# 1. INDEPENDENT DATABASE CALCULATION
# ----------------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=True)

recalculated = con.execute("""
    SELECT
        destination AS airport,
        destination_city AS city,

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

        AVG(
            CASE
                WHEN arrival_delayed_15 = 1
                THEN delay_cause_total_minutes
            END
        ) AS avg_delay_intensity_minutes

    FROM fact_flights

    GROUP BY destination, destination_city

    HAVING COUNT(arrival_delayed_15) >= 500

    ORDER BY destination
""").df()

con.close()

# ----------------------------------------------------------
# 2. COMPARE EXPORTED RESULTS
# ----------------------------------------------------------

merged = exported.merge(
    recalculated,
    on="airport",
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
    len(merged) == 125,
    f"Expected 125 airports (found {len(merged)})"
)

check(
    (merged["_merge"] == "both").all(),
    "Exported airport codes match database airport codes"
)

# ----------------------------------------------------------
# 3. VALIDATE CITY NAMES
# ----------------------------------------------------------

city_match = (
    merged["city_exported"].fillna("").astype(str)
    ==
    merged["city_database"].fillna("").astype(str)
)

check(
    city_match.all(),
    "Airport city names match database records"
)

# ----------------------------------------------------------
# 4. VALIDATE NUMERIC METRICS
# ----------------------------------------------------------

metrics = [
    ("evaluated_arrivals", 0.0),
    ("delayed_arrivals", 0.0),
    ("delay_rate_pct", 0.01),
    ("avg_delay_intensity_minutes", 0.01)
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
# 5. SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("AIRPORT VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks performed: {checks}")
print(f"Checks failed:    {failures}")

if failures == 0:
    print("\nAIRPORT METRICS VALIDATED SUCCESSFULLY.")
else:
    print("\nAIRPORT METRICS REQUIRE INVESTIGATION.")

print("=" * 65)
