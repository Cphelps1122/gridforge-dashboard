import pandas as pd
import numpy as np

EXCEL_FILE = "Database with pivot tables.xlsx"
SHEET_NAME = "Test1"


def load_raw_data():
    """
    Load the raw data from the Excel file and sheet.
    """
    df_raw = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    return df_raw


def rename_and_standardize_columns(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns from Test1 to internal GridForge names.
    """
    df = df_raw.rename(
        columns={
            "Property Name": "property",
            "Provider Code": "provider_code",
            "City": "city",
            "State": "state",
            "# Units": "units",
            "Occupancy": "occupancy",
            "Utility": "utility",
            "Meter #": "meter_number",
            "Unit of Measure": "unit_of_measure",
            "Acct Number": "account_number",
            "Billing Date": "date",
            "Month": "month",
            "Year": "year",
            "Billing Period": "billing_period",
            "Number Days Billed": "days_billed",
            "Due Date": "due_date",
            "Read period": "read_period",
            "Previous Reading": "previous_reading",
            "Current Reading": "current_reading",
            "Usage": "usage",
            "$ Amount": "cost",
        }
    )
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert dates and numeric fields to proper types.
    """
    # Dates
    for col in ["date", "due_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Numeric fields
    numeric_cols = [
        "units",
        "occupancy",
        "previous_reading",
        "current_reading",
        "usage",
        "cost",
        "days_billed",
        "year",
        "month",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived metrics used across the app:
    - usage_per_day
    - cost_per_day
    - reading_delta
    - occupancy_rate
    """
    # Usage per day
    if "usage" in df.columns and "days_billed" in df.columns:
        df["usage_per_day"] = np.where(
            df["days_billed"] > 0,
            df["usage"] / df["days_billed"],
            np.nan,
        )
    else:
        df["usage_per_day"] = np.nan

    # Cost per day
    if "cost" in df.columns and "days_billed" in df.columns:
        df["cost_per_day"] = np.where(
            df["days_billed"] > 0,
            df["cost"] / df["days_billed"],
            np.nan,
        )
    else:
        df["cost_per_day"] = np.nan

    # Reading delta
    if "previous_reading" in df.columns and "current_reading" in df.columns:
        df["reading_delta"] = df["current_reading"] - df["previous_reading"]
    else:
        df["reading_delta"] = np.nan

    # Occupancy rate (0–1)
    if "occupancy" in df.columns and "units" in df.columns:
        df["occupancy_rate"] = np.where(
            df["units"] > 0,
            df["occupancy"] / df["units"],
            np.nan,
        )
    else:
        df["occupancy_rate"] = np.nan

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleanup:
    - Drop rows with no property or utility
    - Standardize strings (strip, upper where needed)
    """
    if "property" in df.columns:
        df["property"] = df["property"].astype(str).str.strip()

    if "utility" in df.columns:
        df["utility"] = df["utility"].astype(str).str.strip()

    if "provider_code" in df.columns:
        df["provider_code"] = df["provider_code"].astype(str).str.strip()

    df = df.dropna(subset=["property", "utility"], how="any")

    return df


def load_data() -> pd.DataFrame:
    """
    Main entry point used by the app:
    - Load raw
    - Rename columns
    - Coerce types
    - Add derived fields
    - Clean
    """
    df_raw = load_raw_data()
    df = rename_and_standardize_columns(df_raw)
    df = coerce_types(df)
    df = add_derived_fields(df)
    df = clean_data(df)
    return df
