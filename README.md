# DataQualityProfiler

A Python-based data quality and CSV processing tool for profiling datasets, validating data rules, cleaning CSV files, and generating JSON reports.

## Features

* **Data profiling:** Inspect row counts, columns, null values, and duplicate rows.
* **Data validation:** Check required columns, null constraints, uniqueness, and non-negative numeric values.
* **CSV cleaning:** Trim whitespace from text fields and remove duplicate rows.
* **JSON reporting:** Export structured reports for further analysis or automation.
* **Integrated quality pipeline:** Profile and validate a dataset, clean it when validation passes, and save a report.
* **Command-line interface:** Run profiling, validation, and the complete pipeline from a terminal.
* **Automated tests:** Use pytest to verify core functionality and pipeline behavior.

## Technology stack

* Python 3.10+
* DuckDB
* pandas
* pytest
* Ruff

## Project structure

```text
dataqualityprofiler/
├── examples/
│   ├── sales.csv
│   ├── example-report-validate.py
│   └── example-pipeline.py
├── src/
│   └── dataqualityprofiler/
│       ├── __init__.py
│       ├── profiling.py
│       ├── validation.py
│       ├── reporting.py
│       ├── pipeline.py
│       ├── pipeline_runner.py
│       ├── logging_config.py
│       └── cli.py
├── tests/
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/gulshanje/data-quality-profiler
cd data-quality-profiler
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Usage

### 1. Profile a CSV file

```bash
dataqualityprofiler profile examples/sales.csv
```

### 2. Validate a CSV file

The validation command supports rules such as required columns, non-null values, unique values, and non-negative numeric values.

```bash
dataqualityprofiler validate --help
```

Use the options shown by the command's help output to specify the rules supported by your installed version.

### 3. Run the complete quality pipeline

```bash
dataqualityprofiler run examples/sales.csv --output data/cleaned.csv --report reports/quality-report.json --required-columns order_id,amount --unique-columns order_id --non-negative-columns amount
```

Replace `order_id` and `amount` with column names present in your CSV.

The pipeline profiles and validates the source file. When validation passes, it cleans the data and writes the cleaned CSV. It also exports a JSON quality report. When validation fails, the cleaned output is skipped and the report records the validation results.

**Note:** The example command assumes that your sample CSV contains `order_id` and `amount` columns. Adjust the names to match your dataset.

### 4. Run the example scripts

```bash
python examples/example-pipeline.py
python examples/example-report-validate.py
```

Run these commands from the repository root.

## Development

Run the automated test suite:

```bash
python -m pytest -v
```

Check code quality with Ruff:

```bash
ruff check .
```

## Current scope

This is an early-stage project. It currently focuses on CSV files and configurable data quality checks. Database connectors, additional file formats, richer reporting, and a graphical interface may be considered for future releases.

## Roadmap

* [x] CSV profiling
* [x] Data validation rules
* [x] JSON report export
* [x] CSV cleaning pipeline
* [x] Integrated profiling and validation workflow
* [x] Command-line interface
* [x] Docker support
* [ ] More edge-case and integration tests
* [ ] Additional input formats and data sources

