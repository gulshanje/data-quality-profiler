
import pytest

from dataqualityprofiler.validation import validate_csv


def test_validation_passes_for_valid_data(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "order_id,amount\n"
        "1,10\n"
        "2,25\n",
        encoding="utf-8",
    )

    report = validate_csv(
        csv_file,
        required_columns=["order_id", "amount"],
        not_null_columns=["order_id"],
        unique_columns=["order_id"],
        non_negative_columns=["amount"],
    )

    assert report["passed"] is True
    assert report["total_rules"] == 5
    assert report["failed_rules"] == 0


def test_validation_detects_null_values(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "order_id,amount\n"
        "1,10\n"
        "2,\n",
        encoding="utf-8",
    )

    report = validate_csv(csv_file, not_null_columns=["amount"])

    assert report["passed"] is False
    assert report["failed_rules"] == 1
    assert report["results"][0]["failure_count"] == 1


def test_validation_detects_duplicate_values(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "order_id,amount\n"
        "1,10\n"
        "1,20\n"
        "2,30\n",
        encoding="utf-8",
    )

    report = validate_csv(csv_file, unique_columns=["order_id"])

    assert report["passed"] is False
    assert report["results"][0]["rule"] == "unique"
    assert report["results"][0]["failure_count"] == 1


def test_validation_detects_negative_values(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "order_id,amount\n"
        "1,10\n"
        "2,-5\n",
        encoding="utf-8",
    )

    report = validate_csv(csv_file, non_negative_columns=["amount"])

    assert report["passed"] is False
    assert report["results"][0]["failure_count"] == 1


def test_validation_reports_missing_column(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("order_id\n1\n2\n", encoding="utf-8")

    report = validate_csv(
        csv_file,
        required_columns=["email"],
        not_null_columns=["email"],
    )

    assert report["passed"] is False
    assert report["failed_rules"] == 2


def test_validation_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_csv(tmp_path / "missing.csv")