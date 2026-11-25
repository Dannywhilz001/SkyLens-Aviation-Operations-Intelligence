
import duckdb

DB_PATH = "data/database/skylens.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

# --------------------------------------------------
# 1. OVERALL DATASET SUMMARY
# --------------------------------------------------

overall = con.execute("""
SELECT
    COUNT(*) AS total_flights,
    MIN(flight_date) AS first_date,
    MAX(flight_date) AS last_date,
    COUNT(DISTINCT reporting_carrier_code) AS carriers,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    SUM(CASE WHEN cancelled = 1 THEN 1 ELSE 0 END)
        AS cancellations,
    SUM(CASE WHEN diverted = 1 THEN 1 ELSE 0 END)
        AS diversions,
    ROUND(AVG(arrival_delay_minutes), 2)
        AS avg_signed_arrival_delay
FROM fact_flights
""").fetchone()

total_flights = overall[0]
evaluated = overall[4]
delayed = overall[5]

delay_rate = 100 * delayed / evaluated if evaluated else 0
cancellation_rate = 100 * overall[6] / total_flights

# --------------------------------------------------
# 2. CARRIER PERFORMANCE
# --------------------------------------------------

carriers = con.execute("""
SELECT
    reporting_carrier_code,
    COUNT(*) AS total_flights,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
        2
    ) AS delay_rate,
    ROUND(AVG(arrival_delay_minutes), 2) AS avg_signed_delay
FROM fact_flights
GROUP BY reporting_carrier_code
HAVING COUNT(arrival_delayed_15) > 0
ORDER BY delay_rate DESC
""").fetchall()

# --------------------------------------------------
# 3. AIRPORT PERFORMANCE
# --------------------------------------------------

airports = con.execute("""
SELECT
    destination,
    destination_city,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
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
    ) AS delay_intensity
FROM fact_flights
GROUP BY destination, destination_city
HAVING COUNT(arrival_delayed_15) >= 500
ORDER BY delay_rate DESC
""").fetchall()

# --------------------------------------------------
# 4. ROUTE PERFORMANCE
# --------------------------------------------------

routes = con.execute("""
SELECT
    origin,
    destination,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
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
    ) AS delay_intensity
FROM fact_flights
GROUP BY origin, destination
HAVING COUNT(arrival_delayed_15) >= 300
ORDER BY delay_rate DESC
""").fetchall()

# --------------------------------------------------
# 5. DELAY CAUSE CONTRIBUTIONS
# --------------------------------------------------

causes = con.execute("""
SELECT
    ROUND(SUM(carrier_delay_minutes), 2),
    ROUND(SUM(late_aircraft_delay_minutes), 2),
    ROUND(SUM(nas_delay_minutes), 2),
    ROUND(SUM(weather_delay_minutes), 2),
    ROUND(SUM(security_delay_minutes), 2)
FROM fact_flights
WHERE arrival_delayed_15 = 1
""").fetchone()

cause_names = [
    "Carrier",
    "Late Aircraft",
    "NAS",
    "Weather",
    "Security"
]

cause_totals = list(causes)
total_cause_minutes = sum(cause_totals)

# --------------------------------------------------
# 6. DAILY PERFORMANCE
# --------------------------------------------------

daily = con.execute("""
SELECT
    flight_date,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
        2
    ) AS delay_rate
FROM fact_flights
GROUP BY flight_date
HAVING COUNT(arrival_delayed_15) > 0
ORDER BY delay_rate DESC
""").fetchall()

# --------------------------------------------------
# 7. ROUTE CLASSIFICATION
# --------------------------------------------------

from statistics import median

median_rate = median([row[4] for row in routes])
median_intensity = median([row[5] for row in routes])

classification_counts = {
    "HIGH RATE + HIGH INTENSITY": 0,
    "HIGH RATE + LOW INTENSITY": 0,
    "LOW RATE + HIGH INTENSITY": 0,
    "LOW RATE + LOW INTENSITY": 0
}

for route in routes:
    high_rate = route[4] >= median_rate
    high_intensity = route[5] >= median_intensity

    if high_rate and high_intensity:
        category = "HIGH RATE + HIGH INTENSITY"
    elif high_rate:
        category = "HIGH RATE + LOW INTENSITY"
    elif high_intensity:
        category = "LOW RATE + HIGH INTENSITY"
    else:
        category = "LOW RATE + LOW INTENSITY"

    classification_counts[category] += 1

