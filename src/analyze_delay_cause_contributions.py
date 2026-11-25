
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 100)
print("SKYLENS | DELAY CAUSE CONTRIBUTION ANALYSIS")
print("=" * 100)

query = """
    WITH cause_data AS (

        SELECT
            'Carrier Delay' AS cause,
            carrier_delay_minutes AS delay_minutes
        FROM fact_flights
        WHERE arrival_delayed_15 = 1

        UNION ALL

        SELECT
            'Late Aircraft Delay',
            late_aircraft_delay_minutes
        FROM fact_flights
        WHERE arrival_delayed_15 = 1

        UNION ALL

        SELECT
            'NAS Delay',
            nas_delay_minutes
        FROM fact_flights
        WHERE arrival_delayed_15 = 1

        UNION ALL

        SELECT
            'Weather Delay',
            weather_delay_minutes
        FROM fact_flights
        WHERE arrival_delayed_15 = 1

        UNION ALL

        SELECT
            'Security Delay',
            security_delay_minutes
        FROM fact_flights
        WHERE arrival_delayed_15 = 1
    ),

    cause_summary AS (
        SELECT
            cause,
            COUNT(delay_minutes) AS populated_records,
            SUM(delay_minutes) AS total_delay_minutes,
            AVG(delay_minutes) AS average_delay_minutes
        FROM cause_data
        WHERE delay_minutes IS NOT NULL
        GROUP BY cause
    )

    SELECT
        cause,
        populated_records,
        ROUND(total_delay_minutes, 2) AS total_delay_minutes,
        ROUND(average_delay_minutes, 2) AS average_delay_minutes,

        ROUND(
            100.0 * total_delay_minutes /
            NULLIF(SUM(total_delay_minutes) OVER (), 0),
            2
        ) AS contribution_pct

    FROM cause_summary
    ORDER BY total_delay_minutes DESC
"""

results = con.execute(query).fetchall()

print("\n--- DELAY CAUSE BREAKDOWN ---\n")

header = (
    f"{'Cause':<25}"
    f"{'Records':>13}"
    f"{'Total Minutes':>18}"
    f"{'Average Minutes':>19}"
    f"{'Contribution':>16}"
)

print(header)
print("-" * len(header))

for row in results:
    cause, records, total, average, contribution = row

    print(
        f"{cause:<25}"
        f"{records:>13,}"
        f"{total:>18,.2f}"
        f"{average:>19,.2f}"
        f"{contribution:>15.2f}%"
    )

print("\nDelay cause contribution analysis completed.")

con.close()
