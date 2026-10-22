
import json

from dataqualityprofiler.cli import main


def test_profile_command_prints_json(tmp_path, capsys):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("id,amount\n1,10\n2,20\n", encoding="utf-8")

    exit_code = main(["profile", str(csv_file)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out)["row_count"] == 2


def test_validate_command_returns_failure_for_invalid_data(
    tmp_path,
    capsys,
):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("id,amount\n1,-5\n", encoding="utf-8")

    exit_code = main([
        "validate",
        str(csv_file),
        "--non-negative",
        "amount",
    ])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert json.loads(captured.out)["passed"] is False


def test_profile_command_writes_report(tmp_path):
    csv_file = tmp_path / "sales.csv"
    output_file = tmp_path / "report.json"
    csv_file.write_text("id\n1\n", encoding="utf-8")

    exit_code = main([
        "profile",
        str(csv_file),
        "--output",
        str(output_file),
    ])

    assert exit_code == 0
    assert json.loads(output_file.read_text(encoding="utf-8"))["row_count"] == 1