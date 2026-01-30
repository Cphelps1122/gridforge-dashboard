import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    meter_group,
    occupancy_normalize,
)
from utils.alerts import detect_meter_anomalies
from utils.charts import meter_usage_bar


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Meter Analytics")
st.write("Analyze meter-level performance, usage patterns, and anomalies.")


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
# METER GROUPING
# ---------------------------------------------------------

meter_df = meter_group(df)

if meter_df.empty:
    st.warning("No meter data available for this property/utility.")
    st.stop()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Meter Summary")

col1, col2, col3 = st.columns(3)

total_meters = meter_df["meter_number"].nunique()
highest_usage_meter = meter_df.sort_values("total_usage", ascending=False).iloc[0]
highest_cost_meter = meter_df.sort_values("total_cost", ascending=False).iloc[0]

with col1:
    kpi_card("Total Meters", f"{total_meters}")

with col2:
    kpi_card(
        "Highest Usage Meter",
        f"#{highest_usage_meter['meter_number']} ({highest_usage_meter['total_usage']:,.0f})"
    )

with col3:
    kpi_card(
        "Highest Cost Meter",
        f"#{highest_cost_meter['meter_number']} (${highest_cost_meter['total_cost']:,.0f})"
    )


section_divider()


# ---------------------------------------------------------
# METER USAGE BAR CHART
# ---------------------------------------------------------

st.subheader("Usage by Meter")

st.altair_chart(meter_usage_bar(meter_df), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# METER ANOMALIES
# ---------------------------------------------------------

st.subheader("Meter Anomalies")

anomalies = detect_meter_anomalies(df)

if anomalies.empty:
    st.success("No meter anomalies detected.")
else:
    st.warning("Anomalous meters detected (Z-score outliers):")
    st.dataframe(anomalies, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# RAW METER TABLE
# ---------------------------------------------------------

st.subheader("Meter Details")

st.dataframe(meter_df, use_container_width=True)
