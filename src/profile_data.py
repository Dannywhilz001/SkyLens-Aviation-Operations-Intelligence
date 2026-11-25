
"""Profile BTS flight data for quality issues without modifying raw files."""

from __future__ import annotations

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "T_ONTIME_REPORTING.csv"


def main() -> None:
    if not RAW_FILE.exists():
        print(f"File not found: {RAW_FILE}")
        return

    con = duckdb.connect(database=":memory:")

    file_path = str(RAW_FILE).replace("\\", "/").replace("'", "''")
    con.execute(
        f"CREATE VIEW flights AS SELECT * FROM read_csv_auto('{file_path}')"
    )

    print("=" * 60)
    print("SKYLENS AVIATION INTELLIGENCE")
    print("DATA QUALITY PROFILE")
    print("=" * 60)

    # 1. Dataset size
    total = con.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    print(f"\nTotal records: {total:,}")

    # 2. Missing values
    print("\n--- MISSING VALUES ---")
    columns = [
        "FL_DATE", "OP_UNIQUE_CARRIER", "ORIGIN", "DEST",
        "DEP_DELAY", "ARR_DELAY", "AIR_TIME", "DISTANCE",
        "CANCELLED", "DIVERTED", "CARRIER_DELAY",
        "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY",
        "LATE_AIRCRAFT_DELAY"
    ]

    for column in columns:
        count = con.execute(
            f'SELECT COUNT(*) FROM flights WHERE "{column}" IS NULL'
        ).fetchone()[0]
        percentage = (count / total) * 100 if total else 0
        print(f"{column}: {count:,} missing ({percentage:.2f}%)")

    # 3. Cancellation distribution
    print("\n--- CANCELLATION DISTRIBUTION ---")
    result = con.execute(
        "SELECT CANCELLED, COUNT(*) FROM flights "
        "GROUP BY CANCELLED ORDER BY CANCELLED"
    ).fetchall()

    for value, count in result:
        print(f"Cancelled = {value}: {count:,}")

    # 4. Diversion distribution
    print("\n--- DIVERSION DISTRIBUTION ---")
    result = con.execute(
        "SELECT DIVERTED, COUNT(*) FROM flights "
        "GROUP BY DIVERTED ORDER BY DIVERTED"
    ).fetchall()

    for value, count in result:
        print(f"Diverted = {value}: {count:,}")

    # 5. Delay-cause missingness by cancellation status
    print("\n--- DELAY-CAUSE MISSINGNESS BY CANCELLATION ---")
    result = con.execute("""
        SELECT
            CANCELLED,
            COUNT(*) AS total_flights,
            COUNT(CARRIER_DELAY) AS carrier_delay_present,
            COUNT(WEATHER_DELAY) AS weather_delay_present,
            COUNT(NAS_DELAY) AS nas_delay_present,
            COUNT(SECURITY_DELAY) AS security_delay_present,
            COUNT(LATE_AIRCRAFT_DELAY) AS late_aircraft_delay_present
        FROM flights
        GROUP BY CANCELLED
        ORDER BY CANCELLED
    """).fetchall()

    for row in result:
        print(row)

    # 6. Basic numerical checks
    print("\n--- BASIC NUMERICAL CHECKS ---")

    checks = {
        "Negative distance": "DISTANCE < 0",
        "Zero distance": "DISTANCE = 0",
        "Negative air time": "AIR_TIME < 0",
        "Negative scheduled elapsed time": "CRS_ELAPSED_TIME < 0",
        "Negative actual elapsed time": "ACTUAL_ELAPSED_TIME < 0",
    }

    for label, condition in checks.items():
        count = con.execute(
            f"SELECT COUNT(*) FROM flights WHERE {condition}"
        ).fetchone()[0]
        print(f"{label}: {count:,}")

    # 7. Date coverage
    print("\n--- DATE COVERAGE ---")
    result = con.execute(
        "SELECT MIN(FL_DATE), MAX(FL_DATE), COUNT(DISTINCT FL_DATE) "
        "FROM flights"
    ).fetchone()

    print(f"Earliest date: {result[0]}")
    print(f"Latest date: {result[1]}")
    print(f"Unique dates: {result[2]}")

    con.close()

    print("\nProfiling complete. Raw source data remains unchanged.")


if __name__ == "__main__":
    main()
