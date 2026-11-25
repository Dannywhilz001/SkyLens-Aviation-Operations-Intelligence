
from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# SKYLENS | DELAY CAUSE VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"
CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "analytics"
    / "delay_cause_contributions.csv"
)

print("=" * 65)
print("SKYLENS | DELAY CAUSE VALIDATION")
print("=" * 65)

if not DB_PATH.exists():
    raise FileNotFoundError(DB_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

exported = pd.read_csv(CSV_PATH)

# ----------------------------------------------------------
# 1. INDEPENDENTLY RECALCULATE DELAY CAUSES
# ----------------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=True)

recalculated = con.execute("""
    WITH causes AS (

        SELECT
            'Carrier' AS delay_cause,
            SUM(carrier_delay_minutes) AS total_delay_minutes
        FROM fact_flights

        UNION ALL

        SELECT
            'Late Aircraft',
            SUM(late_aircraft_delay_minutes)
        FROM fact_flights

        UNION ALL

        SELECT
            'NAS',
            SUM(nas_delay_minutes)
        FROM fact_flights

        UNION ALL

        SELECT
            'Weather',
            SUM(weather_delay_minutes)
        FROM fact_flights

        UNION ALL

        SELECT
            'Security',
            SUM(security_delay_minutes)
        FROM fact_flights
    )

    SELECT
        delay_cause,
        total_delay_minutes,
        100.0 * total_delay_minutes
            / NULLIF(SUM(total_delay_minutes) OVER (), 0)
            AS contribution_pct
    FROM causes
    ORDER BY delay_cause
""").df()

con.close()

# ----------------------------------------------------------
# 2. MATCH EXPORTED AND DATABASE RESULTS
# ----------------------------------------------------------

merged = exported.merge(
    recalculated,
    on="delay_cause",
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
    len(merged) == 5,
    f"Expected 5 delay causes (found {len(merged)})"
)

check(
    (merged["_merge"] == "both").all(),
    "Exported delay causes match database categories"
)

# ----------------------------------------------------------
# 3. VALIDATE TOTAL DELAY MINUTES
# ----------------------------------------------------------

exported_minutes = pd.to_numeric(
    merged["total_delay_minutes_exported"],
    errors="coerce"
)

database_minutes = pd.to_numeric(
    merged["total_delay_minutes_database"],
    errors="coerce"
)

check(
    (
        exported_minutes.notna()
        & database_minutes.notna()
        & ((exported_minutes - database_minutes).abs() <= 0.01)
    ).all(),
    "Total delay minutes match independent database calculations"
)

# ----------------------------------------------------------
# 4. VALIDATE CONTRIBUTION PERCENTAGES
# ----------------------------------------------------------

exported_pct = pd.to_numeric(
    merged["contribution_pct_exported"],
    errors="coerce"
)

database_pct = pd.to_numeric(
    merged["contribution_pct_database"],
    errors="coerce"
)

check(
    (
        exported_pct.notna()
        & database_pct.notna()
        & ((exported_pct - database_pct).abs() <= 0.01)
    ).all(),
    "Contribution percentages match independent calculations"
)

# ----------------------------------------------------------
# 5. VALIDATE TOTAL CONTRIBUTION
# ----------------------------------------------------------

contribution_total = exported_pct.sum()

check(
    abs(contribution_total - 100.0) <= 0.02,
    f"Exported contributions total approximately 100% "
    f"(found {contribution_total:.2f}%)"
)

# ----------------------------------------------------------
# 6. VALIDATION SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("DELAY CAUSE VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks performed: {checks}")
print(f"Checks failed:    {failures}")

if failures == 0:
    print("\nDELAY CAUSE METRICS VALIDATED SUCCESSFULLY.")
else:
    print("\nDELAY CAUSE METRICS REQUIRE INVESTIGATION.")

print("=" * 65)