# --------------------------------------------------
# 8. PRINT CONSOLIDATED REPORT
# --------------------------------------------------

print("\n" + "=" * 85)
print("SKYLENS | CONSOLIDATED ANALYTICAL SUMMARY")
print("=" * 85)

print("\n1. OVERALL FLIGHT PERFORMANCE")
print("-" * 85)
print(f"Total flight records:          {total_flights:,}")
print(f"Reporting period:              {overall[1]} to {overall[2]}")
print(f"Reporting carriers:            {overall[3]}")
print(f"Evaluated arrivals:            {evaluated:,}")
print(f"Delayed arrivals:              {delayed:,}")
print(f"Arrival delay rate:            {delay_rate:.2f}%")
print(f"Cancellations:                 {overall[6]:,}")
print(f"Cancellation rate:             {cancellation_rate:.2f}%")
print(f"Diverted flights:              {overall[7]:,}")
print(f"Average signed arrival delay:  {overall[8]:.2f} minutes")

print("\n2. CARRIER PERFORMANCE")
print("-" * 85)
print("Highest observed delay rates:")

for row in carriers[:5]:
    print(
        f"{row[0]:<6} | Delay rate: {row[3]:>6.2f}%"
        f" | Delayed arrivals: {row[2]:>7,}"
    )

print("\nLowest observed delay rates:")

for row in sorted(carriers, key=lambda x: x[3])[:5]:
    print(
        f"{row[0]:<6} | Delay rate: {row[3]:>6.2f}%"
        f" | Delayed arrivals: {row[2]:>7,}"
    )

print("\n3. AIRPORT PERFORMANCE")
print("-" * 85)

print("Highest airport delay rates:")
for row in airports[:5]:
    print(
        f"{row[0]:<5} | {row[1]:<28}"
        f" | Rate: {row[4]:>6.2f}%"
        f" | Evaluated: {row[2]:>6,}"
    )

print("\nHighest airport delay intensity:")
for row in sorted(airports, key=lambda x: x[5], reverse=True)[:5]:
    print(
        f"{row[0]:<5} | {row[1]:<28}"
        f" | Intensity: {row[5]:>6.2f} min"
        f" | Delayed: {row[3]:>6,}"
    )

print("\n4. ROUTE PERFORMANCE")
print("-" * 85)

print("Highest route delay rates:")
for row in routes[:5]:
    print(
        f"{row[0]}-{row[1]:<5}"
        f" | Rate: {row[4]:>6.2f}%"
        f" | Evaluated: {row[2]:>6,}"
    )

print("\nHighest route delay intensity:")
for row in sorted(routes, key=lambda x: x[5], reverse=True)[:5]:
    print(
        f"{row[0]}-{row[1]:<5}"
        f" | Intensity: {row[5]:>6.2f} min"
        f" | Delayed: {row[3]:>6,}"
    )

print("\n5. DELAY CAUSE CONTRIBUTIONS")
print("-" * 85)

for name, minutes in sorted(
    zip(cause_names, cause_totals),
    key=lambda x: x[1],
    reverse=True
):
    percentage = (
        100 * minutes / total_cause_minutes
        if total_cause_minutes else 0
    )

    print(
        f"{name:<16} | {minutes:>12,.0f} minutes"
        f" | {percentage:>6.2f}%"
    )

print(f"\nTotal recorded delay-cause minutes: {total_cause_minutes:,.0f}")

print("\n6. DAILY PERFORMANCE")
print("-" * 85)

worst_day = daily[0]
best_day = min(daily, key=lambda x: x[3])

print(
    f"Highest delay-rate day: {worst_day[0]}"
    f" | {worst_day[3]:.2f}%"
)

print(
    f"Lowest delay-rate day:  {best_day[0]}"
    f" | {best_day[3]:.2f}%"
)

print("\n7. ROUTE PERFORMANCE CLASSIFICATION")
print("-" * 85)
print(f"Routes classified:          {len(routes)}")
print(f"Median delay rate:          {median_rate:.2f}%")
print(f"Median delay intensity:     {median_intensity:.2f} minutes")

for category, count in classification_counts.items():
    print(f"{category:<32} | {count:>4} routes")

print("\n" + "=" * 85)
print("SKYLENS | ANALYTICAL SUMMARY COMPLETED")
print("=" * 85)

con.close()
