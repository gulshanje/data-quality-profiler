from dataqualityprofiler.reporting import export_json
from dataqualityprofiler.validation import validate_csv

report = validate_csv(
    "examples/sales.csv",
    required_columns=["order_id", "amount"],
    not_null_columns=["order_id"],
    unique_columns=["order_id"],
    non_negative_columns=["amount"],
)

export_json(report, "examples/sales-validation.json")