# SkyLens — Aviation Operations Intelligence

## Project Overview

**SkyLens** is an aviation operations analytics project built with Microsoft Power BI to explore flight activity, airline performance, delays, cancellations, and operational patterns.

The project transforms flight data into an interactive dashboard that helps users understand flight performance, compare airlines, monitor delay patterns, and explore operational details through visual analytics.

## Dashboard Preview

[Flight Overview](https://i.ibb.co/ZzZB5Zqd/skylens-1.png)

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

Blue Horizon recorded the highest flight volume with 2,045 flights, followed by AeroLink with 1,973 flights. Flight volumes across the five airlines are relatively balanced.

[Performance & Delays](https://i.ibb.co/0j6PVtQ6/skylens-2.png)

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

Global Wings recorded the highest departure (30.47 min) and arrival delays (55.12 min), while Nexa Air recorded the lowest averages at 27.41 and 52.01 minutes, respectively. Arrival delays were consistently higher than departure delays across all five airlines.

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
- Data inspection and validation
- Data type correction
- Handling missing values
- Data quality checks
- Validation of duplicate flight records
- Preparation of dimension and lookup tables
- Calendar table creation

Missing passenger and delay data were retained and accounted for rather than indiscriminately replaced, preserving the integrity of the dataset.

## Tools & Technologies

- **Microsoft Power BI** — Dashboard development and visualization
- **Power Query** — Data cleaning and transformation
- **DAX** — Measures, KPI calculations and analytical insights
- **Data Modelling** — Relationships between fact, dimension and calendar tables

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

## Project Structure

- `SkyLens.pbix` — Power BI dashboard project file
- `images/` — Dashboard screenshots and previews
- `README.md` — Project documentation

## Conclusion

SkyLens demonstrates how flight data can be transformed into an interactive business intelligence solution for monitoring aviation activity, analyzing airline performance, and identifying operational patterns.

The project emphasizes data preparation, analytical accuracy, dashboard design, and communicating insights through visualization.

---

*This project was developed for data analytics practice and portfolio demonstration.*

