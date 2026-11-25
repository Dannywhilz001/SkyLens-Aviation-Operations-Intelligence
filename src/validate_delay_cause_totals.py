
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "fact_flights.parquet"

con = duckdb.connect(database=":memory:")

print("=" * 65)
print("SKYLENS | DELAY-CAUSE RECONCILIATION VALIDATION")
print("=" * 65)

result = con.execute("""
    SELECT
        COUNT(*) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
        ) AS populated_cause_totals,

        COUNT(*) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
              AND arrival_delay_minutes_new IS NOT NULL
        ) AS comparable_records,

        COUNT(*) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
              AND arrival_delay_minutes_new IS NOT NULL
              AND ABS(
                  delay_cause_total_minutes -
                  arrival_delay_minutes_new
              ) > 0.000001
        ) AS mismatches,

        AVG(
            delay_cause_total_minutes -
            arrival_delay_minutes_new
        ) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
              AND arrival_delay_minutes_new IS NOT NULL
        ) AS average_difference,

        MIN(
            delay_cause_total_minutes -
            arrival_delay_minutes_new
        ) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
              AND arrival_delay_minutes_new IS NOT NULL
        ) AS minimum_difference,

        MAX(
            delay_cause_total_minutes -
            arrival_delay_minutes_new
        ) FILTER (
            WHERE delay_cause_total_minutes IS NOT NULL
              AND arrival_delay_minutes_new IS NOT NULL
        ) AS maximum_difference

    FROM read_parquet(?)
""", [str(PARQUET_FILE)]).fetchone()

print(f"\nPopulated cause totals: {result[0]:,}")
print(f"Comparable records:     {result[1]:,}")
print(f"Mismatches:             {result[2]:,}")
print(f"Average difference:     {result[3]}")
print(f"Minimum difference:     {result[4]}")
print(f"Maximum difference:     {result[5]}")

print("\nValidation completed.")

con.close()
