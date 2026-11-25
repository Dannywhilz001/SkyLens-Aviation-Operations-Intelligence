
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 90)
print("SKYLENS | CARRIER PERFORMANCE ANALYSIS")
print("=" * 90)

query = """
    SELECT
        reporting_carrier_code,

        COUNT(*) AS total_flight_records,

        COUNT(*) FILTER (
            WHERE cancelled = 1
        ) AS cancelled_flights,

        COUNT(*) FILTER (
            WHERE diverted = 1
        ) AS diverted_flights,

        COUNT(arrival_delayed_15) AS evaluated_arrivals,

        COUNT(*) FILTER (
            WHERE arrival_delayed_15 = 1
        ) AS delayed_arrivals,

        COUNT(*) FILTER (
            WHERE arrival_delayed_15 = 0
        ) AS on_time_arrivals,

        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE arrival_delayed_15 = 1
            ) / NULLIF(COUNT(arrival_delayed_15), 0),
            2
        ) AS arrival_delay_rate_pct,

        ROUND(
            AVG(arrival_delay_minutes),
            2
        ) AS average_arrival_delay_minutes

    FROM fact_flights

    GROUP BY reporting_carrier_code

    ORDER BY arrival_delay_rate_pct DESC
"""

results = con.execute(query).fetchall()

print("\n--- CARRIER PERFORMANCE SUMMARY ---\n")

header = (
    f"{'Carrier':<10}"
    f"{'Records':>12}"
    f"{'Cancelled':>12}"
    f"{'Diverted':>10}"
    f"{'Delayed':>12}"
    f"{'On-time':>12}"
    f"{'Delay Rate':>13}"
    f"{'Avg Delay':>12}"
)

print(header)
print("-" * len(header))

for row in results:
    (
        carrier,
        records,
        cancelled,
        diverted,
        evaluated,
        delayed,
        on_time,
        delay_rate,
        average_delay
    ) = row

    print(
        f"{carrier:<10}"
        f"{records:>12,}"
        f"{cancelled:>12,}"
        f"{diverted:>10,}"
        f"{delayed:>12,}"
        f"{on_time:>12,}"
        f"{delay_rate:>12.2f}%"
        f"{average_delay:>12.2f}"
    )

print("\nAnalysis completed.")

con.close()
