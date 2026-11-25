
"""Transform raw BTS flight records into a cleaned SkyLens dataset."""

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "T_ONTIME_REPORTING.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "fact_flights.parquet"

DELAY_CAUSES = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(database=":memory:")

    file_path = str(RAW_FILE).replace("\\", "/").replace("'", "''")
    output_path = str(OUTPUT_FILE).replace("\\", "/").replace("'", "''")

    con.execute(f"""
    CREATE VIEW raw_flights AS
    SELECT *
    FROM read_csv_auto(
        '{file_path}',
        types = {{'FL_DATE': 'VARCHAR'}}
    )
""")
    # Convert and rename source fields.
    con.execute("""
        CREATE TABLE fact_flights AS

        WITH source AS (
            SELECT
                CAST(TRY_STRPTIME(FL_DATE, '%m/%d/%Y %I:%M:%S %p') AS DATE) AS flight_date,

                OP_UNIQUE_CARRIER AS carrier_code,
                OP_CARRIER AS reporting_carrier_code,
                TRY_CAST(OP_CARRIER_AIRLINE_ID AS BIGINT) AS carrier_id,
                TRY_CAST(OP_CARRIER_FL_NUM AS BIGINT) AS flight_number,

                TRY_CAST(ORIGIN_AIRPORT_ID AS BIGINT)
                    AS origin_airport_id,
                ORIGIN AS origin,
                ORIGIN_CITY_NAME AS origin_city,
                ORIGIN_STATE_NM AS origin_state,

                TRY_CAST(DEST_AIRPORT_ID AS BIGINT)
                    AS destination_airport_id,
                DEST AS destination,
                DEST_CITY_NAME AS destination_city,
                DEST_STATE_NM AS destination_state,

                TRY_CAST(CRS_DEP_TIME AS INTEGER)
                    AS scheduled_departure,
                TRY_CAST(DEP_TIME AS INTEGER)
                    AS actual_departure,
                TRY_CAST(DEP_DELAY AS DOUBLE)
                    AS departure_delay_minutes,
                TRY_CAST(DEP_DELAY_NEW AS DOUBLE)
                    AS departure_delay_minutes_new,
                TRY_CAST(DEP_DEL15 AS INTEGER)
                    AS departure_delayed_15,

                TRY_CAST(CRS_ARR_TIME AS INTEGER)
                    AS scheduled_arrival,
                TRY_CAST(ARR_TIME AS INTEGER)
                    AS actual_arrival,
                TRY_CAST(ARR_DELAY AS DOUBLE)
                    AS arrival_delay_minutes,
                TRY_CAST(ARR_DELAY_NEW AS DOUBLE)
                    AS arrival_delay_minutes_new,
                TRY_CAST(ARR_DEL15 AS INTEGER)
                    AS arrival_delayed_15,

                TRY_CAST(TAXI_OUT AS DOUBLE) AS taxi_out_minutes,
                TRY_CAST(TAXI_IN AS DOUBLE) AS taxi_in_minutes,

                TRY_CAST(CRS_ELAPSED_TIME AS DOUBLE)
                    AS scheduled_elapsed_minutes,
                TRY_CAST(ACTUAL_ELAPSED_TIME AS DOUBLE)
                    AS actual_elapsed_minutes,
                TRY_CAST(AIR_TIME AS DOUBLE) AS air_time_minutes,
                TRY_CAST(DISTANCE AS DOUBLE) AS distance_miles,

                TRY_CAST(CANCELLED AS INTEGER) AS cancelled,
                CANCELLATION_CODE AS cancellation_code,
                TRY_CAST(DIVERTED AS INTEGER) AS diverted,
                TRY_CAST(FLIGHTS AS DOUBLE) AS flights,

                TRY_CAST(CARRIER_DELAY AS DOUBLE)
                    AS carrier_delay_minutes,
                TRY_CAST(WEATHER_DELAY AS DOUBLE)
                    AS weather_delay_minutes,
                TRY_CAST(NAS_DELAY AS DOUBLE)
                    AS nas_delay_minutes,
                TRY_CAST(SECURITY_DELAY AS DOUBLE)
                    AS security_delay_minutes,
                TRY_CAST(LATE_AIRCRAFT_DELAY AS DOUBLE)
                    AS late_aircraft_delay_minutes

            FROM raw_flights
        ),

        clock_values AS (
            SELECT
                *,

                CASE
                    WHEN scheduled_departure = 2400 THEN 0
                    WHEN scheduled_departure BETWEEN 0 AND 2359
                         AND scheduled_departure % 100 < 60
                    THEN FLOOR(scheduled_departure / 100.0) * 60
                         + scheduled_departure % 100
                    ELSE NULL
                END AS scheduled_departure_minutes_of_day,

                CASE
                    WHEN actual_departure = 2400 THEN 0
                    WHEN actual_departure BETWEEN 0 AND 2359
                         AND actual_departure % 100 < 60
                    THEN FLOOR(actual_departure / 100.0) * 60
                         + actual_departure % 100
                    ELSE NULL
                END AS actual_departure_minutes_of_day,

                CASE
                    WHEN scheduled_arrival = 2400 THEN 0
                    WHEN scheduled_arrival BETWEEN 0 AND 2359
                         AND scheduled_arrival % 100 < 60
                    THEN FLOOR(scheduled_arrival / 100.0) * 60
                         + scheduled_arrival % 100
                    ELSE NULL
                END AS scheduled_arrival_minutes_of_day,

                CASE
                    WHEN actual_arrival = 2400 THEN 0
                    WHEN actual_arrival BETWEEN 0 AND 2359
                         AND actual_arrival % 100 < 60
                    THEN FLOOR(actual_arrival / 100.0) * 60
                         + actual_arrival % 100
                    ELSE NULL
                END AS actual_arrival_minutes_of_day

            FROM source
        ),

        enriched AS (
            SELECT
                *,

                CASE
                    WHEN departure_delayed_15 = 1 THEN 'Delayed'
                    WHEN departure_delayed_15 = 0 THEN 'Not Delayed'
                    ELSE 'Unknown'
                END AS departure_delay_status,

                CASE
                    WHEN arrival_delayed_15 = 1 THEN 'Delayed'
                    WHEN arrival_delayed_15 = 0 THEN 'Not Delayed'
                    ELSE 'Unknown'
                END AS arrival_delay_status,

                CASE
                    WHEN carrier_delay_minutes IS NOT NULL
                     AND weather_delay_minutes IS NOT NULL
                     AND nas_delay_minutes IS NOT NULL
                     AND security_delay_minutes IS NOT NULL
                     AND late_aircraft_delay_minutes IS NOT NULL
                    THEN carrier_delay_minutes
                       + weather_delay_minutes
                       + nas_delay_minutes
                       + security_delay_minutes
                       + late_aircraft_delay_minutes
                    ELSE NULL
                END AS delay_cause_total_minutes,

                CASE
                    WHEN departure_delay_minutes IS NULL
                      OR scheduled_departure_minutes_of_day IS NULL
                      OR actual_departure_minutes_of_day IS NULL
                    THEN 'Not Checkable'

                    WHEN (
                        (actual_departure_minutes_of_day
                         - scheduled_departure_minutes_of_day + 1440) % 1440
                    ) = (
                        (CAST(ROUND(departure_delay_minutes) AS BIGINT)
                         % 1440 + 1440) % 1440
                    )
                    THEN 'Pass'

                    ELSE 'Exception'
                END AS departure_delay_consistency_flag,

                CASE
                    WHEN arrival_delay_minutes IS NULL
                      OR scheduled_arrival_minutes_of_day IS NULL
                      OR actual_arrival_minutes_of_day IS NULL
                    THEN 'Not Checkable'

                    WHEN (
                        (actual_arrival_minutes_of_day
                         - scheduled_arrival_minutes_of_day + 1440) % 1440
                    ) = (
                        (CAST(ROUND(arrival_delay_minutes) AS BIGINT)
                         % 1440 + 1440) % 1440
                    )
                    THEN 'Pass'

                    ELSE 'Exception'
                END AS arrival_delay_consistency_flag,

                CASE
                    WHEN arrival_delay_minutes > 1440 THEN TRUE
                    ELSE FALSE
                END AS is_extreme_arrival_delay

            FROM clock_values
        )

        SELECT
            * EXCLUDE (
                scheduled_departure_minutes_of_day,
                actual_departure_minutes_of_day,
                scheduled_arrival_minutes_of_day,
                actual_arrival_minutes_of_day
            )
        FROM enriched
    """)

    # Export the transformed table to Parquet.
    con.execute(f"""
        COPY fact_flights
        TO '{output_path}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    row_count = con.execute(
        "SELECT COUNT(*) FROM fact_flights"
    ).fetchone()[0]

    column_count = len(
        con.execute("DESCRIBE fact_flights").fetchall()
    )

    print("=" * 65)
    print("SKYLENS | FLIGHT DATA TRANSFORMATION")
    print("=" * 65)
    print(f"Source records: {row_count:,}")
    print(f"Output records: {row_count:,}")
    print(f"Output columns: {column_count}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nTransformation completed successfully.")
    print("Original raw CSV was not modified.")

    con.close()


if __name__ == "__main__":
    main()
