import streamlit as st
import pandas as pd

from utils.styles import section_divider
from utils.alerts import (
    detect_spikes,
    detect_missing_bills,
    detect_irregular_billing_periods,
    detect_bad_readings,
    detect_meter_anomalies,
    detect_occupancy_anomalies,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Alerts & Anomalies")
st.write("Automated detection of spikes, missing bills, anomalies, and irregular patterns.")


# ---------------------------------------------------------
# ACCESS FILTERED DATA FROM SESSION STATE
# ---------------------------------------------------------

if "df_filtered" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df_filtered


# ---------------------------------------------------------
# SPIKE DETECTION
# ---------------------------------------------------------

st.subheader("Usage Spikes")

usage_spikes = detect_spikes(df, metric="usage")

if usage_spikes.empty:
    st.success("No usage spikes detected.")
else:
    st.warning("Usage spikes detected:")
    st.dataframe(usage_spikes, use_container_width=True)


section_divider()


st.subheader("Cost Spikes")

cost_spikes = detect_spikes(df, metric="cost")

if cost_spikes.empty:
    st.success("No cost spikes detected.")
else:
    st.warning("Cost spikes detected:")
    st.dataframe(cost_spikes, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# MISSING BILLS
# ---------------------------------------------------------

st.subheader("Missing Bills")

missing = detect_missing_bills(df)

if missing.empty:
    st.success("No missing billing months detected.")
else:
    st.warning("Missing billing months detected:")
    st.dataframe(missing, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# IRREGULAR BILLING PERIODS
# ---------------------------------------------------------

st.subheader("Irregular Billing Periods")

irregular = detect_irregular_billing_periods(df)

if irregular.empty:
    st.success("No irregular billing periods detected.")
else:
    st.warning("Irregular billing periods detected:")
    st.dataframe(irregular, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# BAD READINGS
# ---------------------------------------------------------

st.subheader("Bad or Negative Readings")

bad_readings = detect_bad_readings(df)

if bad_readings.empty:
    st.success("No bad readings detected.")
else:
    st.warning("Bad readings detected:")
    st.dataframe(bad_readings, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# METER ANOMALIES
# ---------------------------------------------------------

st.subheader("Meter Anomalies")

meter_anoms = detect_meter_anomalies(df)

if meter_anoms.empty:
    st.success("No meter anomalies detected.")
else:
    st.warning("Meter anomalies detected (Z-score outliers):")
    st.dataframe(meter_anoms, use_container_width=True)


section_divider()


# ---------------------------------------------------------
# OCCUPANCY ANOMALIES
# ---------------------------------------------------------

st.subheader("Occupancy Anomalies")

occ_anoms = detect_occupancy_anomalies(df)

if occ_anoms.empty:
    st.success("No occupancy anomalies detected.")
else:
    st.warning("Significant occupancy anomalies detected:")
    st.dataframe(occ_anoms, use_container_width=True)
