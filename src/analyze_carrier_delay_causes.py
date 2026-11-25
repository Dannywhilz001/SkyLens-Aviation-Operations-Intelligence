
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 110)
print("SKYLENS | CARRIER-LEVEL DELAY CAUSE ANALYSIS")
print("=" * 110)

query = """
    SELECT
        reporting_carrier_code,

        COUNT(*) AS total_flight_records,

        COUNT(*) FILTER (
            WHERE arrival_delayed_15 = 1
        ) AS delayed_arrivals,

        SUM(carrier_delay_minutes) AS carrier_delay_minutes,

        SUM(late_aircraft_delay_minutes) AS late_aircraft_delay_minutes,

        SUM(nas_delay_minutes) AS nas_delay_minutes,

        SUM(weather_delay_minutes) AS weather_delay_minutes,

        SUM(security_delay_minutes) AS security_delay_minutes,

        SUM(delay_cause_total_minutes) AS total_delay_minutes

    FROM fact_flights

    WHERE arrival_delayed_15 = 1

    GROUP BY reporting_carrier_code

    ORDER BY total_delay_minutes DESC
"""

results = con.execute(query).fetchall()

print("\n--- CARRIER DELAY CAUSE SUMMARY ---\n")

header = (
    f"{'Carrier':<10}"
    f"{'Delayed':>12}"
    f"{'Carrier Delay':>17}"
    f"{'Late Aircraft':>17}"
    f"{'NAS':>14}"
    f"{'Weather':>14}"
    f"{'Security':>12}"
    f"{'Total':>16}"
)

print(header)
print("-" * len(header))

for row in results:
    (
        carrier,
        total_records,
        delayed,
        carrier_delay,
        late_aircraft,
        nas,
        weather,
        security,
        total
    ) = row

    print(
        f"{carrier:<10}"
        f"{delayed:>12,}"
        f"{carrier_delay:>17,.0f}"
        f"{late_aircraft:>17,.0f}"
        f"{nas:>14,.0f}"
        f"{weather:>14,.0f}"
        f"{security:>12,.0f}"
        f"{total:>16,.0f}"
    )

print(f"\nCarriers analyzed: {len(results)}")

print("\n--- DELAY CAUSE CONTRIBUTION BY CARRIER ---")

for row in results:
    (
        carrier,
        total_records,
        delayed,
        carrier_delay,
        late_aircraft,
        nas,
        weather,
        security,
        total
    ) = row

    if total is None or total == 0:
        continue

    print(f"\nCarrier: {carrier}")
    print(f"Delayed arrivals: {delayed:,}")
    print(f"Total recorded delay minutes: {total:,.0f}")

    causes = [
        ("Carrier Delay", carrier_delay),
        ("Late Aircraft", late_aircraft),
        ("NAS", nas),
        ("Weather", weather),
        ("Security", security)
    ]

    for cause, minutes in causes:
        percentage = (minutes / total) * 100
        print(
            f"  {cause:<18}: "
            f"{minutes:>12,.0f} minutes | "
            f"{percentage:>6.2f}%"
        )

print("\nCarrier-level delay cause analysis completed.")

con.close()
