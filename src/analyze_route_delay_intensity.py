
import duckdb

DB_PATH = "data/database/skylens.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

query = """
SELECT
    origin,
    destination,
    origin_city,
    destination_city,

    COUNT(*) AS delayed_arrivals,

    ROUND(AVG(
        carrier_delay_minutes
        + late_aircraft_delay_minutes
        + nas_delay_minutes
        + weather_delay_minutes
        + security_delay_minutes
    ), 2) AS avg_total_delay_minutes,

    ROUND(AVG(carrier_delay_minutes), 2) AS avg_carrier_delay,
    ROUND(AVG(late_aircraft_delay_minutes), 2) AS avg_late_aircraft_delay,
    ROUND(AVG(nas_delay_minutes), 2) AS avg_nas_delay,
    ROUND(AVG(weather_delay_minutes), 2) AS avg_weather_delay,
    ROUND(AVG(security_delay_minutes), 2) AS avg_security_delay

FROM fact_flights

WHERE arrival_delayed_15 = 1

GROUP BY
    origin,
    destination,
    origin_city,
    destination_city

HAVING COUNT(*) >= 100

ORDER BY avg_total_delay_minutes DESC
"""

results = con.execute(query).fetchall()

print("=" * 110)
print("SKYLENS | ROUTE DELAY INTENSITY RANKING")
print("=" * 110)

print(
    f"\n{'Route':<12}"
    f"{'Delayed':>10}"
    f"{'Total Avg':>12}"
    f"{'Carrier':>11}"
    f"{'Late Acft':>12}"
    f"{'NAS':>10}"
    f"{'Weather':>11}"
    f"{'Security':>11}"
)

print("-" * 110)

for row in results:
    (
        origin,
        destination,
        origin_city,
        destination_city,
        delayed,
        total_avg,
        carrier_avg,
        late_avg,
        nas_avg,
        weather_avg,
        security_avg
    ) = row

    route = f"{origin}-{destination}"

    print(
        f"{route:<12}"
        f"{delayed:>10,}"
        f"{total_avg:>12.2f}"
        f"{carrier_avg:>11.2f}"
        f"{late_avg:>12.2f}"
        f"{nas_avg:>10.2f}"
        f"{weather_avg:>11.2f}"
        f"{security_avg:>11.2f}"
    )

print("-" * 110)
print(f"\nRoutes meeting minimum sample threshold: {len(results)}")
print("Minimum sample: 100 delayed arrivals per route")

print("\nRoute delay intensity analysis completed.")

con.close()
