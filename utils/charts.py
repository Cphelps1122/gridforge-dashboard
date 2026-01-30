import altair as alt
import pandas as pd
from .styles import GRIDFORGE_COLORS


# ---------------------------------------------------------
# BASIC LINE CHART (Usage or Cost)
# ---------------------------------------------------------

def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color=None):
    """
    Generic line chart builder.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line()

    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x}:T", title=""),
            y=alt.Y(f"{y}:Q", title=""),
            color=alt.value(color or GRIDFORGE_COLORS["primary"]),
            tooltip=[f"{x}:T", f"{y}:Q"],
        )
        .properties(title=title)
    )


# ---------------------------------------------------------
# MONTHLY USAGE TREND
# ---------------------------------------------------------

def usage_trend(df_monthly: pd.DataFrame):
    return line_chart(
        df_monthly,
        x="month_start",
        y="usage",
        title="Monthly Usage Trend",
        color=GRIDFORGE_COLORS["primary"],
    )


# ---------------------------------------------------------
# MONTHLY COST TREND
# ---------------------------------------------------------

def cost_trend(df_monthly: pd.DataFrame):
    return line_chart(
        df_monthly,
        x="month_start",
        y="cost",
        title="Monthly Cost Trend",
        color=GRIDFORGE_COLORS["accent"],
    )


# ---------------------------------------------------------
# OCCUPANCY TREND
# ---------------------------------------------------------

def occupancy_trend(df_monthly: pd.DataFrame):
    return line_chart(
        df_monthly,
        x="month_start",
        y="occupancy",
        title="Occupancy Trend",
        color="#6A1B9A",
    )


# ---------------------------------------------------------
# USAGE PER OCCUPIED UNIT TREND
# ---------------------------------------------------------

def usage_per_occupied_unit_trend(df_monthly: pd.DataFrame):
    return line_chart(
        df_monthly,
        x="month_start",
        y="usage_per_occupied_unit",
        title="Usage per Occupied Unit",
        color="#00897B",
    )


# ---------------------------------------------------------
# COST PER OCCUPIED UNIT TREND
# ---------------------------------------------------------

def cost_per_occupied_unit_trend(df_monthly: pd.DataFrame):
    return line_chart(
        df_monthly,
        x="month_start",
        y="cost_per_occupied_unit",
        title="Cost per Occupied Unit",
        color="#C62828",
    )


# ---------------------------------------------------------
# METER-LEVEL USAGE BAR CHART
# ---------------------------------------------------------

def meter_usage_bar(df_meters: pd.DataFrame):
    """
    Bar chart showing total usage by meter.
    """
    if df_meters.empty:
        return alt.Chart(pd.DataFrame({"meter_number": [], "total_usage": []})).mark_bar()

    return (
        alt.Chart(df_meters)
        .mark_bar()
        .encode(
            x=alt.X("meter_number:N", title="Meter #"),
            y=alt.Y("total_usage:Q", title="Total Usage"),
            color=alt.value(GRIDFORGE_COLORS["primary"]),
            tooltip=["meter_number:N", "total_usage:Q"],
        )
        .properties(title="Usage by Meter")
    )


# ---------------------------------------------------------
# PROVIDER COMPARISON BAR CHART
# ---------------------------------------------------------

def provider_comparison(df_provider: pd.DataFrame):
    """
    Compare total usage by provider.
    """
    if df_provider.empty:
        return alt.Chart(pd.DataFrame({"provider_code": [], "total_usage": []})).mark_bar()

    return (
        alt.Chart(df_provider)
        .mark_bar()
        .encode(
            x=alt.X("provider_code:N", title="Provider"),
            y=alt.Y("total_usage:Q", title="Total Usage"),
            color=alt.value(GRIDFORGE_COLORS["accent"]),
            tooltip=["provider_code:N", "total_usage:Q", "total_cost:Q"],
        )
        .properties(title="Provider Usage Comparison")
    )


# ---------------------------------------------------------
# UTILITY MIX PIE CHART
# ---------------------------------------------------------

def utility_mix(df_util: pd.DataFrame):
    """
    Pie chart showing usage share by utility type.
    """
    if df_util.empty:
        return alt.Chart(pd.DataFrame({"utility": [], "total_usage": []})).mark_arc()

    return (
        alt.Chart(df_util)
        .mark_arc()
        .encode(
            theta="total_usage:Q",
            color="utility:N",
            tooltip=["utility:N", "total_usage:Q"],
        )
        .properties(title="Utility Mix")
    )


# ---------------------------------------------------------
# YOY USAGE TREND
# ---------------------------------------------------------

def yoy_usage_chart(df_yoy: pd.DataFrame):
    """
    Year-over-year usage trend.
    """
    if df_yoy.empty:
        return alt.Chart(pd.DataFrame({"year": [], "total_usage": []})).mark_line()

    return (
        alt.Chart(df_yoy)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("total_usage:Q", title="Total Usage"),
            color=alt.value(GRIDFORGE_COLORS["primary"]),
            tooltip=["year:O", "total_usage:Q", "usage_change:Q"],
        )
        .properties(title="Year-over-Year Usage")
    )


# ---------------------------------------------------------
# YOY COST TREND
# ---------------------------------------------------------

def yoy_cost_chart(df_yoy: pd.DataFrame):
    """
    Year-over-year cost trend.
    """
    if df_yoy.empty:
        return alt.Chart(pd.DataFrame({"year": [], "total_cost": []})).mark_line()

    return (
        alt.Chart(df_yoy)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("total_cost:Q", title="Total Cost"),
            color=alt.value(GRIDFORGE_COLORS["accent"]),
            tooltip=["year:O", "total_cost:Q", "cost_change:Q"],
        )
        .properties(title="Year-over-Year Cost")
    )


# ---------------------------------------------------------
# FORECAST CHART (Actual + Forecast + Confidence Band)
# ---------------------------------------------------------

def forecast_chart(actual_df, forecast_df, benchmark_df=None):
    """
    Build a combined forecast chart:
    - Actual usage
    - Forecasted usage
    - Confidence interval
    - Optional benchmark line
    """
    base = alt.Chart(forecast_df).encode(x="ds:T")

    # Confidence band
    band = base.mark_area(opacity=0.18, color=GRIDFORGE_COLORS["primary"]).encode(
        y="yhat_lower:Q",
        y2="yhat_upper:Q",
    )

    # Actual
    actual = (
        alt.Chart(actual_df)
        .mark_line(point=True, color=GRIDFORGE_COLORS["accent"])
        .encode(
            x="ds:T",
            y="y:Q",
            tooltip=["ds:T", "y:Q"],
        )
    )

    # Forecast line
    forecast_line = (
        base.mark_line(color=GRIDFORGE_COLORS["primary_dark"])
        .encode(
            y="yhat:Q",
            tooltip=["ds:T", "yhat:Q"],
        )
    )

    chart = band + actual + forecast_line

    # Optional benchmark
    if benchmark_df is not None:
        benchmark_line = (
            alt.Chart(benchmark_df)
            .mark_line(strokeDash=[4, 4], color="#666666")
            .encode(
                x="ds:T",
                y="benchmark:Q",
                tooltip=["ds:T", "benchmark:Q"],
            )
        )
        chart = chart + benchmark_line

    return chart.properties(title="Forecasted Usage")
