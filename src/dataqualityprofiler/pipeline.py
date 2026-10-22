
from pathlib import Path

import pandas as pd


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
) -> dict[str, int | str]:
    """Clean a CSV file and save the result to another CSV file."""
    source = Path(input_path).resolve()
    destination = Path(output_path).resolve()

    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")

    if source == destination:
        raise ValueError("Input and output paths must be different.")

    destination.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source)
    original_rows = len(df)

    # Trim leading and trailing whitespace in text columns.
    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        df[column] = df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    # Remove rows that are identical across all columns.
    df = df.drop_duplicates()
    cleaned_rows = len(df)

    df.to_csv(destination, index=False)

    return {
        "input_file": str(source),
        "output_file": str(destination),
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "duplicates_removed": original_rows - cleaned_rows,
    }