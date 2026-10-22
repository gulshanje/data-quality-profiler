
import json

import pytest

from dataqualityprofiler.reporting import export_json


def test_export_json_writes_report(tmp_path):
    report = {
        "file_name": "sales.csv",
        "row_count": 3,
        "passed": True,
    }
    output_file = tmp_path / "report.json"

    result = export_json(report, output_file)

    assert result == output_file.resolve()
    assert result.exists()
    assert json.loads(result.read_text(encoding="utf-8")) == report


def test_export_json_preserves_unicode(tmp_path):
    report = {"customer": "Müller"}
    output_file = tmp_path / "report.json"

    export_json(report, output_file)

    content = output_file.read_text(encoding="utf-8")

    assert "Müller" in content
    assert json.loads(content) == report


def test_export_json_rejects_non_serializable_values(tmp_path):
    report = {"invalid": object()}

    with pytest.raises(TypeError):
        export_json(report, tmp_path / "report.json")

    assert not (tmp_path / "report.json").exists()


def test_export_json_rejects_non_finite_numbers(tmp_path):
    report = {"value": float("nan")}

    with pytest.raises(ValueError):
        export_json(report, tmp_path / "report.json")


def test_export_json_rejects_missing_directory(tmp_path):
    output_file = tmp_path / "missing" / "report.json"

    with pytest.raises(FileNotFoundError):
        export_json({"passed": True}, output_file)