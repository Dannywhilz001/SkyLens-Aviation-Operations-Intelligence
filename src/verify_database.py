
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

print("=" * 65)
print("SKYLENS | DATABASE INTEGRITY CHECK")
print("=" * 65)

if not DATABASE_FILE.exists():
    raise FileNotFoundError("SkyLens database does not exist.")

# Open the existing database independently
con = duckdb.connect(str(DATABASE_FILE), read_only=True)

# Confirm the table exists
tables = con.execute("""
    SHOW TABLES
""").fetchall()

print("\n--- DATABASE TABLES ---")
for table in tables:
    print(table[0])

# Verify the main fact table
record_count = con.execute("""
    SELECT COUNT(*)
    FROM fact_flights
""").fetchone()[0]

print(f"\nFlight records: {record_count:,}")

# Check distinct carriers
carrier_count = con.execute("""
    SELECT COUNT(DISTINCT carrier_code)
    FROM fact_flights
""").fetchone()[0]

print(f"Distinct carriers: {carrier_count}")

# Check distinct origin and destination airports
airport_count = con.execute("""
    SELECT COUNT(DISTINCT airport)
    FROM (
        SELECT origin AS airport FROM fact_flights
        UNION
        SELECT destination AS airport FROM fact_flights
    )
""").fetchone()[0]

print(f"Distinct airports: {airport_count}")

# Check date range
date_range = con.execute("""
    SELECT MIN(flight_date), MAX(flight_date)
    FROM fact_flights
""").fetchone()

print(f"Date range: {date_range[0]} to {date_range[1]}")

con.close()

print("\nDatabase integrity check completed.")
