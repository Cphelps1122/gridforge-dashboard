import streamlit as st
import pandas as pd
import io

from utils.preprocess import (
    monthly_aggregate,
    provider_group,
    utility_group,
)
from utils.alerts import (
    detect_spikes,
    detect_missing_bills,
    detect_irregular_billing_periods,
    detect_bad_readings,
    detect_meter_anomalies,
    detect_occupancy_anomalies,
)
from utils.forecasting import (
    prepare_monthly_forecast_df,
    run_forecast,
    merge_actual_and_forecast,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.title("Exports")
st.write("Download filtered data, summaries, alerts, and forecast results.")


# ---------------------------------------------------------
# ACCESS FILTERED DATA FROM SESSION STATE
# ---------------------------------------------------------

if "df_filtered" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

df = st.session_state.df_filtered


# ---------------------------------------------------------
# EXPORT HELPER
# ---------------------------------------------------------

def export_csv(df, filename):
    """
    Convert a dataframe to a downloadable CSV.
    """
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"Download {filename}",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )


# ---------------------------------------------------------
# RAW FILTERED DATA
# ---------------------------------------------------------

st.subheader("Filtered Raw Data")

export_csv(df, "filtered_data.csv")

st.dataframe(df, use_container_width=True)

st.markdown("---")


# ---------------------------------------------------------
# MONTHLY AGGREGATE EXPORT
# ---------------------------------------------------------

st.subheader("Monthly Aggregates")

df_monthly = monthly_aggregate(df)

export_csv(df_monthly, "monthly_aggregate.csv")

st.dataframe(df_monthly, use_container_width=True)

st.markdown("---")


# ---------------------------------------------------------
# PROVIDER SUMMARY EXPORT
# ---------------------------------------------------------

st.subheader("Provider Summary")

provider_df = provider_group(df)

export_csv(provider_df, "provider_summary.csv")

st.dataframe(provider_df, use_container_width=True)

st.markdown("---")


# ---------------------------------------------------------
# UTILITY SUMMARY EXPORT
# ---------------------------------------------------------

st.subheader("Utility Summary")

utility_df = utility_group(df)

export_csv(utility_df, "utility_summary.csv")

st.dataframe(utility_df, use_container_width=True)

st.markdown("---")


# ---------------------------------------------------------
# ALERT EXPORTS
# ---------------------------------------------------------

st.subheader("Alerts & Anomalies")

alerts = {
    "usage_spikes": detect_spikes(df, metric="usage"),
    "cost_spikes": detect_spikes(df, metric="cost"),
    "missing_bills": detect_missing_bills(df),
    "irregular_billing": detect_irregular_billing_periods(df),
    "bad_readings": detect_bad_readings(df),
    "meter_anomalies": detect_meter_anomalies(df),
    "occupancy_anomalies": detect_occupancy_anomalies(df),
}

for name, alert_df in alerts.items():
    st.markdown(f"### {name.replace('_', ' ').title()}")
    export_csv(alert_df, f"{name}.csv")
    st.dataframe(alert_df, use_container_width=True)
    st.markdown("---")


# ---------------------------------------------------------
# FORECAST EXPORT
# ---------------------------------------------------------

st.subheader("Forecast Results")

monthly_df, _ = prepare_monthly_forecast_df(df)

if monthly_df.empty:
    st.info("Not enough data to generate a forecast.")
else:
    forecast_df, model = run_forecast(monthly_df, periods=12)
    actual_df, forecast_clean = merge_actual_and_forecast(monthly_df, forecast_df)

    export_csv(forecast_clean, "forecast_results.csv")

    st.dataframe(forecast_clean, use_container_width=True)
