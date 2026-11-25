
import duckdb
import pandas as pd
from pathlib import Path
from statistics import median

# ==================================================
# SKYLENS | CONFIGURATION
# ==================================================

DB_PATH = "data/database/skylens.duckdb"
EXPORT_DIR = Path("data/processed/analytics")
REPORT_PATH = Path("docs/analytical_summary.md")

EXPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH, read_only=True)

exports = {}

# ==================================================
# 1. OVERALL FLIGHT PERFORMANCE
# ==================================================

overall = con.execute("""
SELECT
    COUNT(*) AS total_flights,
    MIN(flight_date) AS start_date,
    MAX(flight_date) AS end_date,
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
""").df()

exports["overall_performance"] = overall

# ==================================================
# 2. CARRIER PERFORMANCE
# ==================================================

exports["carrier_performance"] = con.execute("""
SELECT
    reporting_carrier_code AS carrier,
    COUNT(*) AS total_flights,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
        2
    ) AS delay_rate_pct,
    ROUND(AVG(arrival_delay_minutes), 2)
        AS avg_signed_delay_minutes
FROM fact_flights
GROUP BY reporting_carrier_code
ORDER BY delay_rate_pct DESC
""").df()

# ==================================================
# 3. AIRPORT PERFORMANCE
# ==================================================

exports["airport_performance"] = con.execute("""
SELECT
    destination AS airport,
    destination_city AS city,
    COUNT(arrival_delayed_15) AS evaluated_arrivals,
    SUM(CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END)
        AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE WHEN arrival_delayed_15 = 1 THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(arrival_delayed_15), 0),
        2
    ) AS delay_rate_pct,
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
    ) AS avg_delay_intensity_minutes
FROM fact_flights
GROUP BY destination, destination_city
HAVING COUNT(arrival_delayed_15) >= 500
ORDER BY delay_rate_pct DESC
""").df()

# ==================================================
# 4. ROUTE PERFORMANCE
# ==================================================

route_data = con.execute("""
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
    ) AS delay_rate_pct,
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
    ) AS avg_delay_intensity_minutes
FROM fact_flights
GROUP BY origin, destination
HAVING COUNT(arrival_delayed_15) >= 300
ORDER BY delay_rate_pct DESC
""").df()

# ==================================================
# 5. ROUTE PERFORMANCE CLASSIFICATION
# ==================================================

median_rate = median(route_data["delay_rate_pct"])

median_intensity = median(
    route_data["avg_delay_intensity_minutes"]
)

def classify_route(row):
    high_rate = row["delay_rate_pct"] >= median_rate

    high_intensity = (
        row["avg_delay_intensity_minutes"] >= median_intensity
    )

    if high_rate and high_intensity:
        return "HIGH RATE + HIGH INTENSITY"

    elif high_rate:
        return "HIGH RATE + LOW INTENSITY"

    elif high_intensity:
        return "LOW RATE + HIGH INTENSITY"

    return "LOW RATE + LOW INTENSITY"


route_data["classification"] = route_data.apply(
    classify_route,
    axis=1
)

exports["route_performance"] = route_data

# ==================================================
# 6. DELAY CAUSE CONTRIBUTIONS
# ==================================================

cause_data = con.execute("""
SELECT
    SUM(carrier_delay_minutes) AS carrier_minutes,
    SUM(late_aircraft_delay_minutes) AS late_aircraft_minutes,
    SUM(nas_delay_minutes) AS nas_minutes,
    SUM(weather_delay_minutes) AS weather_minutes,
    SUM(security_delay_minutes) AS security_minutes
FROM fact_flights
WHERE arrival_delayed_15 = 1
""").df()

cause_columns = {
    "Carrier": "carrier_minutes",
    "Late Aircraft": "late_aircraft_minutes",
    "NAS": "nas_minutes",
    "Weather": "weather_minutes",
    "Security": "security_minutes"
}

cause_rows = []

total_cause_minutes = sum(
    cause_data.iloc[0][column]
    for column in cause_columns.values()
)

for cause, column in cause_columns.items():

    minutes = cause_data.iloc[0][column]

    cause_rows.append({
        "delay_cause": cause,
        "total_delay_minutes": minutes,
        "contribution_pct": (
            100 * minutes / total_cause_minutes
            if total_cause_minutes else 0
        )
    })

exports["delay_cause_contributions"] = pd.DataFrame(
    cause_rows
)

# ==================================================
# 7. DAILY PERFORMANCE
# ==================================================

