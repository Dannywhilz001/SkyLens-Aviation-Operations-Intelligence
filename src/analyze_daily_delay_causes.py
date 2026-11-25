
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 110)
print("SKYLENS | DAILY DELAY CAUSE TRENDS")
print("=" * 110)

query = """
    SELECT
        flight_date,

        COUNT(*) FILTER (
            WHERE arrival_delayed_15 = 1
        ) AS delayed_flights,

        SUM(carrier_delay_minutes) AS carrier_delay_minutes,

        SUM(late_aircraft_delay_minutes) AS late_aircraft_delay_minutes,

        SUM(nas_delay_minutes) AS nas_delay_minutes,

        SUM(weather_delay_minutes) AS weather_delay_minutes,

        SUM(security_delay_minutes) AS security_delay_minutes,

        SUM(delay_cause_total_minutes) AS total_delay_minutes

    FROM fact_flights

    WHERE arrival_delayed_15 = 1

    GROUP BY flight_date

    ORDER BY flight_date
"""

results = con.execute(query).fetchall()

print("\n--- DAILY DELAY CAUSE SUMMARY ---\n")

header = (
    f"{'Date':<13}"
    f"{'Delayed':>10}"
    f"{'Carrier':>14}"
    f"{'Late Aircraft':>16}"
    f"{'NAS':>13}"
    f"{'Weather':>13}"
    f"{'Security':>12}"
    f"{'Total':>16}"
)

print(header)
print("-" * len(header))

for row in results:
    (
        date,
        delayed,
        carrier,
        late_aircraft,
        nas,
        weather,
        security,
        total
    ) = row

    print(
        f"{str(date):<13}"
        f"{delayed:>10,}"
        f"{carrier:>14,.0f}"
        f"{late_aircraft:>16,.0f}"
        f"{nas:>13,.0f}"
        f"{weather:>13,.0f}"
        f"{security:>12,.0f}"
        f"{total:>16,.0f}"
    )

print(f"\nDays analyzed: {len(results)}")

print("\n--- DAILY CAUSE CONTRIBUTION PERCENTAGES ---\n")

for row in results:
    date, delayed, carrier, late_aircraft, nas, weather, security, total = row

    if total is None or total == 0:
        continue

    print(f"\n{date} | Total delay minutes: {total:,.0f}")

    causes = [
        ("Carrier", carrier),
        ("Late Aircraft", late_aircraft),
        ("NAS", nas),
        ("Weather", weather),
        ("Security", security)
    ]

    for cause, minutes in causes:
        percentage = 100 * minutes / total
        print(f"  {cause:<15}: {minutes:>10,.0f} minutes | {percentage:>6.2f}%")

print("\nDaily delay cause trends analysis completed.")

con.close()
