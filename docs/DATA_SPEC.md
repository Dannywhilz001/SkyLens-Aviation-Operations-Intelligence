# Data specification — BTS pilot extract

## Source

Bureau of Transportation Statistics (BTS), TranStats — Reporting Carrier On-Time Performance (1987–present).

- Download page: https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=&gnoyr_VQ=FGJ
- Field definitions: https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ
- Release information: https://www.transtats.bts.gov/ReleaseInfo.asp

The table describes reporting carriers' non-stop domestic flights by month, year, carrier and origin/destination airport. Coverage is not worldwide and is not necessarily every flight operated by every airline.

## Pilot window

January 1, 2025 through March 31, 2025 (inclusive). This three-month window is only for initial pipeline testing. After validation, expand to January–December 2025.

## Fields to select in TranStats

Select these fields if they are available in the Reporting Carrier On-Time Performance table:

| Field | Intended use |
|---|---|
| `Year` | Calendar year filtering and validation |
| `Quarter` | Quarter-level summaries |
| `Month` | Month-level summaries |
| `DayofMonth` | Day-level checks |
| `DayOfWeek` | Weekday/weekend analysis |
| `FlightDate` | Flight date and date range |
| `Reporting_Airline` | Stable reporting-carrier identifier across years |
| `DOT_ID_Reporting_Airline` | DOT carrier identifier |
| `IATA_CODE_Reporting_Airline` | Familiar carrier code; do not use alone as a cross-year unique key |
| `OriginAirportID` | Origin airport identifier |
| `Origin` | Origin airport code |
| `DestAirportID` | Destination airport identifier |
| `Dest` | Destination airport code |
| `DepDelay` | Signed departure difference; early departures are negative |
| `DepDelayMinutes` | Departure delay minutes; early departures are set to zero |
| `DepDel15` | Departure delay indicator, 15 minutes or more |
| `ArrDelay` | Signed arrival difference; early arrivals are negative |
| `ArrDelayMinutes` | Arrival delay minutes; early arrivals are set to zero |
| `ArrDel15` | Arrival delay indicator, 15 minutes or more |
| `Cancelled` | Cancelled-flight indicator |
| `CancellationCode` | Reported cancellation reason code |
| `Diverted` | Diverted-flight indicator |
| `Distance` | Non-stop segment distance in miles |
| `CarrierDelay` | Carrier-attributed delay minutes |
| `WeatherDelay` | Weather-attributed delay minutes |
| `NASDelay` | National Air System-attributed delay minutes |
| `SecurityDelay` | Security-attributed delay minutes |
| `LateAircraftDelay` | Late-arriving-aircraft-attributed delay minutes |
| `Flights` | Flight count field; inspect and validate before using in totals |

If the download interface does not allow all fields in one export, use its merge-groups option or export the available fields in a documented way. Do not guess field names or substitute different fields without updating this specification.

## Important source definitions

- BTS treats a flight as on time when it arrives at the gate less than 15 minutes after its scheduled arrival time.
- `ArrDel15` and `DepDel15` are indicators for delays of 15 minutes or more.
- `ArrDelay` and `DepDelay` are signed differences; early arrivals/departures are negative.
- `ArrDelayMinutes` and `DepDelayMinutes` set early arrivals/departures to zero.
- Delay-cause fields are reported for eligible delayed flights; do not assume these fields are populated for every flight.

## Validation to perform after download

1. Confirm the export covers only Jan–Mar 2025.
2. Confirm all selected required fields are present.
3. Check row count and duplicate records.
4. Check whether `FlightDate` parses consistently.
5. Check valid values for `Cancelled`, `Diverted`, `ArrDel15` and `DepDel15`.
6. Check negative values in signed delay fields are retained.
7. Check that cancelled/diverted records are not incorrectly included in completed-arrival denominators.
8. Compare selected aggregate totals with BTS published summaries where comparable.

## Metric policy

Do not finalise KPI formulas until the downloaded file is inspected and denominator rules are checked. In particular, document whether each rate uses scheduled flights, completed flights or eligible arrivals. Never mix a raw signed delay field with a non-negative delay-minutes field without stating why.
