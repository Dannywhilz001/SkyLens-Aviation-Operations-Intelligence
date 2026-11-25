
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 90)
print("SKYLENS | AIRPORT RELIABILITY ANALYSIS")
print("=" * 90)

query = """
    SELECT
        destination AS airport_code,
        destination_city AS airport_city,
        COUNT(*) AS total_flight_records,
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

        ROUND(AVG(arrival_delay_minutes), 2)
            AS average_arrival_delay_minutes

    FROM fact_flights

    GROUP BY destination, destination_city

    HAVING COUNT(arrival_delayed_15) >= 500

    ORDER BY arrival_delay_rate_pct DESC
"""

results = con.execute(query).fetchall()

print("\n--- DESTINATION AIRPORT PERFORMANCE ---\n")

header = (
    f"{'Airport':<10}"
    f"{'City':<25}"
    f"{'Evaluated':>12}"
    f"{'Delayed':>12}"
    f"{'On-time':>12}"
    f"{'Delay Rate':>13}"
    f"{'Avg Delay':>12}"
)

print(header)
print("-" * len(header))

for row in results:
    airport, city, total, evaluated, delayed, on_time, rate, average_delay = row

    print(
        f"{airport:<10}"
        f"{city[:24]:<25}"
        f"{evaluated:>12,}"
        f"{delayed:>12,}"
        f"{on_time:>12,}"
        f"{rate:>12.2f}%"
        f"{average_delay:>12.2f}"
    )

print(f"\nAirports meeting minimum sample requirement: {len(results)}")
print("\nAirport analysis completed.")

con.close()
