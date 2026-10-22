
import pandas as pd
import pytest

from dataqualityprofiler.pipeline import run_pipeline


def test_pipeline_trims_whitespace_and_removes_duplicates(tmp_path):
    source = tmp_path / "input.csv"
    destination = tmp_path / "output.csv"

    source.write_text(
        "name,amount\n Alice ,10\nBob,20\n Alice ,10\n",
        encoding="utf-8",
    )

    result = run_pipeline(source, destination)
    cleaned = pd.read_csv(destination)

    assert result["original_rows"] == 3
    assert result["cleaned_rows"] == 2
    assert result["duplicates_removed"] == 1
    assert cleaned["name"].tolist() == ["Alice", "Bob"]


def test_pipeline_raises_if_input_does_not_exist(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_pipeline(tmp_path / "missing.csv", tmp_path / "output.csv")


def test_pipeline_rejects_same_input_and_output_path(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("name\nAlice\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must be different"):
        run_pipeline(source, source)