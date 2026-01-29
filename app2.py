# ---------------------------------------------------------
# GRIDFORGE — FULLY BRANDED APP (app2.py)
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt
from prophet import Prophet
from io import BytesIO
import numpy as np

# ---------------------------------------------------------
# GLOBAL THEME — COLORS & TYPOGRAPHY
# ---------------------------------------------------------

GRIDFORGE_COLORS = {
    "primary": "#1A73E8",      # GridForge Blue
    "primary_dark": "#1558A6",
    "accent": "#FF7A00",       # Power Orange
    "text_main": "#222222",
    "text_subtle": "#555555",
    "border": "#E0E0E0",
    "background": "#FAFAFA"
}

GRIDFORGE_FONTS = {
    "header": "font-family: 'Segoe UI', sans-serif; font-weight: 700;",
    "subheader": "font-family: 'Segoe UI', sans-serif; font-weight: 600;",
    "body": "font-family: 'Segoe UI', sans-serif; font-weight: 400;",
}

# ---------------------------------------------------------
# GLOBAL STYLING — BUTTONS & ALTAIR THEME
# ---------------------------------------------------------

st.set_page_config(page_title="GridForge — Where Data Becomes Power", layout="wide")

st.markdown(
    f"""
    <style>
        div.stButton > button:first-child {{
            background-color: {GRIDFORGE_COLORS['primary']};
            color: white;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            border: none;
            font-size: 15px;
            {GRIDFORGE_FONTS['subheader']}
        }}
        div.stButton > button:first-child:hover {{
            background-color: {GRIDFORGE_COLORS['primary_dark']};
            color: white;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

def gridforge_chart_theme():
    return {
        "config": {
            "title": {
                "fontSize": 18,
                "font": "Segoe UI",
                "color": GRIDFORGE_COLORS["text_main"]
            },
            "axis": {
                "labelFont": "Segoe UI",
                "titleFont": "Segoe UI",
                "labelColor": GRIDFORGE_COLORS["text_subtle"],
                "titleColor": GRIDFORGE_COLORS["text_main"]
            },
            "legend": {
                "labelFont": "Segoe UI",
                "titleFont": "Segoe UI"
            }
        }
    }

alt.themes.register("gridforge", gridforge_chart_theme)
alt.themes.enable("gridforge")

# ---------------------------------------------------------
# SECTION 1 — GRIDFORGE HEADER WITH LOGO
# ---------------------------------------------------------

header_cols = st.columns([1, 4])

with header_cols[0]:
    # Assumes gridforge_logo.png is in the same directory as app2.py
    try:
        st.image("gridforge_logo.png", use_column_width=True)
    except Exception:
        st.markdown(
            f"<div style='{GRIDFORGE_FONTS['header']} font-size:26px; color:{GRIDFORGE_COLORS['primary']};'>GridForge</div>",
            unsafe_allow_html=True
        )

with header_cols[1]:
    st.markdown(
        f"""
        <div style="
            padding: 10px 0 0 0;
            border-bottom: 1px solid {GRIDFORGE_COLORS['border']};
            margin-bottom: 15px;
        ">
            <h1 style="
                font-size: 32px;
                margin-bottom: 0;
                color: {GRIDFORGE_COLORS['text_main']};
                {GRIDFORGE_FONTS['header']}
                letter-spacing: -0.5px;
            ">
                GridForge
            </h1>
            <p style="
                font-size: 16px;
                margin-top: 4px;
                color: {GRIDFORGE_COLORS['text_subtle']};
                {GRIDFORGE_FONTS['body']}
            ">
                Where Data Becomes Power
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# SECTION 2 — LOAD DATA (Sheet1)
# ---------------------------------------------------------

@st.cache_data
def load_data():
    # Adjust filename if needed
    df_raw = pd.read_excel("Database with pivot tables.xlsx", sheet_name="Sheet1")

    # Rename columns to cleaner internal names
    df = df_raw.rename(
        columns={
            "Prop Name": "property",
            "State": "state",
            "City": "city",
            "# units": "units",
            "Date": "date",
            "Utility": "utility",
            "Usage": "usage",
            "$ Amt": "cost",
        }
    )

    df["date"] = pd.to_datetime(df["date"])
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Error loading data. Please ensure 'Database with pivot tables.xlsx' is in the app directory.")
    st.stop()

# ---------------------------------------------------------
# SECTION 8 — SIDEBAR NAVIGATION + BRANDING
# ---------------------------------------------------------

st.sidebar.markdown(
    f"""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <h2 style="
            margin-bottom:0;
            color:{GRIDFORGE_COLORS['text_main']};
            {GRIDFORGE_FONTS['subheader']}
        ">
            GridForge
        </h2>
        <p style="
            margin-top:5px;
            font-size:13px;
            color:{GRIDFORGE_COLORS['text_subtle']};
            {GRIDFORGE_FONTS['body']}
        ">
            Where Data Becomes Power
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Overview", "Trends", "Forecasting", "Exports"]
)

# ---------------------------------------------------------
# GLOBAL FILTERS (USED BY ALL DATA PAGES)
# ---------------------------------------------------------

st.markdown(
    f"""
    <div style="
        background-color: white;
        border: 1px solid {GRIDFORGE_COLORS['border']};
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    ">
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<h3 style='{GRIDFORGE_FONTS['subheader']} color:{GRIDFORGE_COLORS['text_main']};'>Filters</h3>",
    unsafe_allow_html=True
)

filter_cols = st.columns([1.4, 1.2, 1.2, 1.2])

with filter_cols[0]:
    properties = sorted(df["property"].dropna().unique())
    selected_property = st.selectbox("Primary Property", options=properties)

with filter_cols[1]:
    utilities = sorted(df[df["property"] == selected_property]["utility"].dropna().unique())
    selected_utility = st.selectbox("Utility", options=utilities)

with filter_cols[2]:
    df_prop_util = df[(df["property"] == selected_property) & (df["utility"] == selected_utility)]
    years = sorted(df_prop_util["date"].dt.year.unique())
    selected_years = st.multiselect("Years", options=years, default=years[-1:] if years else [])

with filter_cols[3]:
    compare_property = st.selectbox("Compare To (Optional)", options=["None"] + properties)

normalize = st.checkbox("Normalize by Units (usage & cost per unit)")

if st.button("Reset Filters"):
    st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Apply filters
if selected_years:
    df_filtered = df_prop_util[df_prop_util["date"].dt.year.isin(selected_years)].copy()
else:
    df_filtered = df_prop_util.copy()

df_compare = None
if compare_property != "None":
    df_compare = df[
        (df["property"] == compare_property) &
        (df["utility"] == selected_utility)
    ]
    if selected_years:
        df_compare = df_compare[df_compare["date"].dt.year.isin(selected_years)]

# Normalization by units
if normalize:
    if "units" in df_filtered.columns:
        df_filtered["usage"] = df_filtered["usage"] / df_filtered["units"]
        df_filtered["cost"] = df_filtered["cost"] / df_filtered["units"]
    if df_compare is not None and "units" in df_compare.columns:
        df_compare["usage"] = df_compare["usage"] / df_compare["units"]
        df_compare["cost"] = df_compare["cost"] / df_compare["units"]

# ---------------------------------------------------------
# PAGE: HOME (HERO + BRAND STORY)
# ---------------------------------------------------------

if page == "Home":
    st.markdown(
        f"""
        <div style="
            background-color:{GRIDFORGE_COLORS['background']};
            border: 1px solid {GRIDFORGE_COLORS['border']};
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        ">
            <h1 style="{GRIDFORGE_FONTS['header']} font-size:32px; color:{GRIDFORGE_COLORS['text_main']}; margin-bottom:5px;">
                Where Data Becomes Power
            </h1>
            <p style="{GRIDFORGE_FONTS['body']} font-size:16px; color:{GRIDFORGE_COLORS['text_subtle']}; max-width:800px;">
                GridForge transforms raw utility data into clarity, foresight, and action — empowering you to understand
                consumption, uncover hidden patterns, and shape a smarter, more efficient portfolio.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_hero_1, col_hero_2 = st.columns(2)

    with col_hero_1:
        st.markdown(
            """
            ### Why GridForge

            - **See the whole picture**  
              Unified visibility across usage, cost, and performance.

            - **Forecast with confidence**  
              Benchmark-aware modeling that reveals what’s coming next.

            - **Turn complexity into clarity**  
              Clean, intuitive insights that drive real operational decisions.

            - **Built for modern teams**  
              Fast, flexible, and designed for real-world utility challenges.
            """
        )

    with col_hero_2:
        st.markdown(
            """
            ### How to Use This Dashboard

            - Select a **property** and **utility** above  
            - Choose one or more **years**  
            - View **KPIs**, **trends**, and **forecasts**  
            - Export filtered data for reporting and analysis
            """
        )

    st.markdown("---")
    st.markdown("Use the navigation in the sidebar to explore **Overview**, **Trends**, **Forecasting**, and **Exports**.")

# ---------------------------------------------------------
# PAGE: OVERVIEW (KPIs)
# ---------------------------------------------------------

elif page == "Overview":
    st.markdown(
        f"<h3 style='{GRIDFORGE_FONTS['subheader']} color:{GRIDFORGE_COLORS['text_main']};'>Overview</h3>",
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        total_usage = df_filtered["usage"].sum()
        total_cost = df_filtered["cost"].sum()
        avg_usage = df_filtered["usage"].mean()
        avg_cost = df_filtered["cost"].mean()

        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total Usage", f"{total_usage:,.0f}")
        kpi_cols[1].metric("Total Cost", f"${total_cost:,.0f}")
        kpi_cols[2].metric("Avg Usage", f"{avg_usage:,.0f}")
        kpi_cols[3].metric("Avg Cost", f"${avg_cost:,.0f}")

        if df_compare is not None and not df_compare.empty:
            st.markdown("#### Comparison Property KPIs")
            comp_usage = df_compare["usage"].sum()
            comp_cost = df_compare["cost"].sum()
            comp_cols = st.columns(2)
            comp_cols[0].metric(f"{compare_property} Total Usage", f"{comp_usage:,.0f}")
            comp_cols[1].metric(f"{compare_property} Total Cost", f"${comp_cost:,.0f}")

# ---------------------------------------------------------
# PAGE: TRENDS
# ---------------------------------------------------------

elif page == "Trends":
    st.markdown(
        f"<h3 style='{GRIDFORGE_FONTS['subheader']} color:{GRIDFORGE_COLORS['text_main']};'>Trends</h3>",
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        df_trend = df_filtered.copy()
        df_trend["month"] = df_trend["date"].dt.to_period("M").dt.to_timestamp()
        df_trend_grouped = df_trend.groupby("month")[["usage", "cost"]].sum().reset_index()

        usage_chart = (
            alt.Chart(df_trend_grouped)
            .mark_line(point=True)
            .encode(
                x=alt.X("month:T", title="Month"),
                y=alt.Y("usage:Q", title="Usage"),
                color=alt.value(GRIDFORGE_COLORS["primary"])
            )
            .properties(title="Monthly Usage Trend")
        )

        cost_chart = (
            alt.Chart(df_trend_grouped)
            .mark_line(point=True)
            .encode(
                x=alt.X("month:T", title="Month"),
                y=alt.Y("cost:Q", title="Cost"),
                color=alt.value(GRIDFORGE_COLORS["accent"])
            )
            .properties(title="Monthly Cost Trend")
        )

        st.altair_chart(usage_chart, use_container_width=True)
        st.altair_chart(cost_chart, use_container_width=True)

        if df_compare is not None and not df_compare.empty:
            st.markdown("#### Comparison Usage Trend")
            df_comp = df_compare.copy()
            df_comp["month"] = df_comp["date"].dt.to_period("M").dt.to_timestamp()
            df_comp_grouped = df_comp.groupby("month")[["usage"]].sum().reset_index()
            df_comp_grouped["series"] = compare_property

            df_trend_grouped["series"] = selected_property

            df_both = pd.concat(
                [
                    df_trend_grouped[["month", "usage", "series"]],
                    df_comp_grouped[["month", "usage", "series"]],
                ],
                ignore_index=True,
            )

            comp_chart = (
                alt.Chart(df_both)
                .mark_line(point=True)
                .encode(
                    x="month:T",
                    y=alt.Y("usage:Q", title="Usage"),
                    color="series:N"
                )
                .properties(title="Usage Comparison")
            )

            st.altair_chart(comp_chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: FORECASTING
# ---------------------------------------------------------

elif page == "Forecasting":
    st.markdown(
        f"<h3 style='{GRIDFORGE_FONTS['subheader']} color:{GRIDFORGE_COLORS['text_main']};'>Forecasting</h3>",
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        df_forecast = df_filtered[["date", "usage"]].rename(columns={"date": "ds", "usage": "y"}).copy()
        df_forecast = df_forecast.sort_values("ds")

        if len(df_forecast) < 10:
            st.warning("Not enough data points to generate a reliable forecast.")
        else:
            periods = st.slider("Forecast Horizon (Days)", min_value=30, max_value=365, value=90, step=30)

            model = Prophet()
            model.fit(df_forecast)
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)

            base_chart = alt.Chart(forecast).mark_line().encode(
                x="ds:T",
                y=alt.Y("yhat:Q", title="Forecasted Usage"),
                color=alt.value(GRIDFORGE_COLORS["primary"])
            )

            ci_band = (
                alt.Chart(forecast)
                .mark_area(opacity=0.2)
                .encode(
                    x="ds:T",
                    y="yhat_lower:Q",
                    y2="yhat_upper:Q"
                )
            )

            st.altair_chart(ci_band + base_chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: EXPORTS
# ---------------------------------------------------------

elif page == "Exports":
    st.markdown(
        f"<h3 style='{GRIDFORGE_FONTS['subheader']} color:{GRIDFORGE_COLORS['text_main']};'>Exports</h3>",
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        st.markdown("Download the currently filtered dataset for offline analysis or reporting.")

        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Filtered Data (CSV)",
            data=csv_data,
            file_name="gridforge_filtered_data.csv",
            mime="text/csv"
        )

        # Simple Excel export
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_filtered.to_excel(writer, index=False, sheet_name="Filtered Data")
        excel_data = output.getvalue()

        st.download_button(
            "Download Filtered Data (Excel)",
            data=excel_data,
            file_name="gridforge_filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )