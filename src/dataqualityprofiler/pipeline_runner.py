import logging
from pathlib import Path
from typing import Any

from dataqualityprofiler.pipeline import run_pipeline
from dataqualityprofiler.profiling import profile_csv
from dataqualityprofiler.reporting import export_json
from dataqualityprofiler.validation import validate_csv

logger = logging.getLogger(__name__)


def run_quality_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    *,
    required_columns: tuple[str, ...] = (),
    not_null_columns: tuple[str, ...] = (),
    unique_columns: tuple[str, ...] = (),
    non_negative_columns: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Profile, validate, and conditionally transform a CSV file."""
    source = Path(input_path).resolve()
    
    logger.info("Starting quality pipeline for %s", source)
    
    logger.info("Profiling input CSV")
    
    profile = profile_csv(source)
    
    logger.info("Validating input data")
    
    validation = validate_csv(
        source,
        required_columns=required_columns,
        not_null_columns=not_null_columns,
        unique_columns=unique_columns,
        non_negative_columns=non_negative_columns,
    )

    report: dict[str, Any] = {
        "input_file": str(source),
        "profile": profile,
        "validation": validation,
        "pipeline": {
            "executed": False,
            "output_file": None,
        },
    }

    if validation["passed"]:
        pipeline_result = run_pipeline(source, output_path)
        logger.info("Validation passed; starting CSV cleaning")
        report["pipeline"] = {
            "executed": True,
            **pipeline_result,
        }
    else:
        logger.warning("Validation failed; skipping CSV cleaning")

    export_json(report, report_path)
    logger.info("Quality report saved to %s", report_path)
    return report