import pandas as pd
import numpy as np
from prophet import Prophet
from .benchmarks import (
    get_utility_benchmark,
    build_benchmark_df,
)


# ---------------------------------------------------------
# MONTHLY AGGREGATION FOR FORECASTING
# ---------------------------------------------------------

def prepare_monthly_forecast_df(df: pd.DataFrame):
    """
    Convert daily/billing-level data into a clean monthly time series
    suitable for Prophet forecasting.
    """
    if df.empty:
        return pd.DataFrame(), None

    df = df.copy()
    df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month_start")["usage"]
        .sum()
        .reset_index()
        .rename(columns={"month_start": "ds", "usage": "y"})
    )

    # Ensure no missing months
    full_range = pd.date_range(
        start=monthly["ds"].min(),
        end=monthly["ds"].max(),
        freq="MS"
    )

    monthly = (
        monthly.set_index("ds")
        .reindex(full_range)
        .fillna(0)
        .rename_axis("ds")
        .reset_index()
    )

    return monthly, df


# ---------------------------------------------------------
# BUILD PROPHET MODEL
# ---------------------------------------------------------

def build_prophet_model():
    """
    Create a Prophet model with GridForge-friendly defaults.
    """
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="additive",
    )
    return model


# ---------------------------------------------------------
# RUN FORECAST
# ---------------------------------------------------------

def run_forecast(monthly_df: pd.DataFrame, periods=12):
    """
    Fit Prophet and generate a forecast N months ahead.
    """
    if monthly_df.empty:
        return None, None

    model = build_prophet_model()
    model.fit(monthly_df)

    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)

    return forecast, model


# ---------------------------------------------------------
# BUILD FORECAST + ACTUAL MERGED DF
# ---------------------------------------------------------

def merge_actual_and_forecast(monthly_df, forecast_df):
    """
    Merge actual usage with forecasted usage for charting.
    """
    actual = monthly_df.rename(columns={"y": "y"}).copy()
    actual["ds"] = pd.to_datetime(actual["ds"])

    forecast = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    forecast["ds"] = pd.to_datetime(forecast["ds"])

    return actual, forecast


# ---------------------------------------------------------
# BENCHMARK-AWARE FORECASTING
# ---------------------------------------------------------

def build_benchmark_for_forecast(df_filtered, forecast_df):
    """
    Build a benchmark line for forecast charts based on:
    - Utility type
    - Unit count
    """
    if df_filtered.empty:
        return None

    utility = df_filtered["utility"].iloc[0]
    units = df_filtered["units"].iloc[0]

    usage_bench, _ = get_utility_benchmark(utility, units)

    if usage_bench is None:
        return None

    return build_benchmark_df(forecast_df, usage_bench)


# ---------------------------------------------------------
# FORECAST SUMMARY (NARRATIVE)
# ---------------------------------------------------------

def forecast_summary(actual_df, forecast_df, benchmark_value=None):
    """
    Generate a narrative summary of the forecast:
    - Last actual usage
    - Next 3-month average forecast
    - Benchmark comparison
    """
    if actual_df.empty or forecast_df.empty:
        return "Not enough data to generate a forecast summary."

    last_actual = actual_df.dropna(subset=["y"]).tail(1)
    future_only = forecast_df[forecast_df["ds"] > actual_df["ds"].max()]

    if last_actual.empty or future_only.empty:
        return "Not enough data to generate a forecast summary."

    last_val = float(last_actual["y"].iloc[0])
    next_3 = future_only.head(3)
    avg_forecast = float(next_3["yhat"].mean())

    summary = (
        f"Last actual month usage: **{last_val:,.0f}**\n\n"
        f"Average forecasted usage (next 3 months): **{avg_forecast:,.0f}**\n\n"
    )

    if benchmark_value is not None:
        diff_pct = (avg_forecast - benchmark_value) / benchmark_value * 100
        direction = "above" if diff_pct > 0 else "below"
        summary += (
            f"Benchmark usage: **{benchmark_value:,.0f}**\n\n"
            f"Forecast is **{abs(diff_pct):.1f}% {direction}** the benchmark.\n"
        )

    return summary
