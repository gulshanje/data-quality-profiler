
import json

import pandas as pd

from dataqualityprofiler.pipeline_runner import run_quality_pipeline


def test_quality_pipeline_exports_clean_data_when_validation_passes(
    tmp_path,
):
    source = tmp_path / "input.csv"
    output = tmp_path / "cleaned.csv"
    report_file = tmp_path / "report.json"

    source.write_text(
        "order_id,amount\n1,10\n2,20\n",
        encoding="utf-8",
    )

    report = run_quality_pipeline(
        source,
        output,
        report_file,
        required_columns=("order_id", "amount"),
        not_null_columns=("order_id",),
        unique_columns=("order_id",),
        non_negative_columns=("amount",),
    )

    assert report["validation"]["passed"] is True
    assert report["pipeline"]["executed"] is True
    assert output.exists()
    assert report_file.exists()

    saved_report = json.loads(report_file.read_text(encoding="utf-8"))
    assert saved_report["validation"]["passed"] is True

    cleaned = pd.read_csv(output)
    assert len(cleaned) == 2


def test_quality_pipeline_skips_export_when_validation_fails(
    tmp_path,
):
    source = tmp_path / "input.csv"
    output = tmp_path / "cleaned.csv"
    report_file = tmp_path / "report.json"

    source.write_text(
        "order_id,amount\n1,-10\n2,20\n",
        encoding="utf-8",
    )

    report = run_quality_pipeline(
        source,
        output,
        report_file,
        required_columns=("order_id", "amount"),
        non_negative_columns=("amount",),
    )

    assert report["validation"]["passed"] is False
    assert report["pipeline"]["executed"] is False
    assert not output.exists()
    assert report_file.exists()