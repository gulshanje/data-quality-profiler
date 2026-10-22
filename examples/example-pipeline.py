
from dataqualityprofiler.pipeline import run_pipeline


def main() -> None:
    result = run_pipeline(
        input_path="examples/sales.csv",
        output_path="examples/sales-cleaned.csv",
    )

    print("ETL pipeline completed successfully.")
    print(f"Input rows: {result['original_rows']}")
    print(f"Output rows: {result['cleaned_rows']}")
    print(f"Duplicates removed: {result['duplicates_removed']}")
    print(f"Output file: {result['output_file']}")


if __name__ == "__main__":
    main()