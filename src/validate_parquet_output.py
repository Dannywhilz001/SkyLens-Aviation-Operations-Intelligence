
from pathlib import Path
import duckdb

# Locate the project and transformed Parquet file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "fact_flights.parquet"

print("=" * 65)
print("SKYLENS | INDEPENDENT PARQUET VALIDATION")
print("=" * 65)

if not PARQUET_FILE.exists():
    raise FileNotFoundError(f"Parquet file not found: {PARQUET_FILE}")

con = duckdb.connect(database=":memory:")

# 1. Verify the Parquet file can be read
total_records = con.execute(
    "SELECT COUNT(*) FROM read_parquet(?)",
    [str(PARQUET_FILE)]
).fetchone()[0]

total_columns = len(con.execute(
    "DESCRIBE SELECT * FROM read_parquet(?)",
    [str(PARQUET_FILE)]
).fetchall())

print(f"\nTotal records: {total_records:,}")
print(f"Total columns: {total_columns}")

# 2. Check date coverage
date_summary = con.execute("""
    SELECT
        MIN(flight_date),
        MAX(flight_date),
        COUNT(DISTINCT flight_date)
    FROM read_parquet(?)
""", [str(PARQUET_FILE)]).fetchone()

print("\n--- DATE COVERAGE ---")
print(f"Earliest flight date: {date_summary[0]}")
print(f"Latest flight date:   {date_summary[1]}")
print(f"Unique flight dates:  {date_summary[2]}")

# 3. Check missing values in important fields
print("\n--- KEY FIELD MISSING VALUES ---")

key_fields = [
    "flight_date",
    "carrier_code",
    "origin",
    "destination",
    "cancelled",
    "diverted",
    "departure_delay_status",
    "arrival_delay_status",
]

for field in key_fields:
    missing = con.execute(
        f"SELECT COUNT(*) FROM read_parquet(?) WHERE {field} IS NULL",
        [str(PARQUET_FILE)]
    ).fetchone()[0]

    print(f"{field:<30} {missing:,}")

# 4. Check derived delay statuses
print("\n--- DEPARTURE DELAY STATUS ---")
departure_status = con.execute("""
    SELECT departure_delay_status, COUNT(*)
    FROM read_parquet(?)
    GROUP BY departure_delay_status
    ORDER BY departure_delay_status
""", [str(PARQUET_FILE)]).fetchall()

for status, count in departure_status:
    print(f"{str(status):<20} {count:,}")

print("\n--- ARRIVAL DELAY STATUS ---")
arrival_status = con.execute("""
    SELECT arrival_delay_status, COUNT(*)
    FROM read_parquet(?)
    GROUP BY arrival_delay_status
    ORDER BY arrival_delay_status
""", [str(PARQUET_FILE)]).fetchall()

for status, count in arrival_status:
    print(f"{str(status):<20} {count:,}")

# 5. Check consistency flags
print("\n--- CONSISTENCY FLAGS ---")

for field in [
    "departure_delay_consistency_flag",
    "arrival_delay_consistency_flag",
]:
    print(f"\n{field}")

    results = con.execute(
        f"""
        SELECT {field}, COUNT(*)
        FROM read_parquet(?)
        GROUP BY {field}
        ORDER BY {field}
        """,
        [str(PARQUET_FILE)]
    ).fetchall()

    for flag, count in results:
        print(f"{str(flag):<25} {count:,}")

# 6. Check extreme arrival delays
extreme_count = con.execute("""
    SELECT COUNT(*)
    FROM read_parquet(?)
    WHERE is_extreme_arrival_delay = TRUE
""", [str(PARQUET_FILE)]).fetchone()[0]

print("\n--- EXTREME ARRIVAL DELAYS ---")
print(f"Records flagged: {extreme_count:,}")

print("\nValidation script completed.")
print("No source files were modified.")

con.close()
