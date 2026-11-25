
"""Validate recorded delays against 24-hour clock differences."""

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
            TRY_CAST(CRS_DEP_TIME AS INTEGER) AS sched_dep,
            TRY_CAST(DEP_TIME AS INTEGER) AS actual_dep,
            TRY_CAST(DEP_DELAY AS DOUBLE) AS dep_delay,

            TRY_CAST(CRS_ARR_TIME AS INTEGER) AS sched_arr,
            TRY_CAST(ARR_TIME AS INTEGER) AS actual_arr,
            TRY_CAST(ARR_DELAY AS DOUBLE) AS arr_delay
        FROM flights
    ),

    converted AS (
        SELECT
            *,

            CASE
                WHEN sched_dep = 2400 THEN 0
                ELSE FLOOR(sched_dep / 100.0) * 60
                     + sched_dep % 100
            END AS sched_dep_min,

            CASE
                WHEN actual_dep = 2400 THEN 0
                ELSE FLOOR(actual_dep / 100.0) * 60
                     + actual_dep % 100
            END AS actual_dep_min,

            CASE
                WHEN sched_arr = 2400 THEN 0
                ELSE FLOOR(sched_arr / 100.0) * 60
                     + sched_arr % 100
            END AS sched_arr_min,

            CASE
                WHEN actual_arr = 2400 THEN 0
                ELSE FLOOR(actual_arr / 100.0) * 60
                     + actual_arr % 100
            END AS actual_arr_min

        FROM parsed
    ),

    checks AS (
        SELECT
            'DEPARTURE' AS check_type,

            ((actual_dep_min - sched_dep_min + 1440) % 1440)
                AS clock_difference,

            ((CAST(ROUND(dep_delay) AS BIGINT) % 1440 + 1440) % 1440)
                AS recorded_difference

        FROM converted
        WHERE dep_delay IS NOT NULL
          AND sched_dep IS NOT NULL
          AND actual_dep IS NOT NULL
          AND (
              sched_dep = 2400 OR
              (sched_dep BETWEEN 0 AND 2359
               AND sched_dep % 100 < 60
               AND FLOOR(sched_dep / 100.0) < 24)
          )
          AND (
              actual_dep = 2400 OR
              (actual_dep BETWEEN 0 AND 2359
               AND actual_dep % 100 < 60
               AND FLOOR(actual_dep / 100.0) < 24)
          )

        UNION ALL

        SELECT
            'ARRIVAL' AS check_type,

            ((actual_arr_min - sched_arr_min + 1440) % 1440)
                AS clock_difference,

            ((CAST(ROUND(arr_delay) AS BIGINT) % 1440 + 1440) % 1440)
                AS recorded_difference

        FROM converted
        WHERE arr_delay IS NOT NULL
          AND sched_arr IS NOT NULL
          AND actual_arr IS NOT NULL
          AND (
              sched_arr = 2400 OR
              (sched_arr BETWEEN 0 AND 2359
               AND sched_arr % 100 < 60
               AND FLOOR(sched_arr / 100.0) < 24)
          )
          AND (
              actual_arr = 2400 OR
              (actual_arr BETWEEN 0 AND 2359
               AND actual_arr % 100 < 60
               AND FLOOR(actual_arr / 100.0) < 24)
          )
    )

    SELECT
        check_type,
        COUNT(*) AS records_checked,
        COUNT(*) FILTER (
            WHERE clock_difference = recorded_difference
        ) AS exact_matches,
        COUNT(*) FILTER (
            WHERE clock_difference <> recorded_difference
        ) AS mismatches
    FROM checks
    GROUP BY check_type
    ORDER BY check_type;
    """

    results = con.execute(query).fetchdf()

    print("=" * 70)
    print("SKYLENS | CLOCK-TIME CONSISTENCY VALIDATION")
    print("=" * 70)
    print(results.to_string(index=False))

    con.close()

    print("\nValidation complete. Raw data was not modified.")


if __name__ == "__main__":
    main()
