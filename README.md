# SkyLens — Aviation Operations Intelligence

SkyLens is an aviation analytics project that transforms flight operational data into structured insights through interactive dashboards, analytical processing and data validation.

The project currently contains two complementary implementations:

1. **Power BI Dashboard** — an interactive business intelligence solution for exploring flight activity, airline performance and operational delays.
2. **Python & Streamlit Analytics Platform** — a reproducible aviation analytics application built around public U.S. Bureau of Transportation Statistics (BTS) flight data.

Together, these implementations demonstrate data preparation, analytical modelling, performance measurement, interactive visualization and analytical storytelling.

---

# 1. Power BI Dashboard

## Project Overview

The Power BI implementation explores flight activity, airline performance, delays, cancellations and operational patterns through an interactive dashboard.

It transforms flight data into visual insights that help users understand flight performance, compare airlines, monitor delay patterns and explore operational details.

## Dashboard Preview

### Flight Overview

![Flight Overview](https://i.ibb.co/ZzZB5Zqd/skylens-1.png)

Provides a high-level view of flight activity and operational distribution.

**Key Performance Indicators (KPIs):**
- Total Flights
- On-Time Rate (%)
- Total Delay (min)
- Cancelled Flights
- Average Arrival Delay (min)

**Visualizations:**
- Flight Status Distribution
- Flight Volume Trend
- Flight Distribution by Airline
- Flight Distribution by Destination Airport
- Airline Traffic Insight

**Key Insight:**

Blue Horizon recorded the highest flight volume with 2,045 flights, followed by AeroLink with 1,973 flights. Flight volumes across the five airlines were relatively balanced.

### Performance & Delays

![Performance and Delays](https://i.ibb.co/0j6PVtQ6/skylens-2.png)

Focuses on airline delay performance and temporal patterns in flight delays.

**Key Performance Indicators (KPIs):**
- Delayed Flights
- Delay Rate (%)
- Average Departure Delay (min)
- Average Arrival Delay (min)

**Visualizations:**
- Delay Trend Over Time
- Average Departure Delay by Airline
- Average Arrival Delay by Airline
- Delayed Flights by Day of Week
- Airline Delay Performance Insight

**Key Insight:**

Global Wings recorded the highest average departure delay (30.47 min) and arrival delay (55.12 min), while Nexa Air recorded the lowest averages at 27.41 and 52.01 minutes, respectively. Arrival delays were consistently higher than departure delays across all five airlines.

## Key Project Findings

- The dataset contains 10,000 flight records.
- 6,964 flights were recorded as delayed.
- 335 flights were cancelled.
- 2,795 flights were recorded as on-time.
- Global Wings recorded the highest average departure and arrival delays among the five airlines.
- Nexa Air recorded the lowest average departure and arrival delays.
- Flight volumes across the five airlines were relatively balanced.

## Data Preparation & Quality

Data preparation was performed using Power Query.

The workflow included:
- Data inspection and validation.
- Data type correction.
- Handling missing values.
- Data quality checks.
- Validation of duplicate flight records.
- Preparation of dimension and lookup tables.
- Calendar table creation.

Missing passenger and delay data were retained and accounted for rather than indiscriminately replaced, preserving the integrity of the dataset.

## Power BI Tools & Technologies

- **Microsoft Power BI** — dashboard development and visualization.
- **Power Query** — data cleaning and transformation.
- **DAX** — measures, KPI calculations and analytical insights.
- **Data Modelling** — relationships between fact, dimension and calendar tables.

## Skills Demonstrated

- Data Cleaning & Transformation
- Data Modelling
- DAX Measures
- KPI Development
- Data Visualization
- Dashboard Design
- Operational Performance Analysis
- Airline Performance Analysis
- Analytical Storytelling

---

# 2. Python & Streamlit Aviation Analytics Platform

## Project Overview

The Python implementation extends SkyLens into a reproducible aviation analytics platform for exploring flight reliability, delays, cancellations, diversions and route performance using public U.S. airline on-time performance data.

It uses a structured data pipeline to transform source records into analytical datasets, validate performance metrics and present results through an interactive Streamlit application.

## Product Scope

- **Geography:** U.S. domestic reporting-carrier flights.
- **Reporting period:** January 2025.
- **Dataset size:** 539,747 flight records.
- **Primary data source:** U.S. Department of Transportation, Bureau of Transportation Statistics (BTS), TranStats — Reporting Carrier On-Time Performance.

This is a historical aviation analytics application, not a live flight tracking system. Its coverage is limited to the reporting-carrier data available in the selected BTS dataset.

### Source References

- [BTS TranStats Download Page](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=&gnoyr_VQ=FGJ)
- [BTS Field Definitions](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)
- [BTS Release Information](https://www.transtats.bts.gov/ReleaseInfo.asp)

## Analytical Objectives

The platform supports:

- Airline operational performance analysis.
- Airport arrival reliability analysis.
- Directional route performance analysis.
- Flight delay and cancellation analysis.
- Delay-cause contribution analysis.
- Daily operational performance monitoring.
- Data quality and validation reporting.
- Interactive exploration through a web application.

## Key Analytical Findings

The January 2025 BTS analysis produced the following results:

| Metric | Result |
|---|---:|
| Total Flight Records | 539,747 |
| Evaluated Arrivals | 522,269 |
| Delayed Arrivals | 98,130 |
| Arrival Delay Rate | 18.79% |
| On-Time Arrivals | 424,139 |
| On-Time Arrival Rate | 81.21% |
| Cancelled Flights | 16,312 |
| Cancellation Rate | 3.02% |
| Diversions | 1,166 |
| Diversion Rate | 0.22% |
| Average Signed Arrival Delay | 3.76 min |

**Important metric definitions:**

- Arrival delay rate is calculated using evaluated arrivals as the denominator.
- On-time arrivals include early arrivals and arrivals delayed by fewer than 15 minutes.
- Average signed arrival delay includes early arrivals as negative values.
- Cancellation and diversion rates use total flight records as their denominator.

## Delay-Cause Analysis

The analysis examines recorded delay minutes attributed to five operational categories.

| Delay Cause | Recorded Delay Minutes | Share |
|---|---:|---:|
| Carrier | 2,510,886 | 36.16% |
| Late Aircraft | 2,410,759 | 34.72% |
| National Airspace System (NAS) | 1,381,827 | 19.90% |
| Weather | 629,972 | 9.07% |
| Security | 10,550 | 0.15% |

Carrier and late aircraft delays together accounted for 70.88% of recorded delay-cause minutes.

These percentages represent shares of recorded delay-cause minutes, not percentages of all flights or delayed flights.

## Analytical Coverage

### Overall Flight Performance

- Total flight records.
- Evaluated arrivals.
- Delayed arrivals.
- Arrival delay rate.
- Cancellation counts and rates.
- Diversion counts.
- Average signed arrival delay.

### Carrier Performance

- Total flights.
- Evaluated arrivals.
- Delayed arrivals.
- Arrival delay rate.
- Average signed arrival delay.

Carrier arrival delay rates use evaluated arrivals as the denominator.

### Airport Performance

Destination airport analysis examines:

- Evaluated arrivals.
- Delayed arrivals.
- Arrival delay rate.
- Average arrival delay intensity among delayed arrivals.

A minimum sample threshold of 500 evaluated arrivals is applied.

### Route Performance

Directional route analysis examines:

- Origin and destination.
- Evaluated arrivals.
- Delayed arrivals.
- Arrival delay rate.
- Average delay intensity.
- Relative performance classification.

Routes are evaluated directionally. A route from airport A to airport B is treated separately from the reverse direction.

A minimum sample threshold of 300 evaluated arrivals is applied.

### Daily Performance

- Evaluated arrivals.
- Delayed arrivals.
- Arrival delay rate.
- Daily operational variations.

### Delay-Cause Analysis

- Carrier delay.
- Late aircraft delay.
- National Airspace System delay.
- Weather delay.
- Security delay.

## Data Pipeline

SkyLens uses a structured analytical pipeline designed to preserve source data and separate ingestion, transformation, storage, analysis and validation.

### 1. Source Data

Original BTS flight records are retained as raw source data.

The source includes flight dates, operating carriers, origin and destination airports, scheduled and actual times, delays, cancellation and diversion status, flight distance and delay-cause records.

### 2. Transformation

Flight data is processed using Python, Pandas and DuckDB.

Transformation activities include:

- Data type standardization.
- Date parsing.
- Derived analytical fields.
- Delay status classification.
- Data consistency checks.
- Delay-cause reconciliation.
- Extreme delay observation flagging.

The transformation process preserves the original raw data.

### 3. Analytical Storage

Transformed flight records are stored in Parquet format and loaded into a DuckDB analytical database.

This provides a reproducible environment for SQL-based analysis and analytical output generation.

### 4. Analytical Processing

Python analytical scripts generate performance summaries across multiple operational dimensions.

### 5. Validation

Independent validation scripts compare exported analytical results against separately calculated database results.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing, analysis and validation |
| Pandas | Data manipulation and analytical processing |
| DuckDB | Analytical database and SQL querying |
| SQL | Metric calculations and data analysis |
| Parquet | Structured analytical data storage |
| Plotly | Interactive visualization |
| Streamlit | Interactive web application |
| Git | Version control |
| GitHub | Project hosting and documentation |

---

# 3. Repository Structure

```text
SkyLens-Aviation-Operations-Intelligence/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── analytics/
│   └── database/
│
├── docs/
│   ├── DATA_SPEC.md
│   ├── PRODUCT_BRIEF.md
│   └── analytical_summary.md
│
├── src/
│   ├── transform_flights.py
│   ├── build_database.py
│   ├── export_analytical_outputs.py
│   ├── generate_analytical_summary.py
│   ├── analyze_carrier_performance.py
│   ├── analyze_airport_performance.py
│   ├── analyze_route_performance.py
│   ├── analyze_daily_performance.py
│   └── validation and investigation scripts
│
└── images/
    └── Power BI dashboard screenshots
```

The repository contains the analytical application, supporting data-processing scripts, documentation and dashboard assets. Large raw source files and generated database files are excluded from version control.

---

# 4. Conclusion

SkyLens demonstrates how aviation operational data can be transformed into meaningful analytical insights through business intelligence, Python-based data processing and interactive visualization.

By combining a Power BI dashboard with a reproducible Python and Streamlit analytics platform, the project demonstrates a broader workflow spanning data preparation, analytical modelling, metric validation, operational performance analysis and insight communication.

The project emphasizes analytical accuracy, reproducibility, transparent metric definitions and practical application of data analytics techniques.

---

*Developed as a data analytics portfolio project for learning, experimentation and demonstration of analytical capabilities.*