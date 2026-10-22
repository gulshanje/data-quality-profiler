
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def export_json(
    report: Mapping[str, Any],
    output_path: str | Path,
) -> Path:
    """Export a report to a UTF-8 JSON file.

    Returns the resolved path of the generated file.
    """
    file_path = Path(output_path).expanduser().resolve()

    if not file_path.parent.is_dir():
        raise FileNotFoundError(
            f"Output directory does not exist: {file_path.parent}"
        )

    # Serialize before writing so invalid data does not leave
    # a partially written report.
    content = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

    file_path.write_text(content + "\n", encoding="utf-8")

    return file_path