exports["daily_performance"] = con.execute("""
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
    ) AS delay_rate_pct
FROM fact_flights
GROUP BY flight_date
ORDER BY flight_date
""").df()

# ==================================================
# 8. EXPORT ALL CSV FILES
# ==================================================

for name, dataframe in exports.items():

    output_path = EXPORT_DIR / f"{name}.csv"

    dataframe.to_csv(output_path, index=False)

    print(f"Exported: {output_path}")

# ==================================================
# 9. PROFESSIONAL MARKDOWN REPORT
# ==================================================

o = overall.iloc[0]

daily = exports["daily_performance"]
causes = exports["delay_cause_contributions"]
carriers = exports["carrier_performance"]
airports = exports["airport_performance"]
routes = exports["route_performance"]

# --------------------------------------------------
# REPORT FORMATTING FUNCTIONS
# --------------------------------------------------

def fmt_number(value):
    return f"{value:,.0f}"


def fmt_decimal(value):
    return f"{value:,.2f}"


def fmt_percent(value):
    return f"{value:.2f}%"


def make_table(dataframe, columns, headers, formats=None):
    display = dataframe[columns].copy()

    display.columns = headers

    formats = formats or {}

    for column, formatter in formats.items():

        if column in display.columns:
            display[column] = display[column].map(formatter)

    return display.to_markdown(index=False)


# --------------------------------------------------
# KEY FINDINGS
# --------------------------------------------------

highest_day = daily.loc[
    daily["delay_rate_pct"].idxmax()
]

lowest_day = daily.loc[
    daily["delay_rate_pct"].idxmin()
]

highest_carrier = carriers.iloc[0]

highest_airport = airports.iloc[0]

highest_intensity_airport = airports.sort_values(
    "avg_delay_intensity_minutes",
    ascending=False
).iloc[0]

highest_rate_route = routes.iloc[0]

highest_intensity_route = routes.sort_values(
    "avg_delay_intensity_minutes",
    ascending=False
).iloc[0]

classification_counts = routes["classification"].value_counts()

carrier_late_share = causes.loc[
    causes["delay_cause"].isin(
        ["Carrier", "Late Aircraft"]
    ),
    "contribution_pct"
].sum()

# --------------------------------------------------
# BUILD REPORT
# --------------------------------------------------

report = []

report.append("# SkyLens | Aviation Performance Analysis")
report.append("")

report.append(
    "*Operational reliability, arrival delays and disruption patterns*"
)

report.append("")

report.append("## Reporting scope")
report.append("")

report.append(
    f"- **Reporting period:** "
    f"{o['start_date']:%d %B %Y} – {o['end_date']:%d %B %Y}"
)

report.append(
    "- **Data source:** BTS Reporting Carrier On-Time Performance"
)

report.append(
    "- **Geographic coverage:** U.S. domestic reporting-carrier flights"
)

report.append(
    "- **Analysis frequency:** January 2025"
)

report.append("")
report.append("---")
report.append("")

# ==================================================
# 1. OVERALL PERFORMANCE
# ==================================================

overall_delay_rate = (
    100 * o["delayed_arrivals"] / o["evaluated_arrivals"]
)

report.append("## 1. Overall flight performance")
report.append("")

report.append("### Network-wide operational snapshot")
report.append("")

report.append("| Performance indicator | Result |")
report.append("|:--|--:|")

report.append(
    f"| Total flight records | {fmt_number(o['total_flights'])} |"
)

report.append(
    f"| Reporting carriers | {fmt_number(o['carriers'])} |"
)

report.append(
    f"| Evaluated arrivals | {fmt_number(o['evaluated_arrivals'])} |"
)

report.append(
    f"| Delayed arrivals | {fmt_number(o['delayed_arrivals'])} |"
)

report.append(
    f"| Arrival delay rate | {fmt_percent(overall_delay_rate)} |"
)

report.append(
    f"| Cancellations | {fmt_number(o['cancellations'])} |"
)

report.append(
    f"| Diversions | {fmt_number(o['diversions'])} |"
)

report.append(
    f"| Average signed arrival delay | "
    f"{fmt_decimal(o['avg_signed_arrival_delay'])} min |"
)

report.append("")

report.append(
    f"**Key finding:** {fmt_percent(overall_delay_rate)} of "
    "evaluated arrivals experienced delays of at least 15 minutes."
)

report.append("")

# ==================================================
# 2. CARRIER PERFORMANCE
# ==================================================

report.append("## 2. Carrier performance")
report.append("")

report.append(
    "### Five carriers with the highest arrival delay rates"
)

