# ---------------------------------------------------------
# GRIDFORGE — TXU-STYLE FULL APP (app2.py)
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
    "background": "#F4F8FF"    # Soft TXU-style background
}

GRIDFORGE_FONTS = {
    "header": "font-family: 'Segoe UI', sans-serif; font-weight: 700;",
    "subheader": "font-family: 'Segoe UI', sans-serif; font-weight: 600;",
    "body": "font-family: 'Segoe UI', sans-serif; font-weight: 400;",
}

st.set_page_config(
    page_title="GridForge — Where Data Becomes Power",
    layout="wide"
)

# ---------------------------------------------------------
# GLOBAL STYLING — BUTTONS & ALTAIR THEME
# ---------------------------------------------------------

st.markdown(
    f"""
    <style>
        body {{
            background-color: #f4f6fb;
        }}
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
            },
            "view": {
                "stroke": "transparent"
            }
        }
    }

alt.themes.register("gridforge", gridforge_chart_theme)
alt.themes.enable("gridforge")

# ---------------------------------------------------------
# HEADER — LOGO + TITLE (TXU-STYLE TOP BAR)
# ---------------------------------------------------------

header_cols = st.columns([1, 5])

with header_cols[0]:
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
            margin-bottom: 10px;
        ">
            <h1 style="
                font-size: 30px;
                margin-bottom: 0;
                color: {GRIDFORGE_COLORS['text_main']};
                {GRIDFORGE_FONTS['header']}
                letter-spacing: -0.5px;
            ">
                GridForge Energy Dashboard
            </h1>
            <p style="
                font-size: 14px;
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
# LOAD DATA (Sheet1)
# ---------------------------------------------------------

@st.cache_data
def load_data():
    df_raw = pd.read_excel("Database with pivot tables.xlsx", sheet_name="Sheet1")
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
except Exception:
    st.error("Error loading data. Ensure 'Database with pivot tables.xlsx' is in the app directory.")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (LIGHT, CLEAN)
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
# GLOBAL FILTERS (TXU-STYLE FILTER CARD)
# ---------------------------------------------------------

st.markdown(
    f"""
    <div id="filters" style="
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 10px 0 25px 0;
    ">
        <h3 style="
            {GRIDFORGE_FONTS['subheader']}
            font-size: 18px;
            color:{GRIDFORGE_COLORS['text_main']};
            margin-bottom: 10px;
        ">
            Filters
        </h3>
        <p style="
            {GRIDFORGE_FONTS['body']}
            font-size: 13px;
            color:{GRIDFORGE_COLORS['text_subtle']};
            margin-top: 0;
            margin-bottom: 10px;
        ">
            Choose a property, utility, and time frame to explore usage, trends, and forecasts.
        </p>
    </div>
    """,
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

if normalize:
    if "units" in df_filtered.columns:
        df_filtered["usage"] = df_filtered["usage"] / df_filtered["units"]
        df_filtered["cost"] = df_filtered["cost"] / df_filtered["units"]
    if df_compare is not None and "units" in df_compare.columns:
        df_compare["usage"] = df_compare["usage"] / df_compare["units"]
        df_compare["cost"] = df_compare["cost"] / df_compare["units"]

# ---------------------------------------------------------
# PAGE: HOME — TXU-STYLE WIDE, CENTERED LAYOUT
# ---------------------------------------------------------

if page == "Home":
    # Hero
    st.markdown(
        f"""
        <div style="
            width: 100%;
            padding: 50px 40px;
            border-radius: 12px;
            background: linear-gradient(90deg, #ffffff 0%, #f4f8ff 100%);
            margin-bottom: 40px;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="max-width: 55%;">
                <h1 style="
                    font-size: 40px;
                    font-weight: 700;
                    color: {GRIDFORGE_COLORS['primary']};
                    margin-bottom: 10px;
                    {GRIDFORGE_FONTS['header']}
                ">
                    Smarter Energy Insights for Every Property
                </h1>

                <p style="
                    font-size: 17px;
                    color: #444;
                    line-height: 1.5;
                    margin-bottom: 22px;
                    {GRIDFORGE_FONTS['body']}
                ">
                    GridForge turns raw utility data into clear, actionable insight — helping you track usage,
                    compare properties, and forecast what comes next with confidence.
                </p>

                <a href="#filters" style="
                    background-color: {GRIDFORGE_COLORS['primary']};
                    color: white;
                    padding: 11px 24px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-size: 15px;
                    {GRIDFORGE_FONTS['subheader']}
                ">
                    Start Exploring Your Data
                </a>
            </div>

            <div style="max-width: 40%; text-align: right;">
                <img src="gridforge_logo.png" style="width: 260px; opacity: 0.9;" />
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3-column feature section
    st.markdown(
        f"""
        <div id="overview" style="margin-top: 10px; margin-bottom: 30px;">
            <h2 style="
                font-size: 30px;
                font-weight: 700;
                color: {GRIDFORGE_COLORS['text_main']};
                text-align: center;
                margin-bottom: 8px;
                {GRIDFORGE_FONTS['header']}
            ">
                What GridForge Delivers
            </h2>

            <p style="
                font-size: 16px;
                color: {GRIDFORGE_COLORS['text_subtle']};
                text-align: center;
                max-width: 700px;
                margin: 0 auto 30px auto;
                line-height: 1.5;
                {GRIDFORGE_FONTS['body']}
            ">
                A modern, intuitive platform designed to help you understand your utility data,
                identify trends, and make smarter decisions across your entire portfolio.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 22px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                height: 100%;
            ">
                <h3 style="font-size: 19px; font-weight: 700; color:{GRIDFORGE_COLORS['primary']};">
                    Unified Usage Tracking
                </h3>
                <p style="color:#555; font-size:14px; line-height:1.5;">
                    View electricity, water, and gas usage across all properties in one clean, centralized dashboard.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colB:
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 22px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                height: 100%;
            ">
                <h3 style="font-size: 19px; font-weight: 700; color:{GRIDFORGE_COLORS['primary']};">
                    Benchmark-Aware Forecasting
                </h3>
                <p style="color:#555; font-size:14px; line-height:1.5;">
                    Compare your projected usage against national-style benchmarks to see where you’re leading or lagging.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colC:
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 22px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                height: 100%;
            ">
                <h3 style="font-size: 19px; font-weight: 700; color:{GRIDFORGE_COLORS['primary']};">
                    Portfolio-Level Insights
                </h3>
                <p style="color:#555; font-size:14px; line-height:1.5;">
                    Instantly compare properties, utilities, and time periods to uncover hidden patterns and outliers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Divider + CTA
    st.markdown(
        """
        <div style="
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #e6ecf5 0%, #ffffff 100%);
            margin: 40px 0 30px 0;
        "></div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 30px 20px;
            background: #f7faff;
            border-radius: 12px;
        ">
            <h2 style="
                font-size: 26px;
                font-weight: 700;
                color:{GRIDFORGE_COLORS['primary']};
                margin-bottom: 8px;
            ">
                Ready to Dive Deeper?
            </h2>

            <p style="
                font-size: 15px;
                color:#555;
                max-width: 600px;
                margin: 0 auto 20px auto;
            ">
                Use the navigation on the left to explore detailed KPIs, trends, forecasts, and exports
                for the filters you’ve selected.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# PAGE: OVERVIEW — TXU-STYLE KPI CARDS
# ---------------------------------------------------------

elif page == "Overview":
    st.markdown(
        f"""
        <div style="
            margin-top: 10px;
            margin-bottom: 20px;
        ">
            <h3 style="
                {GRIDFORGE_FONTS['subheader']}
                font-size: 22px;
                color:{GRIDFORGE_COLORS['text_main']};
                margin-bottom: 5px;
            ">
                Overview
            </h3>
            <p style="
                {GRIDFORGE_FONTS['body']}
                font-size: 14px;
                color:{GRIDFORGE_COLORS['text_subtle']};
            ">
                High-level view of usage and cost for your selected property and utility.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        total_usage = df_filtered["usage"].sum()
        total_cost = df_filtered["cost"].sum()
        avg_usage = df_filtered["usage"].mean()
        avg_cost = df_filtered["cost"].mean()

        k1, k2, k3, k4 = st.columns(4)

        def kpi_card(title, value):
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 18px 18px 14px 18px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    text-align: left;
                ">
                    <div style="font-size: 12px; color:{GRIDFORGE_COLORS['text_subtle']}; margin-bottom: 4px;">
                        {title}
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color:{GRIDFORGE_COLORS['text_main']};">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k1:
            kpi_card("Total Usage", f"{total_usage:,.0f}")
        with k2:
            kpi_card("Total Cost", f"${total_cost:,.0f}")
        with k3:
            kpi_card("Average Usage", f"{avg_usage:,.0f}")
        with k4:
            kpi_card("Average Cost", f"${avg_cost:,.0f}")

        if df_compare is not None and not df_compare.empty:
            st.markdown(
                f"""
                <div style="margin-top: 25px; margin-bottom: 10px;">
                    <h4 style="
                        {GRIDFORGE_FONTS['subheader']}
                        font-size: 18px;
                        color:{GRIDFORGE_COLORS['text_main']};
                    ">
                        Comparison Property KPIs
                    </h4>
                </div>
                """,
                unsafe_allow_html=True
            )

            comp_usage = df_compare["usage"].sum()
            comp_cost = df_compare["cost"].sum()

            c1, c2 = st.columns(2)
            with c1:
                kpi_card(f"{compare_property} Total Usage", f"{comp_usage:,.0f}")
            with c2:
                kpi_card(f"{compare_property} Total Cost", f"${comp_cost:,.0f}")

# ---------------------------------------------------------
# PAGE: TRENDS — TXU-STYLE CHARTS
# ---------------------------------------------------------

elif page == "Trends":
    st.markdown(
        f"""
        <div style="
            margin-top: 10px;
            margin-bottom: 15px;
        ">
            <h3 style="
                {GRIDFORGE_FONTS['subheader']}
                font-size: 22px;
                color:{GRIDFORGE_COLORS['text_main']};
                margin-bottom: 5px;
            ">
                Trends
            </h3>
            <p style="
                {GRIDFORGE_FONTS['body']}
                font-size: 14px;
                color:{GRIDFORGE_COLORS['text_subtle']};
            ">
                Explore how usage and cost evolve over time for your selected filters.
            </p>
        </div>
        """,
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

        st.markdown(
            """
            <div style="
                background:white;
                border-radius:12px;
                padding:18px;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);
                margin-bottom:18px;
            ">
            """,
            unsafe_allow_html=True
        )
        st.altair_chart(usage_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
                background:white;
                border-radius:12px;
                padding:18px;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);
                margin-top:5px;
            ">
            """,
            unsafe_allow_html=True
        )
        st.altair_chart(cost_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if df_compare is not None and not df_compare.empty:
            st.markdown(
                f"""
                <div style="margin-top: 25px; margin-bottom: 10px;">
                    <h4 style="
                        {GRIDFORGE_FONTS['subheader']}
                        font-size: 18px;
                        color:{GRIDFORGE_COLORS['text_main']};
                    ">
                        Usage Comparison
                    </h4>
                </div>
                """,
                unsafe_allow_html=True
            )

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

            st.markdown(
                """
                <div style="
                    background:white;
                    border-radius:12px;
                    padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);
                    margin-top:5px;
                ">
                """,
                unsafe_allow_html=True
            )
            st.altair_chart(comp_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE: FORECASTING — TXU-STYLE WITH BENCHMARK
# ---------------------------------------------------------

elif page == "Forecasting":
    st.markdown(
        f"""
        <div style="
            margin-top: 10px;
            margin-bottom: 15px;
        ">
            <h3 style="
                {GRIDFORGE_FONTS['subheader']}
                font-size: 22px;
                color:{GRIDFORGE_COLORS['text_main']};
                margin-bottom: 5px;
            ">
                Forecasting
            </h3>
            <p style="
                {GRIDFORGE_FONTS['body']}
                font-size: 14px;
                color:{GRIDFORGE_COLORS['text_subtle']};
            ">
                Project future usage and compare it against a simple national-style benchmark.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        # Monthly aggregation
        df_monthly = df_filtered.copy()
        df_monthly["month"] = df_monthly["date"].dt.to_period("M").dt.to_timestamp()
        monthly_usage = df_monthly.groupby("month")["usage"].sum().reset_index()

        # Fill missing months
        full_range = pd.date_range(
            start=monthly_usage["month"].min(),
            end=monthly_usage["month"].max(),
            freq="MS"
        )
        monthly_usage = (
            monthly_usage
            .set_index("month")
            .reindex(full_range)
            .fillna(0)
            .rename_axis("ds")
            .reset_index()
        )
        monthly_usage.rename(columns={"usage": "y"}, inplace=True)

        if len(monthly_usage) < 6:
            st.warning("Need at least 6 months of history to run a meaningful forecast.")
        else:
            forecast_months = st.slider(
                "Forecast months ahead",
                min_value=3,
                max_value=24,
                value=12,
                step=3
            )

            model = Prophet()
            model.fit(monthly_usage)
            future = model.make_future_dataframe(periods=forecast_months, freq="MS")
            forecast = model.predict(future)

            chart_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].merge(
                monthly_usage, on="ds", how="left"
            )

            base = alt.Chart(chart_df).encode(x="ds:T")

            band = base.mark_area(opacity=0.18, color=GRIDFORGE_COLORS["primary"]).encode(
                y="yhat_lower:Q",
                y2="yhat_upper:Q"
            )

            actual = base.mark_line(point=True, color=GRIDFORGE_COLORS["accent"]).encode(
                y=alt.Y("y:Q", title="Monthly Usage"),
                tooltip=["ds:T", "y:Q"]
            )

            forecast_line = base.mark_line(color=GRIDFORGE_COLORS["primary_dark"]).encode(
                y="yhat:Q",
                tooltip=["ds:T", "yhat:Q"]
            )

            # Simple benchmark
            BENCHMARK_USAGE_PER_UNIT = {
                "Electricity": 1200,
                "Gas": 300,
                "Water": 25000,
            }

            benchmark_chart = None
            benchmark_value = None

            if "units" in df_filtered.columns and selected_utility in BENCHMARK_USAGE_PER_UNIT:
                units = df_filtered["units"].iloc[0]
                benchmark_value = units * BENCHMARK_USAGE_PER_UNIT[selected_utility]

                bench_df = forecast[["ds"]].copy()
                bench_df["benchmark"] = benchmark_value

                benchmark_chart = (
                    alt.Chart(bench_df)
                    .mark_line(strokeDash=[4, 4], color="#666666")
                    .encode(
                        x="ds:T",
                        y="benchmark:Q",
                        tooltip=["ds:T", "benchmark:Q"]
                    )
                )

            st.markdown(
                """
                <div style="
                    background:white;
                    border-radius:12px;
                    padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);
                    margin-bottom:18px;
                ">
                """,
                unsafe_allow_html=True
            )

            if benchmark_chart is not None:
                st.altair_chart(band + actual + forecast_line + benchmark_chart, use_container_width=True)
                st.caption(
                    "Orange = actual, Blue = forecast, shaded area = confidence interval, "
                    "dashed grey = benchmark usage based on national-style assumptions."
                )
            else:
                st.altair_chart(band + actual + forecast_line, use_container_width=True)
                st.caption("Orange = actual, Blue = forecast, shaded area = confidence interval.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Narrative summary
            last_actual = monthly_usage.dropna(subset=["y"]).tail(1)
            future_only = forecast[forecast["ds"] > monthly_usage["ds"].max()]

            if not last_actual.empty and not future_only.empty:
                last_actual_val = float(last_actual["y"].iloc[0])
                next_3 = future_only.head(3)
                avg_forecast_next_3 = float(next_3["yhat"].mean())

                summary = f"""
                **Forecast Summary for {selected_property} — {selected_utility}**

                - Last actual month usage: **{last_actual_val:,.0f}**
                - Average forecasted usage (next 3 months): **{avg_forecast_next_3:,.0f}**
                """

                if benchmark_value is not None:
                    diff_pct = (avg_forecast_next_3 - benchmark_value) / benchmark_value * 100
                    direction = "above" if diff_pct > 0 else "below"
                    summary += f"""
                    - Benchmark usage (national-style assumption): **{benchmark_value:,.0f}**
                    - You are trending **{abs(diff_pct):.1f}% {direction}** the benchmark.
                    """

                st.markdown(
                    f"""
                    <div style="
                        background:white;
                        border-radius:12px;
                        padding:18px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);
                        margin-top:10px;
                    ">
                        {summary}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ---------------------------------------------------------
# PAGE: EXPORTS — TXU-STYLE EXPORT CARD
# ---------------------------------------------------------

elif page == "Exports":
    st.markdown(
        f"""
        <div style="
            margin-top: 10px;
            margin-bottom: 15px;
        ">
            <h3 style="
                {GRIDFORGE_FONTS['subheader']}
                font-size: 22px;
                color:{GRIDFORGE_COLORS['text_main']};
                margin-bottom: 5px;
            ">
                Exports
            </h3>
            <p style="
                {GRIDFORGE_FONTS['body']}
                font-size: 14px;
                color:{GRIDFORGE_COLORS['text_subtle']};
            ">
                Download the currently filtered dataset for offline analysis or reporting.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
    else:
        st.markdown(
            """
            <div style="
                background:white;
                border-radius:12px;
                padding:18px;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);
                margin-bottom:18px;
            ">
            """,
            unsafe_allow_html=True
        )

        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Filtered Data (CSV)",
            data=csv_data,
            file_name="gridforge_filtered_data.csv",
            mime="text/csv"
        )

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

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER — LIGHT, MINIMAL
# ---------------------------------------------------------

st.markdown(
    f"""
    <div style="
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid {GRIDFORGE_COLORS['border']};
        font-size: 11px;
        color:{GRIDFORGE_COLORS['text_subtle']};
        text-align: right;
    ">
        Powered by GridForge — Where Data Becomes Power
    </div>
    """,
    unsafe_allow_html=True
)
