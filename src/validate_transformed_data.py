from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "fact_flights.parquet"

con = duckdb.connect()

print("=" * 65)
print("SKYLENS | TRANSFORMED DATA VALIDATION")
print("=" * 65)

row_count = con.execute(
    "SELECT COUNT(*) FROM read_parquet(?)",
    [str(PARQUET_FILE)]
).fetchone()[0]

print(f"\nTotal records: {row_count:,}")

schema = con.execute(
    "DESCRIBE SELECT * FROM read_parquet(?)",
    [str(PARQUET_FILE)]
).fetchall()

print(f"Total columns: {len(schema)}")

print("\n--- COLUMN NAMES AND DATA TYPES ---")

for column in schema:
    print(f"{column[0]:35} {column[1]}")

con.close()