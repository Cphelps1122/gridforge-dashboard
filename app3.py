import streamlit as st
import pandas as pd

from utils.data_loader import load_data
from utils.styles import inject_global_styles, enable_chart_theme


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="GridForge — Where Data Becomes Power",
    page_icon="⚡",
    layout="wide",
)

inject_global_styles()
enable_chart_theme()


# ---------------------------------------------------------
# LOAD DATA ONCE
# ---------------------------------------------------------

@st.cache_data
def load_all_data():
    return load_data()

df = load_all_data()

# Store full dataset for Portfolio page
st.session_state.df = df


# ---------------------------------------------------------
# SIDEBAR FILTERS (Shown on Every Page)
# ---------------------------------------------------------

st.sidebar.title("Filters")

# Property filter
properties = sorted(df["property"].unique())
selected_property = st.sidebar.selectbox("Property", properties)

# Utility filter
utilities = sorted(df[df["property"] == selected_property]["utility"].unique())
selected_utility = st.sidebar.selectbox("Utility", utilities)

# Year filter
years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect("Year(s)", years, default=years)

# Comparison property
comparison_property = st.sidebar.selectbox(
    "Comparison Property (optional)",
    ["None"] + properties,
    index=0
)

# Normalize toggle
normalize = st.sidebar.checkbox("Normalize by Occupancy", value=False)


# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------

df_filtered = df[
    (df["property"] == selected_property)
    & (df["utility"] == selected_utility)
    & (df["year"].isin(selected_years))
]

df_comparison = None
if comparison_property != "None":
    df_comparison = df[
        (df["property"] == comparison_property)
        & (df["utility"] == selected_utility)
        & (df["year"].isin(selected_years))
    ]


# ---------------------------------------------------------
# STORE FILTERED DATA IN SESSION STATE
# ---------------------------------------------------------

st.session_state.df_filtered = df_filtered
st.session_state.df_comparison = df_comparison
st.session_state.normalize = normalize


# ---------------------------------------------------------
# HOME PAGE (HERO SECTION)
# ---------------------------------------------------------

st.markdown(
    """
    <div style="padding: 40px 0 20px 0;">
        <h1 style="
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 0;
            color: #1A73E8;
            font-family: 'Segoe UI', sans-serif;
        ">
            GridForge
        </h1>

        <h2 style="
            font-size: 24px;
            font-weight: 500;
            margin-top: 5px;
            color: #444444;
            font-family: 'Segoe UI', sans-serif;
        ">
            Where Data Becomes Power
        </h2>

        <p style="
            font-size: 18px;
            color: #555555;
            max-width: 700px;
            margin-top: 20px;
            font-family: 'Segoe UI', sans-serif;
        ">
            GridForge transforms raw utility bills into actionable intelligence.
            Explore trends, forecast usage, benchmark performance, detect anomalies,
            and understand your portfolio like never before — all in one unified platform.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# FEATURE HIGHLIGHTS
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="gridforge-card">
            <h4 style="margin:0; font-size:20px; color:#1A73E8;">Intelligent Forecasting</h4>
            <p style="margin-top:8px; color:#555;">AI-powered predictions with benchmark overlays.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="gridforge-card">
            <h4 style="margin:0; font-size:20px; color:#1A73E8;">Deep Analytics</h4>
            <p style="margin-top:8px; color:#555;">Trends, occupancy insights, provider comparisons, and more.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="gridforge-card">
            <h4 style="margin:0; font-size:20px; color:#1A73E8;">Smart Alerts</h4>
            <p style="margin-top:8px; color:#555;">Automatic detection of spikes, anomalies, and missing bills.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# CTA BUTTON
# ---------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

start = st.button("Start Exploring →")

if start:
    st.switch_page("pages/1_Overview.py")
