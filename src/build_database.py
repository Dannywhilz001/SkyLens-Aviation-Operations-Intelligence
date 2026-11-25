
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "fact_flights.parquet"
DATABASE_DIR = PROJECT_ROOT / "data" / "database"
DATABASE_FILE = DATABASE_DIR / "skylens.duckdb"

print("=" * 65)
print("SKYLENS | DATABASE INITIALISATION")
print("=" * 65)

if not PARQUET_FILE.exists():
    raise FileNotFoundError(f"Parquet file not found: {PARQUET_FILE}")

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Protect any existing database from accidental overwriting
if DATABASE_FILE.exists():
    raise FileExistsError(
        f"Database already exists: {DATABASE_FILE}\n"
        "No existing database was modified."
    )

con = duckdb.connect(str(DATABASE_FILE))

print("\nCreating fact_flights table...")

con.execute("""
    CREATE TABLE fact_flights AS
    SELECT *
    FROM read_parquet(?)
""", [str(PARQUET_FILE)])

record_count = con.execute("""
    SELECT COUNT(*) FROM fact_flights
""").fetchone()[0]

column_count = len(con.execute("""
    DESCRIBE fact_flights
""").fetchall())

print("\n--- DATABASE SUMMARY ---")
print(f"Database: {DATABASE_FILE}")
print(f"Table: fact_flights")
print(f"Records: {record_count:,}")
print(f"Columns: {column_count}")

print("\n--- SAMPLE RECORDS ---")

sample = con.execute("""
    SELECT
        flight_date,
        carrier_code,
        origin,
        destination,
        arrival_delay_minutes,
        arrival_delay_status
    FROM fact_flights
    LIMIT 5
""").fetchall()

for row in sample:
    print(row)

con.close()

print("\nDatabase created successfully.")
