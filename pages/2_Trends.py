import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    monthly_aggregate,
    yoy_comparison,
    occupancy_normalize,
)
from utils.charts import (
    usage_trend,
    cost_trend,
    occupancy_trend,
    yoy_usage_chart,
    yoy_cost_chart,
    usage_per_occupied_unit_trend,
    cost_per_occupied_unit_trend,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Trends")
st.write("Explore usage, cost, occupancy, and year-over-year performance.")


# ---------------------------------------------------------
# ACCESS FILTERED DATA FROM SESSION STATE
# ---------------------------------------------------------

if "df_filtered" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df_filtered
df_compare = st.session_state.df_comparison
normalize = st.session_state.normalize


# ---------------------------------------------------------
# NORMALIZATION (if enabled)
# ---------------------------------------------------------

if normalize:
    df = occupancy_normalize(df)
    if df_compare is not None:
        df_compare = occupancy_normalize(df_compare)


# ---------------------------------------------------------
# MONTHLY AGGREGATION
# ---------------------------------------------------------

df_monthly = monthly_aggregate(df)

if df_compare is not None:
    df_monthly_compare = monthly_aggregate(df_compare)
else:
    df_monthly_compare = None


# ---------------------------------------------------------
# KPI CARDS (Rolling Averages)
# ---------------------------------------------------------

st.subheader("Rolling Averages")

col1, col2, col3 = st.columns(3)

if len(df_monthly) >= 3:
    last_3_usage = df_monthly["usage"].tail(3).mean()
    last_3_cost = df_monthly["cost"].tail(3).mean()
    last_3_occ = df_monthly["occupancy"].tail(3).mean()
else:
    last_3_usage = last_3_cost = last_3_occ = 0

with col1:
    kpi_card("3-Month Avg Usage", f"{last_3_usage:,.0f}")

with col2:
    kpi_card("3-Month Avg Cost", f"${last_3_cost:,.0f}")

with col3:
    kpi_card("3-Month Avg Occupancy", f"{last_3_occ:,.1f}")


section_divider()


# ---------------------------------------------------------
# MONTHLY TRENDS
# ---------------------------------------------------------

st.subheader("Monthly Trends")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Usage",
    "Cost",
    "Occupancy",
    "Usage per Occupied Unit",
    "Cost per Occupied Unit",
])

with tab1:
    st.altair_chart(usage_trend(df_monthly), use_container_width=True)

with tab2:
    st.altair_chart(cost_trend(df_monthly), use_container_width=True)

with tab3:
    st.altair_chart(occupancy_trend(df_monthly), use_container_width=True)

with tab4:
    if normalize:
        st.altair_chart(usage_per_occupied_unit_trend(df_monthly), use_container_width=True)
    else:
        st.info("Enable normalization in the sidebar to view this chart.")

with tab5:
    if normalize:
        st.altair_chart(cost_per_occupied_unit_trend(df_monthly), use_container_width=True)
    else:
        st.info("Enable normalization in the sidebar to view this chart.")


section_divider()


# ---------------------------------------------------------
# YEAR-OVER-YEAR TRENDS
# ---------------------------------------------------------

st.subheader("Year-over-Year Trends")

df_yoy = yoy_comparison(df)

tabA, tabB = st.tabs(["YOY Usage", "YOY Cost"])

with tabA:
    st.altair_chart(yoy_usage_chart(df_yoy), use_container_width=True)

with tabB:
    st.altair_chart(yoy_cost_chart(df_yoy), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# COMPARISON PROPERTY OVERLAY
# ---------------------------------------------------------

if df_compare is not None:
    st.subheader("Comparison Property Overlay")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### Selected Property")
        st.altair_chart(usage_trend(df_monthly), use_container_width=True)

    with colB:
        st.markdown("### Comparison Property")
        st.altair_chart(usage_trend(df_monthly_compare), use_container_width=True)
