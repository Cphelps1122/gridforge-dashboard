import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    monthly_aggregate,
    occupancy_normalize,
)
from utils.forecasting import (
    prepare_monthly_forecast_df,
    run_forecast,
    merge_actual_and_forecast,
    build_benchmark_for_forecast,
    forecast_summary,
)
from utils.charts import forecast_chart


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Forecasting")
st.write("AI-powered usage forecasting with benchmark overlays and narrative insights.")


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
# MONTHLY AGGREGATION FOR FORECASTING
# ---------------------------------------------------------

monthly_df, df_full = prepare_monthly_forecast_df(df)

if monthly_df.empty:
    st.warning("Not enough data to generate a forecast.")
    st.stop()


# ---------------------------------------------------------
# RUN FORECAST
# ---------------------------------------------------------

forecast_df, model = run_forecast(monthly_df, periods=12)

if forecast_df is None:
    st.warning("Forecast model could not be generated.")
    st.stop()


# ---------------------------------------------------------
# MERGE ACTUAL + FORECAST
# ---------------------------------------------------------

actual_df, forecast_df_clean = merge_actual_and_forecast(monthly_df, forecast_df)


# ---------------------------------------------------------
# BENCHMARK LINE (optional)
# ---------------------------------------------------------

benchmark_df = build_benchmark_for_forecast(df, forecast_df_clean)


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Forecast KPIs")

col1, col2, col3 = st.columns(3)

last_actual = actual_df["y"].iloc[-1]
next_month_forecast = forecast_df_clean["yhat"].iloc[len(actual_df)]

with col1:
    kpi_card("Last Actual Usage", f"{last_actual:,.0f}")

with col2:
    kpi_card("Next Month Forecast", f"{next_month_forecast:,.0f}")

with col3:
    if benchmark_df is not None:
        kpi_card("Benchmark Usage", f"{benchmark_df['benchmark'].iloc[0]:,.0f}")
    else:
        kpi_card("Benchmark Usage", "N/A")


section_divider()


# ---------------------------------------------------------
# FORECAST CHART
# ---------------------------------------------------------

st.subheader("Forecast Chart")

chart = forecast_chart(
    actual_df,
    forecast_df_clean,
    benchmark_df=benchmark_df
)

st.altair_chart(chart, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# FORECAST SUMMARY (Narrative)
# ---------------------------------------------------------

st.subheader("Forecast Summary")

benchmark_value = None
if benchmark_df is not None:
    benchmark_value = benchmark_df["benchmark"].iloc[0]

summary_text = forecast_summary(actual_df, forecast_df_clean, benchmark_value)

st.markdown(
    f"""
    <div class="gridforge-card" style="font-size:16px; line-height:1.5;">
        {summary_text}
    </div>
    """,
    unsafe_allow_html=True
)
