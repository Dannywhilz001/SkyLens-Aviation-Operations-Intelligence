
"""Inspect BTS CSV exports without modifying the original source files."""

from __future__ import annotations

from pathlib import Path
import sys

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

REQUIRED_FIELDS = {
    "FL_DATE",
    "OP_UNIQUE_CARRIER",
    "ORIGIN",
    "DEST",
    "ARR_DEL15",
    "CANCELLED",
    "DIVERTED",
}


def sql_string(value: str) -> str:
    """Return a safely single-quoted SQL string literal."""
    return "'" + value.replace("'", "''") + "'"


def main() -> int:
    files = sorted(RAW_DIR.glob("*.csv"))

    if not files:
        print(f"No CSV files found in: {RAW_DIR}")
        print("Place the original BTS CSV file(s) in data/raw/.")
        return 1

    con = duckdb.connect(database=":memory:")
    has_errors = False

    for file_path in files:
        print("\n" + "=" * 72)
        print(f"FILE: {file_path.name}")

        csv_path = sql_string(file_path.as_posix())
        relation_sql = (
            f"read_csv_auto({csv_path}, header = true, sample_size = 100000, "
            "ignore_errors = false)"
        )

        try:
            columns_info = con.execute(
                f"DESCRIBE SELECT * FROM {relation_sql}"
            ).fetchall()

            columns = [row[0] for row in columns_info]

            row_count = con.execute(
                f"SELECT COUNT(*) FROM {relation_sql}"
            ).fetchone()[0]

        except Exception as exc:
            print(f"Could not read this CSV: {exc}")
            has_errors = True
            continue

        print(f"Rows: {row_count:,}")
        print(f"Columns: {len(columns)}")

        print("\nDetected columns and types:")
        for name, data_type, *_ in columns_info:
            print(f"  - {name}: {data_type}")

        missing = sorted(REQUIRED_FIELDS.difference(columns))

        if missing:
            print("\nREQUIRED FIELD CHECK: FAIL")
            print("Missing fields: " + ", ".join(missing))
            has_errors = True
        else:
            print("\nREQUIRED FIELD CHECK: PASS")

        if "FL_DATE" in columns:
            try:
                date_result = con.execute(
                    f"SELECT MIN(FL_DATE), MAX(FL_DATE) "
                    f"FROM {relation_sql}"
                ).fetchone()

                print(
                    f"FL_DATE range: {date_result[0]} "
                    f"to {date_result[1]}"
                )

            except Exception as exc:
                print(f"Could not profile FL_DATE: {exc}")
                has_errors = True

    con.close()

    print("\nInspection complete. Original CSV files were not changed.")
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
