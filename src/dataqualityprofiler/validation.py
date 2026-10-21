
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import duckdb


def validate_csv(
    path: str | Path,
    *,
    required_columns: Iterable[str] = (),
    not_null_columns: Iterable[str] = (),
    unique_columns: Iterable[str] = (),
    non_negative_columns: Iterable[str] = (),
) -> dict[str, Any]:
    """Validate a CSV file against a set of data quality rules."""
    file_path = Path(path).expanduser().resolve()

    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    required_columns = list(required_columns)
    not_null_columns = list(not_null_columns)
    unique_columns = list(unique_columns)
    non_negative_columns = list(non_negative_columns)

    def quote_identifier(name: str) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Column names must be non-empty strings.")
        return '"' + name.replace('"', '""') + '"'

    results: list[dict[str, Any]] = []

    def add_result(
        rule: str,
        column: str | None,
        passed: bool,
        failure_count: int,
        message: str,
    ) -> None:
        results.append({
            "rule": rule,
            "column": column,
            "passed": passed,
            "failure_count": failure_count,
            "message": message,
        })

    with duckdb.connect(":memory:") as connection:
        connection.read_csv(str(file_path)).create_view("source_data")

        schema = connection.execute(
            "DESCRIBE source_data"
        ).fetchall()
        available_columns = {row[0] for row in schema}

        # Check the dataset schema before running column-specific rules.
        for name in required_columns:
            exists = name in available_columns
            add_result(
                rule="required_column",
                column=name,
                passed=exists,
                failure_count=0 if exists else 1,
                message=(
                    "Column exists."
                    if exists
                    else "Required column is missing."
                ),
            )

        # Avoid executing SQL against columns that do not exist.
        checks = (
            ("not_null", not_null_columns),
            ("unique", unique_columns),
            ("non_negative", non_negative_columns),
        )

        for rule, names in checks:
            for name in names:
                if name not in available_columns:
                    add_result(
                        rule=rule,
                        column=name,
                        passed=False,
                        failure_count=1,
                        message="Cannot validate: column is missing.",
                    )
                    continue

                col = quote_identifier(name)

                if rule == "not_null":
                    query = (
                        f"SELECT COUNT(*) FROM source_data "
                        f"WHERE {col} IS NULL"
                    )
                    failure_count = connection.execute(
                        query
                    ).fetchone()[0]
                    message = "Null values found." if failure_count else "No null values."

                elif rule == "unique":
                    query = f"""
                        SELECT COUNT(*)
                        FROM (
                            SELECT {col}
                            FROM source_data
                            WHERE {col} IS NOT NULL
                            GROUP BY {col}
                            HAVING COUNT(*) > 1
                        ) AS duplicates
                    """
                    failure_count = connection.execute(
                        query
                    ).fetchone()[0]
                    message = (
                        "Duplicate values found."
                        if failure_count
                        else "All non-null values are unique."
                    )

                else:
                    query = f"""
                        SELECT COUNT(*)
                        FROM source_data
                        WHERE {col} IS NOT NULL
                          AND (
                              TRY_CAST({col} AS DOUBLE) IS NULL
                              OR TRY_CAST({col} AS DOUBLE) < 0
                          )
                    """
                    failure_count = connection.execute(
                        query
                    ).fetchone()[0]
                    message = (
                        "Negative or non-numeric values found."
                        if failure_count
                        else "All non-null values are non-negative numbers."
                    )

                add_result(
                    rule=rule,
                    column=name,
                    passed=failure_count == 0,
                    failure_count=failure_count,
                    message=message,
                )

    return {
        "file_name": file_path.name,
        "passed": all(result["passed"] for result in results),
        "total_rules": len(results),
        "failed_rules": sum(not result["passed"] for result in results),
        "results": results,
    }