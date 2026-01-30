import streamlit as st
import pandas as pd

from utils.styles import section_divider, kpi_card
from utils.preprocess import (
    portfolio_summary,
    property_ranking,
    utility_group,
    provider_group,
)
from utils.charts import utility_mix


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Portfolio Overview")
st.write("Portfolio-wide insights across all properties, utilities, and providers.")


# ---------------------------------------------------------
# ACCESS FULL DATA (not just filtered)
# ---------------------------------------------------------

if "df" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df


# ---------------------------------------------------------
# PORTFOLIO SUMMARY
# ---------------------------------------------------------

st.subheader("Portfolio KPIs")

summary = portfolio_summary(df).iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("Total Usage", f"{summary['total_usage']:,.0f}")

with col2:
    kpi_card("Total Cost", f"${summary['total_cost']:,.0f}")

with col3:
    kpi_card("Total Properties", f"{summary['total_properties']}")

with col4:
    kpi_card("Total Meters", f"{summary['total_meters']}")


section_divider()


# ---------------------------------------------------------
# UTILITY MIX
# ---------------------------------------------------------

st.subheader("Utility Mix")

util_df = utility_group(df)

if util_df.empty:
    st.info("No utility data available.")
else:
    st.altair_chart(utility_mix(util_df), use_container_width=True)


section_divider()


# ---------------------------------------------------------
# PROVIDER MIX
# ---------------------------------------------------------

st.subheader("Provider Summary")

provider_df = provider_group(df)

if provider_df.empty:
    st.info("No provider data available.")
else:
    st.dataframe(provider_df, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# TOP & BOTTOM PROPERTIES
# ---------------------------------------------------------

st.subheader("Top & Bottom Properties")

colA, colB = st.columns(2)

with colA:
    st.markdown("### Top 5 by Usage")
    top5 = property_ranking(df, metric="usage", top_n=5)
    st.dataframe(top5, use_container_width=True)

with colB:
    st.markdown("### Bottom 5 by Usage")
    bottom5 = property_ranking(df, metric="usage", top_n=len(df["property"].unique()))
    bottom5 = bottom5.tail(5)
    st.dataframe(bottom5, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# RAW PORTFOLIO TABLE
# ---------------------------------------------------------

st.subheader("Portfolio Data Table")

st.dataframe(df, use_container_width=True)
