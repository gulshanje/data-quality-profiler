
import argparse
import json
import sys
from pathlib import Path

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
    raise SystemExit(main())