
import duckdb
from statistics import median

DB_PATH = "data/database/skylens.duckdb"
MINIMUM_FLIGHTS = 300

con = duckdb.connect(DB_PATH, read_only=True)

query = """
SELECT
    origin,
    destination,
    origin_city,
    destination_city,

    COUNT(arrival_delayed_15) AS evaluated_arrivals,

    SUM(
        CASE WHEN arrival_delayed_15 = 1
        THEN 1 ELSE 0 END
    ) AS delayed_arrivals,

    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1
            THEN 1 ELSE 0 END
        ) / COUNT(arrival_delayed_15),
        2
    ) AS delay_rate,

    ROUND(
        AVG(
            CASE WHEN arrival_delayed_15 = 1 THEN
                carrier_delay_minutes
                + late_aircraft_delay_minutes
                + nas_delay_minutes
                + weather_delay_minutes
                + security_delay_minutes
            END
        ),
        2
    ) AS avg_delay_intensity

FROM fact_flights

GROUP BY
    origin,
    destination,
    origin_city,
    destination_city

HAVING COUNT(arrival_delayed_15) >= ?

ORDER BY delay_rate DESC
"""

results = con.execute(query, [MINIMUM_FLIGHTS]).fetchall()

con.close()

if not results:
    raise ValueError("No routes met the minimum flight threshold.")

# Calculate median thresholds
delay_rates = [row[6] for row in results]
delay_intensities = [row[7] for row in results]

median_delay_rate = median(delay_rates)
median_delay_intensity = median(delay_intensities)

# Classify routes
classified_routes = []

for row in results:
    (
        origin,
        destination,
        origin_city,
        destination_city,
        evaluated,
        delayed,
        delay_rate,
        intensity
    ) = row

    high_rate = delay_rate >= median_delay_rate
    high_intensity = intensity >= median_delay_intensity

    if high_rate and high_intensity:
        category = "HIGH RATE + HIGH INTENSITY"
    elif high_rate and not high_intensity:
        category = "HIGH RATE + LOW INTENSITY"
    elif not high_rate and high_intensity:
        category = "LOW RATE + HIGH INTENSITY"
    else:
        category = "LOW RATE + LOW INTENSITY"

    classified_routes.append({
        "route": f"{origin}-{destination}",
        "evaluated": evaluated,
        "delayed": delayed,
        "rate": delay_rate,
        "intensity": intensity,
        "category": category
    })

# Display thresholds
print("=" * 100)
print("SKYLENS | ROUTE PERFORMANCE CLASSIFICATION")
print("=" * 100)

print(f"\nRoutes analysed: {len(classified_routes)}")
print(f"Minimum evaluated arrivals: {MINIMUM_FLIGHTS}")
print(f"Median delay rate: {median_delay_rate:.2f}%")
print(f"Median delay intensity: {median_delay_intensity:.2f} minutes")

categories = [
    "HIGH RATE + HIGH INTENSITY",
    "HIGH RATE + LOW INTENSITY",
    "LOW RATE + HIGH INTENSITY",
    "LOW RATE + LOW INTENSITY"
]

for category in categories:
    group = [
        route for route in classified_routes
        if route["category"] == category
    ]

    print("\n" + "=" * 100)
    print(category)
    print("=" * 100)

    print(
        f"{'Route':<12}"
        f"{'Evaluated':>12}"
        f"{'Delayed':>10}"
        f"{'Delay Rate':>13}"
        f"{'Intensity':>13}"
    )

    print("-" * 60)

    # Show highest delay rates first within each group
    group.sort(
        key=lambda x: (x["rate"], x["intensity"]),
        reverse=True
    )

    for route in group[:10]:
        print(
            f"{route['route']:<12}"
            f"{route['evaluated']:>12,}"
            f"{route['delayed']:>10,}"
            f"{route['rate']:>12.2f}%"
            f"{route['intensity']:>12.2f}"
        )

    print(f"\nRoutes in this category: {len(group)}")

print("\n" + "=" * 100)
print("Route performance classification completed.")
