
from pathlib import Path
from typing import Any

import duckdb


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
            "columns": columns,
        }