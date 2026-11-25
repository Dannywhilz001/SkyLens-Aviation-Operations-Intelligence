
"""Investigate BTS delay-cause reporting patterns."""

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

    print("=" * 70)
    print("SKYLENS | DELAY-CAUSE REPORTING INVESTIGATION")
    print("=" * 70)

    # 1. Departure delay status
    print("\n--- DEPARTURE DELAY STATUS ---")
    print(
        con.execute("""
            SELECT DEP_DEL15, COUNT(*)
            FROM flights
            GROUP BY DEP_DEL15
            ORDER BY DEP_DEL15
        """).fetchdf().to_string(index=False)
    )

    # 2. Arrival delay status
    print("\n--- ARRIVAL DELAY STATUS ---")
    print(
        con.execute("""
            SELECT ARR_DEL15, COUNT(*)
            FROM flights
            GROUP BY ARR_DEL15
            ORDER BY ARR_DEL15
        """).fetchdf().to_string(index=False)
    )

    # 3. Delay-cause availability by arrival delay status
    print("\n--- DELAY-CAUSE AVAILABILITY BY ARRIVAL DELAY STATUS ---")
    print(
        con.execute("""
            SELECT
                ARR_DEL15,
                COUNT(*) AS total_records,
                COUNT(CARRIER_DELAY) AS carrier_delay_present,
                COUNT(WEATHER_DELAY) AS weather_delay_present,
                COUNT(NAS_DELAY) AS nas_delay_present,
                COUNT(SECURITY_DELAY) AS security_delay_present,
                COUNT(LATE_AIRCRAFT_DELAY) AS late_aircraft_delay_present
            FROM flights
            GROUP BY ARR_DEL15
            ORDER BY ARR_DEL15
        """).fetchdf().to_string(index=False)
    )

    # 4. Delay-cause availability by departure delay status
    print("\n--- DELAY-CAUSE AVAILABILITY BY DEPARTURE DELAY STATUS ---")
    print(
        con.execute("""
            SELECT
                DEP_DEL15,
                COUNT(*) AS total_records,
                COUNT(CARRIER_DELAY) AS carrier_delay_present,
                COUNT(WEATHER_DELAY) AS weather_delay_present,
                COUNT(NAS_DELAY) AS nas_delay_present,
                COUNT(SECURITY_DELAY) AS security_delay_present,
                COUNT(LATE_AIRCRAFT_DELAY) AS late_aircraft_delay_present
            FROM flights
            GROUP BY DEP_DEL15
            ORDER BY DEP_DEL15
        """).fetchdf().to_string(index=False)
    )

    # 5. Cancellation and delay-cause availability
    print("\n--- CANCELLATION AND DELAY-CAUSE AVAILABILITY ---")
    print(
        con.execute("""
            SELECT
                CANCELLED,
                COUNT(*) AS total_records,
                COUNT(CARRIER_DELAY) AS carrier_delay_present,
                COUNT(WEATHER_DELAY) AS weather_delay_present
            FROM flights
            GROUP BY CANCELLED
            ORDER BY CANCELLED
        """).fetchdf().to_string(index=False)
    )

    # 6. Delay-cause values on records where all five are populated
    print("\n--- COMPLETE DELAY-CAUSE RECORDS ---")
    print(
        con.execute("""
            SELECT COUNT(*) AS records_with_all_five_causes
            FROM flights
            WHERE CARRIER_DELAY IS NOT NULL
              AND WEATHER_DELAY IS NOT NULL
              AND NAS_DELAY IS NOT NULL
              AND SECURITY_DELAY IS NOT NULL
              AND LATE_AIRCRAFT_DELAY IS NOT NULL
        """).fetchdf().to_string(index=False)
    )

    con.close()
    print("\nInvestigation complete. No source data was modified.")


if __name__ == "__main__":
    main()
