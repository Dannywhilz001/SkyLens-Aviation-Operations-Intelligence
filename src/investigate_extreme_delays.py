"""Inspect operational details of extreme arrival delays."""

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "T_ONTIME_REPORTING.csv"


def main():
    con = duckdb.connect(database=":memory:")

    file_path = str(RAW_FILE).replace("\\", "/").replace("'", "''")

    con.execute(
        f"CREATE VIEW flights AS "
        f"SELECT * FROM read_csv_auto('{file_path}')"
    )

    result = con.execute("""
        SELECT
            FL_DATE,
            OP_UNIQUE_CARRIER,
            OP_CARRIER_FL_NUM,
            ORIGIN,
            DEST,
            CRS_DEP_TIME,
            DEP_TIME,
            DEP_DELAY,
            CRS_ARR_TIME,
            ARR_TIME,
            ARR_DELAY,
            ARR_DELAY_NEW,
            CRS_ELAPSED_TIME,
            ACTUAL_ELAPSED_TIME,
            CANCELLED,
            CANCELLATION_CODE,
            DIVERTED
        FROM flights
        WHERE ARR_DEL15 = 1
        ORDER BY ARR_DELAY_NEW DESC
        LIMIT 10
    """).fetchdf()

    print("=" * 80)
    print("SKYLENS | EXTREME FLIGHT OPERATIONAL REVIEW")
    print("=" * 80)

    print(result.to_string(index=False))

    con.close()

    print("\nReview complete. Raw data was not modified.")


if __name__ == "__main__":
    main()