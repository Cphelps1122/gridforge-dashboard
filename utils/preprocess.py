import pandas as pd
import numpy as np


# ---------------------------------------------------------
# MONTHLY AGGREGATION
# ---------------------------------------------------------

def monthly_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate usage and cost by month for a given property + utility.
    Requires df to already be filtered by property and utility.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month_start")
        .agg(
            usage=("usage", "sum"),
            cost=("cost", "sum"),
            occupancy=("occupancy", "mean"),
            units=("units", "mean"),
            usage_per_day=("usage_per_day", "mean"),
            cost_per_day=("cost_per_day", "mean"),
        )
        .reset_index()
    )

    return monthly


# ---------------------------------------------------------
# OCCUPANCY NORMALIZATION
# ---------------------------------------------------------

def occupancy_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add occupancy-normalized usage and cost:
    - usage_per_occupied_unit
    - cost_per_occupied_unit
    """
    df = df.copy()

    if "occupancy" in df.columns and "usage" in df.columns:
        df["usage_per_occupied_unit"] = np.where(
            df["occupancy"] > 0,
            df["usage"] / df["occupancy"],
            np.nan,
        )
    else:
        df["usage_per_occupied_unit"] = np.nan

    if "occupancy" in df.columns and "cost" in df.columns:
        df["cost_per_occupied_unit"] = np.where(
            df["occupancy"] > 0,
            df["cost"] / df["occupancy"],
            np.nan,
        )
    else:
        df["cost_per_occupied_unit"] = np.nan

    return df


# ---------------------------------------------------------
# METER-LEVEL GROUPING
# ---------------------------------------------------------

def meter_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group usage and cost by meter number.
    """
    if "meter_number" not in df.columns:
        return pd.DataFrame()

    meter_df = (
        df.groupby("meter_number")
        .agg(
            total_usage=("usage", "sum"),
            total_cost=("cost", "sum"),
            avg_usage_per_day=("usage_per_day", "mean"),
            avg_cost_per_day=("cost_per_day", "mean"),
            reading_delta=("reading_delta", "mean"),
        )
        .reset_index()
    )

    return meter_df


# ---------------------------------------------------------
# PROVIDER-LEVEL GROUPING
# ---------------------------------------------------------

def provider_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group usage and cost by provider_code.
    """
    if "provider_code" not in df.columns:
        return pd.DataFrame()

    provider_df = (
        df.groupby("provider_code")
        .agg(
            total_usage=("usage", "sum"),
            total_cost=("cost", "sum"),
            avg_usage_per_day=("usage_per_day", "mean"),
            avg_cost_per_day=("cost_per_day", "mean"),
        )
        .reset_index()
    )

    return provider_df


# ---------------------------------------------------------
# UTILITY-LEVEL GROUPING
# ---------------------------------------------------------

def utility_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group usage and cost by utility type (Electricity, Gas, Water, etc.)
    """
    if "utility" not in df.columns:
        return pd.DataFrame()

    util_df = (
        df.groupby("utility")
        .agg(
            total_usage=("usage", "sum"),
            total_cost=("cost", "sum"),
            avg_usage_per_day=("usage_per_day", "mean"),
            avg_cost_per_day=("cost_per_day", "mean"),
        )
        .reset_index()
    )

    return util_df


# ---------------------------------------------------------
# YEAR-OVER-YEAR COMPARISON
# ---------------------------------------------------------

def yoy_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute YOY usage and cost for each property + utility.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["year"] = df["date"].dt.year

    yoy = (
        df.groupby("year")
        .agg(
            total_usage=("usage", "sum"),
            total_cost=("cost", "sum"),
            avg_usage_per_day=("usage_per_day", "mean"),
            avg_cost_per_day=("cost_per_day", "mean"),
        )
        .reset_index()
    )

    yoy["usage_change"] = yoy["total_usage"].diff()
    yoy["cost_change"] = yoy["total_cost"].diff()

    return yoy


# ---------------------------------------------------------
# PORTFOLIO ROLLUP
# ---------------------------------------------------------

def portfolio_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Portfolio-level KPIs across all properties.
    """
    if df.empty:
        return pd.DataFrame()

    summary = {
        "total_usage": df["usage"].sum(),
        "total_cost": df["cost"].sum(),
        "avg_usage_per_day": df["usage_per_day"].mean(),
        "avg_cost_per_day": df["cost_per_day"].mean(),
        "total_properties": df["property"].nunique(),
        "total_meters": df["meter_number"].nunique() if "meter_number" in df.columns else None,
    }

    return pd.DataFrame([summary])


# ---------------------------------------------------------
# TOP/BOTTOM PROPERTY RANKING
# ---------------------------------------------------------

def property_ranking(df: pd.DataFrame, metric="usage", top_n=5):
    """
    Rank properties by usage or cost.
    """
    if df.empty or metric not in df.columns:
        return pd.DataFrame()

    ranking = (
        df.groupby("property")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    return ranking
