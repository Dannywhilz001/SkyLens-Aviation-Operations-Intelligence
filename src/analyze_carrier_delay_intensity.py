
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "database" / "skylens.duckdb"

con = duckdb.connect(str(DATABASE_FILE), read_only=True)

print("=" * 110)
print("SKYLENS | CARRIER DELAY INTENSITY ANALYSIS")
print("=" * 110)

query = """
    SELECT
        reporting_carrier_code,

        COUNT(*) AS delayed_arrivals,

        SUM(delay_cause_total_minutes) AS total_delay_minutes,

        SUM(carrier_delay_minutes) AS carrier_delay_minutes,

        SUM(late_aircraft_delay_minutes) AS late_aircraft_delay_minutes,

        SUM(nas_delay_minutes) AS nas_delay_minutes,

        SUM(weather_delay_minutes) AS weather_delay_minutes,

        SUM(security_delay_minutes) AS security_delay_minutes

    FROM fact_flights

    WHERE arrival_delayed_15 = 1

    GROUP BY reporting_carrier_code

    ORDER BY
        SUM(delay_cause_total_minutes) * 1.0 / COUNT(*) DESC
"""

results = con.execute(query).fetchall()

print("\n--- AVERAGE DELAY MINUTES PER DELAYED ARRIVAL ---\n")

header = (
    f"{'Carrier':<10}"
    f"{'Delayed':>12}"
    f"{'Total Avg':>14}"
    f"{'Carrier Avg':>15}"
    f"{'Late Acft Avg':>16}"
    f"{'NAS Avg':>12}"
    f"{'Weather Avg':>14}"
    f"{'Security Avg':>15}"
)

print(header)
print("-" * len(header))

for row in results:
    (
        carrier,
        delayed,
        total,
        carrier_delay,
        late_aircraft,
        nas,
        weather,
        security
    ) = row

    print(
        f"{carrier:<10}"
        f"{delayed:>12,}"
        f"{total / delayed:>14.2f}"
        f"{carrier_delay / delayed:>15.2f}"
        f"{late_aircraft / delayed:>16.2f}"
        f"{nas / delayed:>12.2f}"
        f"{weather / delayed:>14.2f}"
        f"{security / delayed:>15.2f}"
    )

print("\n--- CARRIER DELAY INTENSITY RANKING ---\n")

for rank, row in enumerate(results, start=1):
    carrier = row[0]
    delayed = row[1]
    total = row[2]

    average = total / delayed

    print(
        f"{rank:>2}. {carrier:<5} | "
        f"{average:>7.2f} minutes per delayed arrival | "
        f"{delayed:>7,} delayed arrivals"
    )

print("\nCarrier delay intensity analysis completed.")

con.close()
