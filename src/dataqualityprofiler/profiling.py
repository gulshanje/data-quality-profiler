
from pathlib import Path
from typing import Any

import duckdb


def count_duplicate_rows(connection, column_names: list[str]) -> int:
    """Count extra occurrences of duplicate rows."""
    if not column_names:
        return 0

    identifiers = ", ".join(
        '"' + name.replace('"', '""') + '"'
        for name in column_names
    )

    query = f"""
        SELECT COALESCE(SUM(row_count - 1), 0)
        FROM (
            SELECT COUNT(*) AS row_count
            FROM source_data
            GROUP BY {identifiers}
            HAVING COUNT(*) > 1
        )
    """

    return connection.execute(query).fetchone()[0]


def profile_csv(path: str | Path) -> dict[str, Any]:
    """Profile a CSV file and return its schema and null statistics."""
    file_path = Path(path).expanduser().resolve()

    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with duckdb.connect(":memory:") as connection:
        relation = connection.read_csv(str(file_path))
        relation.create_view("source_data")

        row_count = connection.execute(
            "SELECT COUNT(*) FROM source_data"
        ).fetchone()[0]
        
        
        schema = connection.execute(
            "DESCRIBE source_data"
        ).fetchall()
        
        column_names = [column[0] for column in schema]

        duplicate_count = count_duplicate_rows(
            connection,
            column_names,
        )

       
        columns = {}

        for name, data_type, *_ in schema:
            # Escape SQL identifier quotes.
            identifier = '"' + name.replace('"', '""') + '"'

            null_count = connection.execute(
                f"SELECT COUNT(*) FROM source_data "
                f"WHERE {identifier} IS NULL"
            ).fetchone()[0]

            columns[name] = {
                "data_type": data_type,
                "null_count": null_count,
                "null_percentage": (
                    round(null_count / row_count * 100, 2)
                    if row_count
                    else 0.0
                ),
            }
       
        return {
            "file_name": file_path.name,
            "row_count": row_count,
            "column_count": len(schema),
            "duplicate_row_count": duplicate_count,
            "columns": columns,
        }
