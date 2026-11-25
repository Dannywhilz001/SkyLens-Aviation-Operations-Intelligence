
from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# SKYLENS | ROUTE METRICS VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"
CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "analytics"
    / "route_performance.csv"
)

print("=" * 65)
print("SKYLENS | ROUTE METRICS VALIDATION")
print("=" * 65)

if not DB_PATH.exists():
    raise FileNotFoundError(DB_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

exported = pd.read_csv(CSV_PATH)

# ----------------------------------------------------------
# 1. INDEPENDENTLY RECALCULATE ROUTE METRICS
# ----------------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=True)

recalculated = con.execute("""
    SELECT
        origin,
        destination,

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

    GROUP BY origin, destination

    HAVING COUNT(arrival_delayed_15) >= 300

    ORDER BY origin, destination
""").df()

con.close()

# ----------------------------------------------------------
# 2. MATCH ROUTES BY DIRECTION
# ----------------------------------------------------------

merged = exported.merge(
    recalculated,
    on=["origin", "destination"],
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
    len(merged) == 324,
    f"Expected 324 directional routes (found {len(merged)})"
)

check(
    (merged["_merge"] == "both").all(),
    "Exported route pairs match database route pairs"
)

# ----------------------------------------------------------
# 3. VALIDATE ROUTE METRICS
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
# 4. CHECK ROUTE CLASSIFICATION COVERAGE
# ----------------------------------------------------------

classification_valid = (
    merged["classification"].notna()
    & merged["classification"].astype(str).str.strip().ne("")
).all()

check(
    classification_valid,
    "Every exported route has a classification"
)

# ----------------------------------------------------------
# 5. VALIDATION SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("ROUTE VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks performed: {checks}")
print(f"Checks failed:    {failures}")

if failures == 0:
    print("\nROUTE METRICS VALIDATED SUCCESSFULLY.")
else:
    print("\nROUTE METRICS REQUIRE INVESTIGATION.")

print("=" * 65)
