
import argparse
import json
import sys
from pathlib import Path

from dataqualityprofiler.logging_config import configure_logging
from dataqualityprofiler.pipeline_runner import run_quality_pipeline
from dataqualityprofiler.profiling import profile_csv
from dataqualityprofiler.reporting import export_json
from dataqualityprofiler.validation import validate_csv


def parse_columns(value: str) -> list[str]:
    """Parse comma-separated column names."""
    columns = [column.strip() for column in value.split(",")]

    if not all(columns):
        raise argparse.ArgumentTypeError(
            "Column names must not be empty."
        )

    return columns


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataqualityprofiler",
        description="Profile and validate CSV datasets.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )
    
    
    
    run_parser = subparsers.add_parser(
        "run",
        help="Run the complete data quality pipeline",
    )
    run_parser.add_argument("input", help="Path to the input CSV file")
    run_parser.add_argument(
        "--output",
        required=True,
        help="Path for the cleaned output CSV",
    )
    run_parser.add_argument(
        "--report",
        required=True,
        help="Path for the JSON quality report",
    )
    run_parser.add_argument(
        "--required-columns",
        default="",
        help="Comma-separated list of required columns",
    )
    run_parser.add_argument(
        "--not-null-columns",
        default="",
        help="Comma-separated list of columns that cannot contain nulls",
    )
    run_parser.add_argument(
        "--unique-columns",
        default="",
        help="Comma-separated list of columns that must be unique",
    )
    run_parser.add_argument(
        "--non-negative-columns",
        default="",
        help="Comma-separated list of columns that must be non-negative",
    )
    profile_parser = subparsers.add_parser(
        "profile",
        help="Profile a CSV file.",
    )
    profile_parser.add_argument("csv_file", type=Path)
    profile_parser.add_argument("--output", type=Path)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a CSV file against quality rules.",
    )
    validate_parser.add_argument("csv_file", type=Path)
    validate_parser.add_argument(
        "--required-columns",
        type=parse_columns,
        default=[],
    )
    validate_parser.add_argument(
        "--not-null",
        type=parse_columns,
        default=[],
    )
    validate_parser.add_argument(
        "--unique",
        type=parse_columns,
        default=[],
    )
    validate_parser.add_argument(
        "--non-negative",
        type=parse_columns,
        default=[],
    )
    validate_parser.add_argument("--output", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "profile":
            report = profile_csv(args.csv_file)
            
        
        elif args.command == "run":
            report = run_quality_pipeline(
                input_path=args.input,
                output_path=args.output,
                report_path=args.report,
                required_columns=tuple(
                    column.strip()
                    for column in args.required_columns.split(",")
                    if column.strip()
                ),
                not_null_columns=tuple(
                    column.strip()
                    for column in args.not_null_columns.split(",")
                    if column.strip()
                ),
                unique_columns=tuple(
                    column.strip()
                    for column in args.unique_columns.split(",")
                    if column.strip()
                ),
                non_negative_columns=tuple(
                    column.strip()
                    for column in args.non_negative_columns.split(",")
                    if column.strip()
                ),
            )

            print(f"Validation passed: {report['validation']['passed']}")
            print(f"Report saved to: {args.report}")

            if report["pipeline"]["executed"]:
                print(f"Cleaned CSV saved to: {args.output}")
                return 0

            print("Validation failed; cleaned CSV was not generated.")
            return 1
        else:
            report = validate_csv(
                args.csv_file,
                required_columns=args.required_columns,
                not_null_columns=args.not_null,
                unique_columns=args.unique,
                non_negative_columns=args.non_negative,
            )

        if args.output:
            output_path = export_json(report, args.output)
            print(f"Report written to {output_path}")
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))

        if args.command == "validate" and not report["passed"]:
            return 1

        return 0

    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    configure_logging()
    raise SystemExit(main())