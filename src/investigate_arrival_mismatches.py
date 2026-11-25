
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

    query = """
    WITH parsed AS (
        SELECT
            *,
            TRY_CAST(CRS_ARR_TIME AS INTEGER) AS scheduled_time,
            TRY_CAST(ARR_TIME AS INTEGER) AS actual_time,
            TRY_CAST(ARR_DELAY AS DOUBLE) AS recorded_delay
        FROM flights
    ),

    converted AS (
        SELECT
            *,
            CASE
                WHEN scheduled_time = 2400 THEN 0
                ELSE FLOOR(scheduled_time / 100.0) * 60
                     + scheduled_time % 100
            END AS scheduled_minutes,

            CASE
                WHEN actual_time = 2400 THEN 0
                ELSE FLOOR(actual_time / 100.0) * 60
                     + actual_time % 100
            END AS actual_minutes
        FROM parsed
    )

    SELECT
        FL_DATE,
        OP_UNIQUE_CARRIER,
        OP_CARRIER_FL_NUM,
        ORIGIN,
        DEST,
        CRS_ARR_TIME,
        ARR_TIME,
        ARR_DELAY,
        ARR_DELAY_NEW,
        CANCELLED,
        DIVERTED,
        (actual_minutes - scheduled_minutes + 1440) % 1440
            AS clock_difference,
        recorded_delay % 1440 AS recorded_difference
    FROM converted
    WHERE recorded_delay IS NOT NULL
      AND scheduled_time IS NOT NULL
      AND actual_time IS NOT NULL
      AND scheduled_time BETWEEN 0 AND 2400
      AND actual_time BETWEEN 0 AND 2400
      AND scheduled_time % 100 < 60
      AND actual_time % 100 < 60
      AND scheduled_time <> 2400
          OR FALSE
    """

    # Apply the same clock-time comparison used in the validation.
    query = query.replace(
        "AND scheduled_time <> 2400\n          OR FALSE",
        """
        AND (
            scheduled_time = 2400 OR
            scheduled_time BETWEEN 0 AND 2359
        )
        AND (
            actual_time = 2400 OR
            actual_time BETWEEN 0 AND 2359
        )
        AND (
            (actual_minutes - scheduled_minutes + 1440) % 1440
        ) <> (
            (CAST(ROUND(recorded_delay) AS BIGINT) % 1440 + 1440) % 1440
        )
        ORDER BY FL_DATE
        """
    )

    result = con.execute(query).fetchdf()

    print("=" * 75)
    print("SKYLENS | ARRIVAL MISMATCH INVESTIGATION")
    print("=" * 75)
    print(result.to_string(index=False))

    con.close()
    print("\nInvestigation complete. Raw data was not modified.")


if __name__ == "__main__":
    main()
