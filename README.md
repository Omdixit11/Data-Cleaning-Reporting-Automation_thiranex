# Data Cleaning & Reporting Automation

This project demonstrates a Python-based workflow to automate data cleaning and reporting for internship task purposes.

## What it does
- Reads raw data from `sample_data.csv`
- Handles missing values, duplicates, and inconsistent formatting
- Cleans column values and parses dates/numbers
- Saves cleaned data to `output/cleaned_data.xlsx`
- Generates a summary report in `output/summary_report.xlsx`
- Creates visual summaries in `output/charts`

## Requirements
- Python 3.9 or newer

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the automation

```bash
python data_cleaning_report.py
```

## Output files
- `output/cleaned_data.xlsx`
- `output/summary_report.xlsx`
- `output/charts/sales_by_category.png`
- `output/charts/sales_by_region.png`
- `output/charts/monthly_sales_trend.png`

## Notes
- You can replace `sample_data.csv` with your own dataset.
- The script automatically detects and cleans common data issues, then summarizes the results.
