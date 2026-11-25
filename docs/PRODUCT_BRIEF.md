# Product brief — SkyLens Aviation Intelligence

## Product vision

Build a trustworthy, accessible aviation analytics product that helps users explore airline, airport and route reliability using documented public flight-performance data.

## Initial users

- Data analysts and students investigating airline operations.
- Aviation researchers and journalists exploring historical reliability patterns.
- Curious travellers comparing historical performance, with clear warnings that historical averages do not predict the outcome of an individual flight.

## Problem statement

Flight performance information is available in large public datasets, but users may find it difficult to prepare, compare and interpret the records consistently. SkyLens will make the dataset easier to explore while keeping the source, coverage, calculations and limitations visible.

## Initial release boundaries

- Geography: U.S. domestic reporting-carrier flights represented in the selected BTS dataset.
- Pilot data period: January–March 2025.
- Expansion target after validation: the full 2025 calendar year.
- Source: BTS TranStats Reporting Carrier On-Time Performance.
- Product type: historical analytics and exploration, not live tracking, flight dispatch or operational control.

## Core user tasks

1. Filter flight records by period, reporting airline, origin airport and destination airport.
2. Compare performance across airlines, airports and routes.
3. Examine delay causes and their distribution.
4. Inspect data coverage, missingness and validation results.
5. Export or reproduce clearly defined summaries.

## Planned product modules

### Flight Explorer

Filter the available historical flight records and inspect the associated performance measures.

### Airline Reliability

Compare reporting airlines using clearly defined performance measures and transparent denominators.

### Airport and Route Analysis

Explore origin, destination and route-level patterns. Apply minimum flight-volume thresholds before ranking entities to reduce misleading small-sample comparisons.

### Delay Causes

Explore the BTS delay-cause fields: carrier, weather, National Air System (NAS), security and late-arriving aircraft.

### Data Quality

Show source period, row counts, null checks, duplicate checks, schema checks and known limitations.

## Metric governance

No KPI should be displayed until its numerator, denominator, inclusion rules and treatment of cancelled/diverted flights are documented and tested. Keep raw delay minutes separate from the 15-minute delay indicators. Use BTS definitions for the official delay indicators.

## Explicitly out of scope for the first release

- Worldwide airline coverage.
- Live aircraft positions or live flight status.
- Claims about the causes of an individual flight's disruption beyond fields reported by BTS.
- Operational recommendations for airline dispatch or safety-critical decisions.
- Predictive delay scores until the historical data pipeline, leakage controls, baseline and out-of-time evaluation are implemented.

## Initial success criteria

- A new user can understand the geographic and date coverage before interpreting results.
- The same source files and documented steps reproduce the same cleaned dataset and summary metrics.
- Data validation checks report failures instead of silently passing bad data.
- Every published KPI has a documented definition and automated test.
- Users can filter and compare records without confusing scheduled, cancelled, diverted and completed flights.
