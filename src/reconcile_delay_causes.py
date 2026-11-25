
"""Compare BTS delay-cause minutes with reported arrival delays."""

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "T_ONTIME_REPORTING.csv"

CAUSES = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]


def main():
    if not RAW_FILE.exists():
        print(f"File not found: {RAW_FILE}")
        return

    con = duckdb.connect(database=":memory:")
    file_path = str(RAW_FILE).replace("\\", "/").replace("'", "''")

    con.execute(
        f"CREATE VIEW flights AS "
        f"SELECT * FROM read_csv_auto('{file_path}')"
    )

    print("=" * 65)
    print("SKYLENS | DELAY-CAUSE RECONCILIATION")
    print("=" * 65)

    # 1. Summary statistics for each delay cause
    print("\n--- DELAY-CAUSE SUMMARY ---")

    for cause in CAUSES:
        result = con.execute(f"""
            SELECT
                COUNT({cause}),
                MIN({cause}),
                MAX({cause}),
                ROUND(AVG({cause}), 2),
                SUM({cause})
            FROM flights
            WHERE {cause} IS NOT NULL
        """).fetchone()

        print(f"\n{cause}")
        print(f"  Populated records: {result[0]:,}")
        print(f"  Minimum minutes: {result[1]}")
        print(f"  Maximum minutes: {result[2]}")
        print(f"  Average minutes: {result[3]}")
        print(f"  Total minutes: {result[4]:,.2f}")

    # 2. Check for negative cause values
    print("\n--- NEGATIVE DELAY-CAUSE VALUES ---")

    for cause in CAUSES:
        count = con.execute(f"""
            SELECT COUNT(*)
            FROM flights
            WHERE {cause} < 0
        """).fetchone()[0]

        print(f"{cause}: {count:,}")

    # 3. Compare combined causes with arrival delay
    print("\n--- ARRIVAL DELAY RECONCILIATION ---")

    cause_sum = " + ".join(CAUSES)

    result = con.execute(f"""
        WITH delayed AS (
            SELECT
                ARR_DELAY_NEW,
                ({cause_sum}) AS total_cause_minutes
            FROM flights
            WHERE ARR_DEL15 = 1
              AND ARR_DELAY_NEW IS NOT NULL
        )
        SELECT
            COUNT(*) AS delayed_records,
            COUNT(*) FILTER (
                WHERE total_cause_minutes = ARR_DELAY_NEW
            ) AS exact_matches,
            COUNT(*) FILTER (
                WHERE total_cause_minutes <> ARR_DELAY_NEW
            ) AS differences,
            ROUND(AVG(
                total_cause_minutes - ARR_DELAY_NEW
            ), 2) AS average_difference,
            MIN(total_cause_minutes - ARR_DELAY_NEW) AS minimum_difference,
            MAX(total_cause_minutes - ARR_DELAY_NEW) AS maximum_difference
        FROM delayed
    """).fetchone()

    print(f"Delayed records checked: {result[0]:,}")
    print(f"Exact matches: {result[1]:,}")
    print(f"Differences: {result[2]:,}")
    print(f"Average difference: {result[3]} minutes")
    print(f"Minimum difference: {result[4]} minutes")
    print(f"Maximum difference: {result[5]} minutes")

    # 4. Show examples where totals differ
    print("\n--- EXAMPLES OF DIFFERENCES ---")

    examples = con.execute(f"""
        SELECT
            FL_DATE,
            OP_UNIQUE_CARRIER,
            ORIGIN,
            DEST,
            ARR_DELAY_NEW,
            ({cause_sum}) AS total_cause_minutes,
            ({cause_sum}) - ARR_DELAY_NEW AS difference
        FROM flights
        WHERE ARR_DEL15 = 1
          AND ARR_DELAY_NEW IS NOT NULL
          AND ({cause_sum}) <> ARR_DELAY_NEW
        LIMIT 10
    """).fetchdf()

    if examples.empty:
        print("No differences found.")
    else:
        print(examples.to_string(index=False))

    con.close()
    print("\nReconciliation complete. Raw data was not modified.")


if __name__ == "__main__":
    main()
