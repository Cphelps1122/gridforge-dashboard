import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    provider_group,
    occupancy_normalize,
)
from utils.benchmarks import (
    get_provider_benchmark,
    efficiency_score,
    benchmark_deviation,
)
from utils.charts import provider_comparison


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Provider Analysis")
st.write("Compare provider performance, benchmark costs, and efficiency scores.")


# ---------------------------------------------------------
# ACCESS FILTERED DATA FROM SESSION STATE
# ---------------------------------------------------------

if "df_filtered" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df_filtered
normalize = st.session_state.normalize


# ---------------------------------------------------------
# NORMALIZATION (if enabled)
# ---------------------------------------------------------

if normalize:
    df = occupancy_normalize(df)


# ---------------------------------------------------------
# PROVIDER GROUPING
# ---------------------------------------------------------

provider_df = provider_group(df)

if provider_df.empty:
    st.warning("No provider data available for this property/utility.")
    st.stop()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Provider KPIs")

col1, col2, col3 = st.columns(3)

total_providers = provider_df["provider_code"].nunique()
top_usage_provider = provider_df.sort_values("total_usage", ascending=False).iloc[0]
top_cost_provider = provider_df.sort_values("total_cost", ascending=False).iloc[0]

with col1:
    kpi_card("Total Providers", f"{total_providers}")

with col2:
    kpi_card(
        "Highest Usage Provider",
        f"{top_usage_provider['provider_code']} ({top_usage_provider['total_usage']:,.0f})"
    )

with col3:
    kpi_card(
        "Highest Cost Provider",
        f"{top_cost_provider['provider_code']} (${top_cost_provider['total_cost']:,.0f})"
    )


section_divider()


# ---------------------------------------------------------
# PROVIDER COMPARISON CHART
# ---------------------------------------------------------

st.subheader("Provider Usage Comparison")

st.altair_chart(provider_comparison(provider_df), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# PROVIDER BENCHMARK COSTS
# ---------------------------------------------------------

st.subheader("Provider Benchmark Costs")

bench_rows = []

for _, row in provider_df.iterrows():
    provider = row["provider_code"]
    usage = row["total_usage"]
    actual_cost = row["total_cost"]

    bench_cost = get_provider_benchmark(provider, usage)
    deviation = benchmark_deviation(actual_cost, bench_cost)
    score = efficiency_score(actual_cost, bench_cost)

    bench_rows.append({
        "provider_code": provider,
        "actual_usage": usage,
        "actual_cost": actual_cost,
        "benchmark_cost": bench_cost,
        "cost_deviation_pct": deviation,
        "efficiency_score": score,
    })

bench_df = pd.DataFrame(bench_rows)

st.dataframe(bench_df, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# RAW PROVIDER TABLE
# ---------------------------------------------------------

st.subheader("Provider Details")

st.dataframe(provider_df, use_container_width=True)