report.append("")

report.append(
    make_table(
        carriers.head(5),
        [
            "carrier",
            "total_flights",
            "evaluated_arrivals",
            "delayed_arrivals",
            "delay_rate_pct",
            "avg_signed_delay_minutes"
        ],
        [
            "Carrier",
            "Flights",
            "Evaluated",
            "Delayed",
            "Delay rate",
            "Avg. signed delay (min)"
        ],
        {
            "Flights": fmt_number,
            "Evaluated": fmt_number,
            "Delayed": fmt_number,
            "Delay rate": fmt_percent,
            "Avg. signed delay (min)": fmt_decimal
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** {highest_carrier['carrier']} recorded "
    f"the highest arrival delay rate at "
    f"{fmt_percent(highest_carrier['delay_rate_pct'])}."
)

report.append("")

# ==================================================
# 3. AIRPORT PERFORMANCE
# ==================================================

report.append("## 3. Airport performance")
report.append("")

report.append(
    "### Airports with the highest arrival delay rates"
)

report.append("")

report.append(
    make_table(
        airports.head(5),
        [
            "airport",
            "city",
            "evaluated_arrivals",
            "delayed_arrivals",
            "delay_rate_pct"
        ],
        [
            "Airport",
            "City",
            "Evaluated",
            "Delayed",
            "Delay rate"
        ],
        {
            "Evaluated": fmt_number,
            "Delayed": fmt_number,
            "Delay rate": fmt_percent
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** {highest_airport['airport']} "
    f"({highest_airport['city']}) recorded the highest "
    f"airport delay rate at "
    f"{fmt_percent(highest_airport['delay_rate_pct'])}."
)

report.append("")

report.append(
    "### Airports with the highest delay intensity"
)

report.append("")

report.append(
    make_table(
        airports.sort_values(
            "avg_delay_intensity_minutes",
            ascending=False
        ).head(5),
        [
            "airport",
            "city",
            "delayed_arrivals",
            "avg_delay_intensity_minutes"
        ],
        [
            "Airport",
            "City",
            "Delayed",
            "Avg. intensity (min)"
        ],
        {
            "Delayed": fmt_number,
            "Avg. intensity (min)": fmt_decimal
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** {highest_intensity_airport['airport']} "
    f"recorded the highest average delay intensity at "
    f"{fmt_decimal(highest_intensity_airport['avg_delay_intensity_minutes'])} minutes."
)

report.append("")

# ==================================================
# 4. ROUTE PERFORMANCE
# ==================================================

report.append("## 4. Route performance")
report.append("")

report.append(
    "### Routes with the highest arrival delay rates"
)

report.append("")

report.append(
    make_table(
        routes.head(5),
        [
            "origin",
            "destination",
            "evaluated_arrivals",
            "delayed_arrivals",
            "delay_rate_pct",
            "classification"
        ],
        [
            "Origin",
            "Destination",
            "Evaluated",
            "Delayed",
            "Delay rate",
            "Classification"
        ],
        {
            "Evaluated": fmt_number,
            "Delayed": fmt_number,
            "Delay rate": fmt_percent
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** {highest_rate_route['origin']}–"
    f"{highest_rate_route['destination']} recorded the highest "
    f"route delay rate at "
    f"{fmt_percent(highest_rate_route['delay_rate_pct'])}."
)

report.append("")

report.append(
    "### Routes with the highest delay intensity"
)

report.append("")

report.append(
    make_table(
        routes.sort_values(
            "avg_delay_intensity_minutes",
            ascending=False
        ).head(5),
        [
            "origin",
            "destination",
            "evaluated_arrivals",
            "delayed_arrivals",
            "avg_delay_intensity_minutes"
        ],
        [
            "Origin",
            "Destination",
            "Evaluated",
            "Delayed",
            "Avg. intensity (min)"
        ],
        {
            "Evaluated": fmt_number,
            "Delayed": fmt_number,
            "Avg. intensity (min)": fmt_decimal
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** {highest_intensity_route['origin']}–"
    f"{highest_intensity_route['destination']} recorded the "
    f"highest average delay intensity at "
    f"{fmt_decimal(highest_intensity_route['avg_delay_intensity_minutes'])} minutes."
)

report.append("")

report.append(
    "> **Interpretation note:** Route intensity should be "
    "considered alongside the number of delayed arrivals. "
    "A high average based on a smaller sample may be less stable."
)

report.append("")

# ==================================================
# 5. DELAY CAUSE CONTRIBUTIONS
# ==================================================

report.append("## 5. Delay cause contributions")
report.append("")

report.append(
    "### Distribution of recorded arrival delay minutes"
)

report.append("")

report.append(
    make_table(
        causes.sort_values(
            "contribution_pct",
            ascending=False
        ),
        [
            "delay_cause",
            "total_delay_minutes",
            "contribution_pct"
        ],
        [
            "Delay cause",
            "Total minutes",
            "Contribution"
        ],
        {
            "Total minutes": fmt_number,
            "Contribution": fmt_percent
        }
    )
)

report.append("")

report.append(
    f"**Key finding:** Carrier-related and late-aircraft delays "
    f"together accounted for {fmt_percent(carrier_late_share)} "
    "of recorded delay-cause minutes."
)

report.append("")

# ==================================================
# 6. DAILY PERFORMANCE
# ==================================================

report.append("## 6. Daily performance")
report.append("")

report.append(
    "### Highest and lowest daily arrival delay rates"
)

report.append("")

report.append("| Indicator | Date | Delay rate |")
report.append("|:--|:--|--:|")

report.append(
    f"| Highest delay rate | "
    f"{highest_day['flight_date']:%d %b %Y} | "
    f"{fmt_percent(highest_day['delay_rate_pct'])} |"
)

report.append(
    f"| Lowest delay rate | "
    f"{lowest_day['flight_date']:%d %b %Y} | "
    f"{fmt_percent(lowest_day['delay_rate_pct'])} |"
)

report.append("")

report.append(
    f"**Key finding:** {highest_day['flight_date']:%d %B %Y} "
    f"recorded the highest daily arrival delay rate, while "
    f"{lowest_day['flight_date']:%d %B %Y} recorded the lowest."
)

report.append("")

# ==================================================
# 7. ROUTE CLASSIFICATION
# ==================================================

report.append("## 7. Route performance classification")
report.append("")

report.append(
    "Routes are classified using the median delay rate and "
    "median delay intensity across the qualifying route dataset."
)

report.append("")

report.append("| Classification | Routes |")
report.append("|:--|--:|")

for category in [
    "HIGH RATE + HIGH INTENSITY",
    "HIGH RATE + LOW INTENSITY",
    "LOW RATE + HIGH INTENSITY",
    "LOW RATE + LOW INTENSITY"
]:

    report.append(
        f"| {category.title()} | "
        f"{fmt_number(classification_counts.get(category, 0))} |"
    )

report.append("")

report.append(
    f"- **Routes classified:** {fmt_number(len(routes))}"
)

report.append(
    f"- **Median delay rate:** {fmt_percent(median_rate)}"
)

report.append(
    f"- **Median delay intensity:** "
    f"{fmt_decimal(median_intensity)} minutes"
)

report.append("")

# ==================================================
# 8. METHODOLOGY AND LIMITATIONS
# ==================================================

report.append("## 8. Methodology and limitations")
report.append("")

report.append(
    "- Arrival delay rates exclude records with unknown "
    "arrival-delay status."
)

report.append(
    "- An arrival is classified as delayed when its arrival "
    "delay is at least 15 minutes."
)

report.append(
    "- Delay intensity represents average recorded delay-cause "
    "minutes among arrivals delayed by at least 15 minutes."
)

report.append(
    "- Airport rankings require at least 500 evaluated arrivals."
)

report.append(
    "- Route rankings and classifications require at least "
    "300 evaluated arrivals."
)

report.append(
    "- Route classifications use dataset-specific median "
    "thresholds, not universal aviation standards."
)

report.append(
    "- Route direction is preserved; A–B and B–A are treated "
    "as separate routes."
)

report.append(
    "- Delay-cause contribution percentages represent shares "
    "of recorded delay minutes, not percentages of affected flights."
)

report.append(
    "- Results describe January 2025 only and should not be "
    "interpreted as permanent performance rankings."
)

report.append("")

report.append("---")
report.append("")

report.append(
    "*Generated by SkyLens Aviation Intelligence | "
    "BTS Reporting Carrier On-Time Performance*"
)

# ==================================================
# 10. SAVE REPORT AND CLOSE DATABASE
# ==================================================

REPORT_PATH.write_text(
    "\n".join(report),
    encoding="utf-8"
)

con.close()

print("\n" + "=" * 65)
print("SKYLENS | ANALYTICAL EXPORT COMPLETED")
print("=" * 65)

print(f"CSV files exported: {len(exports)}")
print(f"Markdown report: {REPORT_PATH}")
