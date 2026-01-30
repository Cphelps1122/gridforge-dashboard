import streamlit as st
import pandas as pd

from utils.styles import kpi_card, section_divider
from utils.preprocess import (
    monthly_aggregate,
    occupancy_normalize,
    provider_group,
    utility_group,
)
from utils.charts import (
    usage_trend,
    cost_trend,
    occupancy_trend,
    usage_per_occupied_unit_trend,
    cost_per_occupied_unit_trend,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Overview")
st.write("A high-level summary of usage, cost, occupancy, and provider performance.")


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
# KPI CARDS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

total_usage = df["usage"].sum()
total_cost = df["cost"].sum()
avg_occ = df["occupancy"].mean()
num_meters = df["meter_number"].nunique()

with col1:
    kpi_card("Total Usage", f"{total_usage:,.0f}")

with col2:
    kpi_card("Total Cost", f"${total_cost:,.0f}")

with col3:
    kpi_card("Avg Occupancy", f"{avg_occ:,.1f}")

with col4:
    kpi_card("Meters", f"{num_meters}")


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
# PROVIDER SUMMARY
# ---------------------------------------------------------

st.subheader("Provider Summary")

provider_df = provider_group(df)
st.dataframe(provider_df, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# UTILITY SUMMARY
# ---------------------------------------------------------

st.subheader("Utility Summary")

utility_df = utility_group(df)
st.dataframe(utility_df, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# COMPARISON PROPERTY (if selected)
# ---------------------------------------------------------

if df_compare is not None:
    st.subheader("Comparison Property")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### Selected Property")
        st.altair_chart(usage_trend(df_monthly), use_container_width=True)

    with colB:
        st.markdown("### Comparison Property")
        st.altair_chart(usage_trend(df_monthly_compare), use_container_width=True)
