
from pathlib import Path
import pandas as pd
import duckdb

# ==========================================================
# SKYLENS | ANALYTICAL OUTPUT VALIDATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "database" / "skylens.duckdb"
EXPORT_DIR = BASE_DIR / "data" / "processed" / "analytics"

EXPECTED_FILES = {
    "overall_performance.csv": 1,
    "carrier_performance.csv": 14,
    "airport_performance.csv": 125,
    "route_performance.csv": 324,
    "delay_cause_contributions.csv": 5,
    "daily_performance.csv": 31
}

passed = 0
failed = 0
warnings = 0


def check(condition, description):
    global passed, failed

    if condition:
        print(f"[PASS] {description}")
        passed += 1
    else:
        print(f"[FAIL] {description}")
        failed += 1


def warning(description):
    global warnings
    print(f"[WARN] {description}")
    warnings += 1


def normalize_column(column):
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def find_column(df, possible_names):
    columns = {
        normalize_column(column): column
        for column in df.columns
    }

    for name in possible_names:
        if name in columns:
            return columns[name]

    return None


print("=" * 65)
print("SKYLENS | ANALYTICAL OUTPUT VALIDATION")
print("=" * 65)

# ----------------------------------------------------------
# 1. CHECK DATABASE
# ----------------------------------------------------------

check(DB_PATH.exists(), "DuckDB database exists")

if not DB_PATH.exists():
    raise SystemExit("Database missing. Validation stopped.")

con = duckdb.connect(str(DB_PATH), read_only=True)

database_records = con.execute(
    "SELECT COUNT(*) FROM fact_flights"
).fetchone()[0]

check(
    database_records == 539747,
    f"Database contains expected 539,747 records "
    f"(found {database_records:,})"
)

# ----------------------------------------------------------
# 2. CHECK EXPORTED FILES
# ----------------------------------------------------------

exported_data = {}

for filename, expected_rows in EXPECTED_FILES.items():

    file_path = EXPORT_DIR / filename

    exists = file_path.exists()

    check(exists, f"{filename} exists")

    if not exists:
        continue

    try:
        df = pd.read_csv(file_path)

        exported_data[filename] = df

        check(
            not df.empty,
            f"{filename} contains data"
        )

        check(
            len(df) == expected_rows,
            f"{filename} has {expected_rows} expected rows "
            f"(found {len(df)})"
        )

    except Exception as error:
        check(
            False,
            f"{filename} can be read: {error}"
        )

# ----------------------------------------------------------
# 3. CHECK OVERALL RECORD RECONCILIATION
# ----------------------------------------------------------

overall = exported_data.get("overall_performance.csv")

if overall is not None and not overall.empty:

    flight_column = find_column(
        overall,
        [
            "total_flight_records",
            "total_flights",
            "flight_records",
            "total_records"
        ]
    )

    if flight_column is not None:

        exported_total = int(overall.iloc[0][flight_column])

        check(
            exported_total == database_records,
            "Overall export reconciles with DuckDB record count"
        )

    else:
        warning(
            "Could not identify total-flight column in overall export"
        )

# ----------------------------------------------------------
# 4. CHECK DELAY CAUSE CONTRIBUTIONS
# ----------------------------------------------------------

causes = exported_data.get(
    "delay_cause_contributions.csv"
)

if causes is not None and not causes.empty:

    percentage_column = find_column(
        causes,
        [
            "contribution_pct",
            "contribution_percentage",
            "percentage",
            "share_pct"
        ]
    )

    if percentage_column is not None:

        contribution_total = pd.to_numeric(
            causes[percentage_column],
            errors="coerce"
        ).sum()

        check(
            abs(contribution_total - 100) <= 0.02,
            f"Delay cause contributions total approximately 100% "
            f"(found {contribution_total:.2f}%)"
        )

    else:
        warning(
            "Could not identify contribution percentage column"
        )

# ----------------------------------------------------------
# 5. CHECK ROUTE CLASSIFICATION
# ----------------------------------------------------------

routes = exported_data.get("route_performance.csv")

if routes is not None and not routes.empty:

    classification_column = find_column(
        routes,
        [
            "classification",
            "route_classification",
            "performance_classification"
        ]
    )

    if classification_column is not None:

        classification_counts = routes[
            classification_column
        ].value_counts()

        classified_total = int(classification_counts.sum())

        check(
            classified_total == len(routes),
            "Every exported route has a classification"
        )

        print("\nROUTE CLASSIFICATION COUNTS")

        for category, count in classification_counts.items():
            print(f"{category:<35} {count:>5}")

    else:
        warning(
            "Could not identify route classification column"
        )

# ----------------------------------------------------------
# 6. CLOSE DATABASE
# ----------------------------------------------------------

con.close()

# ----------------------------------------------------------
# 7. VALIDATION SUMMARY
# ----------------------------------------------------------

print("\n" + "=" * 65)
print("SKYLENS | VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks passed:   {passed}")
print(f"Checks failed:   {failed}")
print(f"Warnings:        {warnings}")

if failed == 0:
    print("\nVALIDATION COMPLETED: No failed checks detected.")
else:
    print("\nVALIDATION COMPLETED: Issues require investigation.")

print("=" * 65)
