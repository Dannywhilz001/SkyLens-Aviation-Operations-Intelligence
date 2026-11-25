
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 100)
print("SKYLENS | DAILY FLIGHT PERFORMANCE ANALYSIS")
print("=" * 100)

query = """
    SELECT
        flight_date,

        COUNT(*) AS total_flights,

        COUNT(arrival_delayed_15) AS evaluated_arrivals,

        COUNT(*) FILTER (
            WHERE arrival_delayed_15 = 1
        ) AS delayed_arrivals,

        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE arrival_delayed_15 = 1
            ) / NULLIF(COUNT(arrival_delayed_15), 0),
            2
        ) AS arrival_delay_rate_pct,

        COUNT(*) FILTER (
            WHERE cancelled = 1
        ) AS cancelled_flights,

        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE cancelled = 1
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS cancellation_rate_pct,

        ROUND(
            AVG(arrival_delay_minutes),
            2
        ) AS average_arrival_delay_minutes

    FROM fact_flights

    GROUP BY flight_date

    ORDER BY flight_date
"""

results = con.execute(query).fetchall()

print("\n--- DAILY PERFORMANCE ---\n")

header = (
    f"{'Date':<13}"
    f"{'Flights':>11}"
    f"{'Evaluated':>12}"
    f"{'Delayed':>11}"
    f"{'Delay Rate':>13}"
    f"{'Cancelled':>12}"
    f"{'Cancel Rate':>13}"
    f"{'Avg Delay':>12}"
)

print(header)
print("-" * len(header))

for row in results:
    date, flights, evaluated, delayed, delay_rate, cancelled, cancel_rate, avg_delay = row

    print(
        f"{str(date):<13}"
        f"{flights:>11,}"
        f"{evaluated:>12,}"
        f"{delayed:>11,}"
        f"{delay_rate:>12.2f}%"
        f"{cancelled:>12,}"
        f"{cancel_rate:>12.2f}%"
        f"{avg_delay:>12.2f}"
    )

print(f"\nDays analyzed: {len(results)}")
print("\nDaily performance analysis completed.")

con.close()
