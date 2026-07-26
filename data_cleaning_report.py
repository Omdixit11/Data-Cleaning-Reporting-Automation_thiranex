import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

INPUT_FILE = "sample_data.csv"
OUTPUT_DIR = "output"
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")


def load_data(path: str) -> pd.DataFrame:
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def standardize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.select_dtypes(include=["object", "string"]):
        df[column] = df[column].astype("string").str.strip()
    return df


def clean_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    threshold = len(df) * 0.6
    dropped_columns = [col for col in df.columns if df[col].count() < threshold]
    if dropped_columns:
        df = df.drop(columns=dropped_columns)

    numeric_columns = df.select_dtypes(include=["number"]).columns
    for column in numeric_columns:
        median_value = df[column].median()
        df[column] = df[column].fillna(median_value)

    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        mode_value = df[column].mode(dropna=True)
        if not mode_value.empty:
            df[column] = df[column].fillna(mode_value.iloc[0])
        else:
            df[column] = df[column].fillna("")

    return df, dropped_columns


def clean_inconsistent_data(df: pd.DataFrame) -> pd.DataFrame:
    lower_columns = {col.lower(): col for col in df.columns}
    if "region" in lower_columns:
        region_col = lower_columns["region"]
        df[region_col] = df[region_col].astype("string").str.replace(r"[^A-Za-z ]", "", regex=True).str.title()

    if "category" in lower_columns:
        category_col = lower_columns["category"]
        df[category_col] = df[category_col].astype("string").str.replace("HomeOffice", "Home Office", regex=False).str.title()

    if "date" in lower_columns:
        date_col = lower_columns["date"]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=False)

    for column in df.columns:
        if column.lower() in {"sales", "profit"}:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates(ignore_index=True)
    return df, duplicate_count


def generate_summary(df: pd.DataFrame, dropped_columns: list[str], duplicate_count: int) -> tuple[pd.DataFrame, dict[str, object]]:
    describe_df = df.describe(include="all").transpose()
    describe_df["missing_values"] = df.isna().sum()

    metrics = {
        "rows_after_cleaning": len(df),
        "columns_after_cleaning": len(df.columns),
        "dropped_columns": ", ".join(dropped_columns) if dropped_columns else "None",
        "duplicates_removed": duplicate_count,
        "missing_values_remaining": int(df.isna().sum().sum()),
    }

    return describe_df, metrics


def save_outputs(df: pd.DataFrame, summary_df: pd.DataFrame, metrics: dict[str, object]) -> None:
    os.makedirs(CHART_DIR, exist_ok=True)
    df.to_excel(os.path.join(OUTPUT_DIR, "cleaned_data.xlsx"), index=False)
    df.to_csv(os.path.join(OUTPUT_DIR, "cleaned_data.csv"), index=False)

    with pd.ExcelWriter(os.path.join(OUTPUT_DIR, "summary_report.xlsx"), engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary Statistics")
        pd.DataFrame([metrics]).to_excel(writer, sheet_name="Key Metrics", index=False)

    with open(os.path.join(OUTPUT_DIR, "report.txt"), "w", encoding="utf-8") as report_file:
        report_file.write("Data Cleaning & Reporting Automation\n")
        report_file.write("===============================\n")
        for key, value in metrics.items():
            report_file.write(f"{key}: {value}\n")

    create_visualizations(df)


def create_visualizations(df: pd.DataFrame) -> None:
    lower_columns = {col.lower(): col for col in df.columns}
    if "category" in lower_columns and "sales" in lower_columns:
        category_col = lower_columns["category"]
        sales_col = lower_columns["sales"]
        grouped = df.groupby(category_col, dropna=False)[sales_col].sum().sort_values(ascending=False)
        grouped.plot(kind="bar", title="Sales by Category", ylabel="Total Sales", figsize=(10, 5))
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, "sales_by_category.png"))
        plt.close()

    if "region" in lower_columns:
        region_col = lower_columns["region"]
        df[region_col].value_counts().plot(kind="pie", autopct="%1.1f%%", title="Sales Distribution by Region", figsize=(8, 8))
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, "sales_by_region.png"))
        plt.close()

    if "date" in lower_columns and "sales" in lower_columns:
        date_col = lower_columns["date"]
        sales_col = lower_columns["sales"]
        monthly = df.dropna(subset=[date_col]).groupby(pd.Grouper(key=date_col, freq="ME"))[sales_col].sum()
        if not monthly.empty:
            monthly.plot(marker="o", title="Monthly Sales Trend", ylabel="Sales", figsize=(10, 5))
            plt.tight_layout()
            plt.savefig(os.path.join(CHART_DIR, "monthly_sales_trend.png"))
            plt.close()


def main() -> None:
    print("Loading data from", INPUT_FILE)
    df = load_data(INPUT_FILE)

    print("Standardizing text columns...")
    df = standardize_text_columns(df)

    print("Cleaning missing values...")
    df, dropped_columns = clean_missing_values(df)

    print("Cleaning inconsistent data...")
    df = clean_inconsistent_data(df)

    print("Removing duplicate records...")
    df, duplicate_count = remove_duplicates(df)

    print("Generating summary...")
    summary_df, metrics = generate_summary(df, dropped_columns, duplicate_count)

    print("Saving outputs...")
    save_outputs(df, summary_df, metrics)

    print("Completed. Check the output folder for cleaned data and visual reports.")


if __name__ == "__main__":
    main()
