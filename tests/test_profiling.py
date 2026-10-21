
import pytest

from dataqualityprofiler.profiling import profile_csv


def test_profile_csv_returns_basic_statistics(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "id,amount\n"
        "1,10\n"
        "2,\n"
        "3,30\n",
        encoding="utf-8",
    )

    report = profile_csv(csv_file)

    assert report["file_name"] == "sales.csv"
    assert report["row_count"] == 3
    assert report["column_count"] == 2

    assert report["columns"]["id"]["null_count"] == 0
    assert report["columns"]["amount"]["null_count"] == 1
    assert report["columns"]["amount"]["null_percentage"] == pytest.approx(
        33.33
    )


def test_profile_csv_missing_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        profile_csv(missing_file)


def test_profile_csv_empty_dataset(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("id,amount\n", encoding="utf-8")

    report = profile_csv(csv_file)

    assert report["row_count"] == 0
    assert report["column_count"] == 2
    assert report["columns"]["id"]["null_percentage"] == 0.0
    
    

def test_profile_csv_counts_duplicate_rows(tmp_path):
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text(
        "id,name\n"
        "1,Alice\n"
        "2,Bob\n"
        "1,Alice\n"
        "1,Alice\n",
        encoding="utf-8",
    )

    report = profile_csv(csv_file)

    assert report["row_count"] == 4
    assert report["duplicate_row_count"] == 2