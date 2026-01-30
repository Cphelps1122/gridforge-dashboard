import pandas as pd
import numpy as np


# ---------------------------------------------------------
# SPIKE DETECTION (Usage or Cost)
# ---------------------------------------------------------

def detect_spikes(df: pd.DataFrame, metric="usage", threshold_pct=40):
    """
    Detects spikes where usage or cost jumps more than X% month-over-month.
    Returns a dataframe of flagged months.
    """
    if df.empty or metric not in df.columns:
        return pd.DataFrame()

    df = df.copy().sort_values("date")
    df["prev"] = df[metric].shift(1)

    df["pct_change"] = np.where(
        df["prev"] > 0,
        (df[metric] - df["prev"]) / df["prev"] * 100,
        np.nan,
    )

    spikes = df[df["pct_change"] >= threshold_pct]

    return spikes[["date", metric, "pct_change"]]


# ---------------------------------------------------------
# MISSING BILL DETECTION
# ---------------------------------------------------------

def detect_missing_bills(df: pd.DataFrame):
    """
    Detects missing billing months by checking gaps in monthly periods.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()

    full_range = pd.date_range(
        start=df["month_start"].min(),
        end=df["month_start"].max(),
        freq="MS"
    )

    missing = full_range[~full_range.isin(df["month_start"])]

    return pd.DataFrame({"missing_month": missing})


# ---------------------------------------------------------
# IRREGULAR BILLING PERIODS
# ---------------------------------------------------------

def detect_irregular_billing_periods(df: pd.DataFrame, min_days=25, max_days=35):
    """
    Flags bills with unusually short or long billing periods.
    """
    if df.empty or "days_billed" not in df.columns:
        return pd.DataFrame()

    irregular = df[(df["days_billed"] < min_days) | (df["days_billed"] > max_days)]

    return irregular[["date", "days_billed", "usage", "cost"]]


# ---------------------------------------------------------
# NEGATIVE OR ZERO READINGS
# ---------------------------------------------------------

def detect_bad_readings(df: pd.DataFrame):
    """
    Flags negative or zero readings or negative deltas.
    """
    if df.empty:
        return pd.DataFrame()

    bad = df[
        (df["current_reading"] <= 0)
        | (df["previous_reading"] < 0)
        | (df["reading_delta"] < 0)
    ]

    return bad[["date", "previous_reading", "current_reading", "reading_delta"]]


# ---------------------------------------------------------
# METER ANOMALIES
# ---------------------------------------------------------

def detect_meter_anomalies(df: pd.DataFrame, z_threshold=2.5):
    """
    Detects meters with unusually high or low usage using Z-scores.
    """
    if df.empty or "meter_number" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    meter_usage = df.groupby("meter_number")["usage"].sum().reset_index()

    meter_usage["z_score"] = (
        (meter_usage["usage"] - meter_usage["usage"].mean())
        / meter_usage["usage"].std(ddof=0)
    )

    anomalies = meter_usage[
        (meter_usage["z_score"] >= z_threshold)
        | (meter_usage["z_score"] <= -z_threshold)
    ]

    return anomalies


# ---------------------------------------------------------
# OCCUPANCY ANOMALIES
# ---------------------------------------------------------

def detect_occupancy_anomalies(df: pd.DataFrame, threshold_pct=20):
    """
    Flags months where occupancy changes more than X% month-over-month.
    """
    if df.empty or "occupancy" not in df.columns:
        return pd.DataFrame()

    df = df.copy().sort_values("date")
    df["prev_occ"] = df["occupancy"].shift(1)

    df["occ_change_pct"] = np.where(
        df["prev_occ"] > 0,
        (df["occupancy"] - df["prev_occ"]) / df["prev_occ"] * 100,
        np.nan,
    )

    anomalies = df[abs(df["occ_change_pct"]) >= threshold_pct]

    return anomalies[["date", "occupancy", "occ_change_pct"]]


# ---------------------------------------------------------
# COMBINED ALERT SUMMARY
# ---------------------------------------------------------

def build_alert_summary(df: pd.DataFrame):
    """
    Returns a dictionary of all alerts for a property + utility.
    """
    return {
        "spikes_usage": detect_spikes(df, metric="usage"),
        "spikes_cost": detect_spikes(df, metric="cost"),
        "missing_bills": detect_missing_bills(df),
        "irregular_billing": detect_irregular_billing_periods(df),
        "bad_readings": detect_bad_readings(df),
        "meter_anomalies": detect_meter_anomalies(df),
        "occupancy_anomalies": detect_occupancy_anomalies(df),
    }
