import pandas as pd
import os


def load_data():
    """
    Loads the Excel file safely, without assuming any sheet name.
    Automatically loads the FIRST sheet in the workbook.
    Ensures required columns exist so the rest of the app never breaks.
    """

    filename = "Database with pivot tables.xlsx"

    # If file missing, fail clearly
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Expected file '{filename}' not found in project root."
        )

    # Load workbook and detect first sheet
    xls = pd.ExcelFile(filename)
    first_sheet = xls.sheet_names[0]  # <-- This avoids the Test1 problem entirely

    # Load the first sheet
    df = pd.read_excel(filename, sheet_name=first_sheet)

    # Ensure required columns exist
    required_cols = [
        "property",
        "utility",
        "provider_code",
        "meter_number",
        "start_date",
        "end_date",
        "usage",
        "cost",
        "occupancy",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Convert dates safely
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

    # Add year/month
    df["year"] = df["start_date"].dt.year
    df["month"] = df["start_date"].dt.month

    return df
