
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 115)
print("SKYLENS | AIRPORT DELAY INTENSITY ANALYSIS")
print("=" * 115)

query = """
    SELECT
        destination,
        destination_city,

        COUNT(*) AS delayed_arrivals,

        SUM(delay_cause_total_minutes) AS total_delay_minutes,

        SUM(carrier_delay_minutes) AS carrier_delay_minutes,

        SUM(late_aircraft_delay_minutes) AS late_aircraft_delay_minutes,

        SUM(nas_delay_minutes) AS nas_delay_minutes,

        SUM(weather_delay_minutes) AS weather_delay_minutes,

        SUM(security_delay_minutes) AS security_delay_minutes

    FROM fact_flights

    WHERE arrival_delayed_15 = 1

    GROUP BY destination, destination_city

    HAVING COUNT(*) >= 500

    ORDER BY
        SUM(delay_cause_total_minutes) * 1.0 / COUNT(*) DESC
"""

results = con.execute(query).fetchall()

print("\n--- AIRPORT DELAY INTENSITY RANKING ---\n")

header = (
    f"{'Airport':<10}"
    f"{'City':<27}"
    f"{'Delayed':>11}"
    f"{'Total Avg':>13}"
    f"{'Carrier Avg':>14}"
    f"{'Late Acft Avg':>16}"
    f"{'NAS Avg':>11}"
    f"{'Weather Avg':>14}"
    f"{'Security Avg':>15}"
)

print(header)
print("-" * len(header))

for row in results:
    (
        airport,
        city,
        delayed,
        total,
        carrier,
        late_aircraft,
        nas,
        weather,
        security
    ) = row

    print(
        f"{airport:<10}"
        f"{str(city)[:26]:<27}"
        f"{delayed:>11,}"
        f"{total / delayed:>13.2f}"
        f"{carrier / delayed:>14.2f}"
        f"{late_aircraft / delayed:>16.2f}"
        f"{nas / delayed:>11.2f}"
        f"{weather / delayed:>14.2f}"
        f"{security / delayed:>15.2f}"
    )

print(f"\nAirports meeting the minimum sample threshold: {len(results)}")
print("Minimum sample: 500 delayed arrivals per destination airport")

print("\nAirport delay intensity analysis completed.")

con.close()
