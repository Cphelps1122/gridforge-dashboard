import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    monthly_aggregate,
    occupancy_normalize,
)
from utils.alerts import detect_occupancy_anomalies
from utils.charts import (
    occupancy_trend,
    usage_per_occupied_unit_trend,
    cost_per_occupied_unit_trend,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Occupancy Insights")
st.write("Understand how occupancy impacts usage, cost, and efficiency.")


# ---------------------------------------------------------
# ACCESS FILTERED DATA FROM SESSION STATE
# ---------------------------------------------------------

if "df_filtered" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df_filtered
normalize = st.session_state.normalize


# ---------------------------------------------------------
# NORMALIZATION (always applied for this page)
# ---------------------------------------------------------

df_norm = occupancy_normalize(df)

# Monthly aggregation
df_monthly = monthly_aggregate(df_norm)

if df_monthly.empty:
    st.warning("Not enough data to display occupancy insights.")
    st.stop()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Occupancy KPIs")

col1, col2, col3 = st.columns(3)

avg_occ = df_monthly["occupancy"].mean()
avg_usage_per_occ = df_monthly["usage_per_occupied_unit"].mean()
avg_cost_per_occ = df_monthly["cost_per_occupied_unit"].mean()

with col1:
    kpi_card("Avg Occupancy", f"{avg_occ:,.1f}")

with col2:
    kpi_card("Usage per Occupied Unit", f"{avg_usage_per_occ:,.1f}")

with col3:
    kpi_card("Cost per Occupied Unit", f"${avg_cost_per_occ:,.2f}")


section_divider()


# ---------------------------------------------------------
# OCCUPANCY TREND
# ---------------------------------------------------------

st.subheader("Occupancy Trend")

st.altair_chart(occupancy_trend(df_monthly), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# NORMALIZED USAGE & COST TRENDS
# ---------------------------------------------------------

st.subheader("Normalized Usage & Cost Trends")

tab1, tab2 = st.tabs(["Usage per Occupied Unit", "Cost per Occupied Unit"])

with tab1:
    st.altair_chart(usage_per_occupied_unit_trend(df_monthly), use_container_width=True)

with tab2:
    st.altair_chart(cost_per_occupied_unit_trend(df_monthly), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# OCCUPANCY ANOMALIES
# ---------------------------------------------------------

st.subheader("Occupancy Anomalies")

anomalies = detect_occupancy_anomalies(df)

if anomalies.empty:
    st.success("No significant occupancy anomalies detected.")
else:
    st.warning("Significant occupancy changes detected:")
    st.dataframe(anomalies, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# RAW NORMALIZED TABLE
# ---------------------------------------------------------

st.subheader("Normalized Occupancy Table")

st.dataframe(df_monthly, use_container_width=True)
