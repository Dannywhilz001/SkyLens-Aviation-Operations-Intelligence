# SkyLens | Aviation Performance Analysis

*Operational reliability, arrival delays and disruption patterns*

## Reporting scope

- **Reporting period:** 01 January 2025 – 31 January 2025
- **Data source:** BTS Reporting Carrier On-Time Performance
- **Geographic coverage:** U.S. domestic reporting-carrier flights
- **Analysis frequency:** January 2025

---

## 1. Overall flight performance

### Network-wide operational snapshot

| Performance indicator | Result |
|:--|--:|
| Total flight records | 539,747 |
| Reporting carriers | 14 |
| Evaluated arrivals | 522,269 |
| Delayed arrivals | 98,130 |
| Arrival delay rate | 18.79% |
| Cancellations | 16,312 |
| Diversions | 1,166 |
| Average signed arrival delay | 3.76 min |

**Key finding:** 18.79% of evaluated arrivals experienced delays of at least 15 minutes.

## 2. Carrier performance

### Five carriers with the highest arrival delay rates

| Carrier   |   Flights |   Evaluated |   Delayed | Delay rate   |   Avg. signed delay (min) |
|:----------|----------:|------------:|----------:|:-------------|--------------------------:|
| F9        |    15,526 |      15,110 |     3,925 | 25.98%       |                     10.82 |
| OH        |    21,094 |      19,151 |     4,880 | 25.48%       |                     14.14 |
| B6        |    17,918 |      17,558 |     4,294 | 24.46%       |                      5.81 |
| G4        |     9,345 |       9,206 |     2,183 | 23.71%       |                      9.54 |
| OO        |    65,036 |      63,502 |    13,261 | 20.88%       |                      7.94 |

**Key finding:** F9 recorded the highest arrival delay rate at 25.98%.

## 3. Airport performance

### Airports with the highest arrival delay rates

| Airport   | City                           |   Evaluated |   Delayed | Delay rate   |
|:----------|:-------------------------------|------------:|----------:|:-------------|
| ASE       | Aspen, CO                      |         962 |       327 | 33.99%       |
| SFB       | Sanford, FL                    |         783 |       237 | 30.27%       |
| PGD       | Punta Gorda, FL                |         704 |       210 | 29.83%       |
| PBI       | West Palm Beach/Palm Beach, FL |       2,886 |       838 | 29.04%       |
| EGE       | Eagle, CO                      |         718 |       203 | 28.27%       |

**Key finding:** ASE (Aspen, CO) recorded the highest airport delay rate at 33.99%.

### Airports with the highest delay intensity

| Airport   | City                  |   Delayed |   Avg. intensity (min) |
|:----------|:----------------------|----------:|-----------------------:|
| ASE       | Aspen, CO             |       327 |                  99.31 |
| DFW       | Dallas/Fort Worth, TX |     5,135 |                  91.92 |
| HNL       | Honolulu, HI          |       581 |                  90.5  |
| ATL       | Atlanta, GA           |     4,486 |                  89.42 |
| SBN       | South Bend, IN        |       151 |                  88.17 |

**Key finding:** ASE recorded the highest average delay intensity at 99.31 minutes.

## 4. Route performance

### Routes with the highest arrival delay rates

| Origin   | Destination   |   Evaluated |   Delayed | Delay rate   | Classification             |
|:---------|:--------------|------------:|----------:|:-------------|:---------------------------|
| DEN      | COS           |         433 |       148 | 34.18%       | HIGH RATE + LOW INTENSITY  |
| BOS      | MCO           |         416 |       133 | 31.97%       | HIGH RATE + LOW INTENSITY  |
| JFK      | SJU           |         332 |       104 | 31.33%       | HIGH RATE + HIGH INTENSITY |
| DFW      | SAT           |         347 |       108 | 31.12%       | HIGH RATE + HIGH INTENSITY |
| JFK      | MCO           |         385 |       119 | 30.91%       | HIGH RATE + LOW INTENSITY  |

**Key finding:** DEN–COS recorded the highest route delay rate at 34.18%.

### Routes with the highest delay intensity

| Origin   | Destination   |   Evaluated |   Delayed |   Avg. intensity (min) |
|:---------|:--------------|------------:|----------:|-----------------------:|
| AUS      | DFW           |         364 |        49 |                 149.82 |
| DFW      | AUS           |         365 |        85 |                 124.01 |
| IAH      | DFW           |         460 |        98 |                 121.39 |
| ORD      | DTW           |         422 |        92 |                 108.08 |
| BOS      | LAX           |         319 |        37 |                 106.03 |

**Key finding:** AUS–DFW recorded the highest average delay intensity at 149.82 minutes.

> **Interpretation note:** Route intensity should be considered alongside the number of delayed arrivals. A high average based on a smaller sample may be less stable.

## 5. Delay cause contributions

### Distribution of recorded arrival delay minutes

| Delay cause   |   Total minutes | Contribution   |
|:--------------|----------------:|:---------------|
| Carrier       |       2,510,886 | 36.16%         |
| Late Aircraft |       2,410,759 | 34.72%         |
| NAS           |       1,381,827 | 19.90%         |
| Weather       |         629,972 | 9.07%          |
| Security      |          10,550 | 0.15%          |

**Key finding:** Carrier-related and late-aircraft delays together accounted for 70.88% of recorded delay-cause minutes.

## 6. Daily performance

### Highest and lowest daily arrival delay rates

| Indicator | Date | Delay rate |
|:--|:--|--:|
| Highest delay rate | 06 Jan 2025 | 40.15% |
| Lowest delay rate | 28 Jan 2025 | 5.89% |

**Key finding:** 06 January 2025 recorded the highest daily arrival delay rate, while 28 January 2025 recorded the lowest.

## 7. Route performance classification

Routes are classified using the median delay rate and median delay intensity across the qualifying route dataset.

| Classification | Routes |
|:--|--:|
| High Rate + High Intensity | 91 |
| High Rate + Low Intensity | 72 |
| Low Rate + High Intensity | 71 |
| Low Rate + Low Intensity | 90 |

- **Routes classified:** 324
- **Median delay rate:** 18.10%
- **Median delay intensity:** 64.31 minutes

## 8. Methodology and limitations

- Arrival delay rates exclude records with unknown arrival-delay status.
- An arrival is classified as delayed when its arrival delay is at least 15 minutes.
- Delay intensity represents average recorded delay-cause minutes among arrivals delayed by at least 15 minutes.
- Airport rankings require at least 500 evaluated arrivals.
- Route rankings and classifications require at least 300 evaluated arrivals.
- Route classifications use dataset-specific median thresholds, not universal aviation standards.
- Route direction is preserved; A–B and B–A are treated as separate routes.
- Delay-cause contribution percentages represent shares of recorded delay minutes, not percentages of affected flights.
- Results describe January 2025 only and should not be interpreted as permanent performance rankings.

---

*Generated by SkyLens Aviation Intelligence | BTS Reporting Carrier On-Time Performance*