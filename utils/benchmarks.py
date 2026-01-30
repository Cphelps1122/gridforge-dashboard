import pandas as pd
import numpy as np


# ---------------------------------------------------------
# UTILITY BENCHMARKS (industry-style assumptions)
# ---------------------------------------------------------

UTILITY_BENCHMARKS = {
    "Electricity": {
        "usage_per_unit": 1200,     # kWh per unit per month
        "cost_per_unit": 150,       # dollars per unit per month
    },
    "Gas": {
        "usage_per_unit": 300,      # therms per unit per month
        "cost_per_unit": 40,
    },
    "Water": {
        "usage_per_unit": 25000,    # gallons per unit per month
        "cost_per_unit": 60,
    },
}


# ---------------------------------------------------------
# PROVIDER BENCHMARKS (example defaults)
# ---------------------------------------------------------

PROVIDER_BENCHMARKS = {
    # provider_code: cost_per_kwh or equivalent
    "TXU": 0.14,
    "ONCOR": 0.12,
    "RELIANT": 0.13,
    "CONSTELLATION": 0.15,
}


# ---------------------------------------------------------
# UTILITY BENCHMARK LOOKUP
# ---------------------------------------------------------

def get_utility_benchmark(utility: str, units: float):
    """
    Returns benchmark usage and cost for a given utility and unit count.
    """
    if utility not in UTILITY_BENCHMARKS or units is None or units <= 0:
        return None, None

    usage_bench = units * UTILITY_BENCHMARKS[utility]["usage_per_unit"]
    cost_bench = units * UTILITY_BENCHMARKS[utility]["cost_per_unit"]

    return usage_bench, cost_bench


# ---------------------------------------------------------
# PROVIDER BENCHMARK LOOKUP
# ---------------------------------------------------------

def get_provider_benchmark(provider_code: str, usage: float):
    """
    Returns benchmark cost based on provider rate * usage.
    """
    if provider_code not in PROVIDER_BENCHMARKS or usage is None:
        return None

    rate = PROVIDER_BENCHMARKS[provider_code]
    return usage * rate


# ---------------------------------------------------------
# EFFICIENCY SCORING
# ---------------------------------------------------------

def efficiency_score(actual_usage: float, benchmark_usage: float):
    """
    Score from 0–100 based on how close actual usage is to benchmark.
    Lower usage = better score.
    """
    if actual_usage is None or benchmark_usage is None or benchmark_usage <= 0:
        return None

    ratio = actual_usage / benchmark_usage

    # Perfect efficiency = 100
    # 20% above benchmark = 80
    # 50% above benchmark = 50
    # 100% above benchmark = 0
    score = max(0, min(100, 100 - (ratio - 1) * 100))

    return round(score, 1)


# ---------------------------------------------------------
# BENCHMARK DEVIATION (% above/below)
# ---------------------------------------------------------

def benchmark_deviation(actual: float, benchmark: float):
    """
    Returns % difference between actual and benchmark.
    Positive = above benchmark (worse)
    Negative = below benchmark (better)
    """
    if actual is None or benchmark is None or benchmark <= 0:
        return None

    return round((actual - benchmark) / benchmark * 100, 1)


# ---------------------------------------------------------
# BENCHMARK DATAFRAME FOR FORECAST OVERLAY
# ---------------------------------------------------------

def build_benchmark_df(forecast_df: pd.DataFrame, benchmark_value: float):
    """
    Build a dataframe with a constant benchmark line for forecast charts.
    """
    if forecast_df.empty or benchmark_value is None:
        return None

    bench_df = forecast_df[["ds"]].copy()
    bench_df["benchmark"] = benchmark_value
    return bench_df


# ---------------------------------------------------------
# PROPERTY-LEVEL BENCHMARK SUMMARY
# ---------------------------------------------------------

def property_benchmark_summary(df: pd.DataFrame):
    """
    Returns a summary table comparing actual vs benchmark usage and cost.
    """
    if df.empty:
        return pd.DataFrame()

    utility = df["utility"].iloc[0]
    units = df["units"].iloc[0]

    usage_bench, cost_bench = get_utility_benchmark(utility, units)

    actual_usage = df["usage"].sum()
    actual_cost = df["cost"].sum()

    return pd.DataFrame([{
        "utility": utility,
        "units": units,
        "actual_usage": actual_usage,
        "benchmark_usage": usage_bench,
        "usage_deviation_pct": benchmark_deviation(actual_usage, usage_bench),
        "actual_cost": actual_cost,
        "benchmark_cost": cost_bench,
        "cost_deviation_pct": benchmark_deviation(actual_cost, cost_bench),
        "efficiency_score": efficiency_score(actual_usage, usage_bench),
    }])
