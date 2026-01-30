import streamlit as st
import altair as alt

# ---------------------------------------------------------
# COLOR PALETTE — TXU-INSPIRED + GRIDFORGE BRAND
# ---------------------------------------------------------

GRIDFORGE_COLORS = {
    "primary": "#1A73E8",          # GridForge Blue
    "primary_dark": "#1558A6",
    "accent": "#FF7A00",           # Power Orange
    "background": "#F4F8FF",       # Soft TXU-style background
    "text_main": "#222222",
    "text_subtle": "#555555",
    "border": "#E0E0E0",
    "card_bg": "#FFFFFF",
}


# ---------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------

GRIDFORGE_FONTS = {
    "header": "font-family: 'Segoe UI', sans-serif; font-weight: 700;",
    "subheader": "font-family: 'Segoe UI', sans-serif; font-weight: 600;",
    "body": "font-family: 'Segoe UI', sans-serif; font-weight: 400;",
}


# ---------------------------------------------------------
# GLOBAL CSS INJECTION
# ---------------------------------------------------------

def inject_global_styles():
    """
    Inject global CSS for buttons, background, spacing, and layout.
    """
    st.markdown(
        f"""
        <style>
            /* Background */
            body {{
                background-color: {GRIDFORGE_COLORS['background']};
            }}

            /* Buttons */
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

            /* Card styling */
            .gridforge-card {{
                background-color: {GRIDFORGE_COLORS['card_bg']};
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                margin-bottom: 15px;
            }}

            /* Section header spacing */
            .gridforge-section {{
                margin-top: 10px;
                margin-bottom: 15px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# CARD COMPONENTS
# ---------------------------------------------------------

def card(title: str, body: str):
    """
    Render a TXU-style card with a title and body text.
    """
    st.markdown(
        f"""
        <div class="gridforge-card">
            <h4 style="
                {GRIDFORGE_FONTS['subheader']}
                font-size: 18px;
                color:{GRIDFORGE_COLORS['primary']};
                margin-bottom: 6px;
            ">
                {title}
            </h4>

            <p style="
                {GRIDFORGE_FONTS['body']}
                font-size: 14px;
                color:{GRIDFORGE_COLORS['text_subtle']};
                margin: 0;
            ">
                {body}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def kpi_card(label: str, value: str):
    """
    Render a KPI card used in Overview, Trends, Portfolio, etc.
    """
    st.markdown(
        f"""
        <div class="gridforge-card" style="text-align:left;">
            <div style="
                font-size: 12px;
                color:{GRIDFORGE_COLORS['text_subtle']};
                margin-bottom: 4px;
                {GRIDFORGE_FONTS['body']}
            ">
                {label}
            </div>

            <div style="
                font-size: 22px;
                font-weight: 700;
                color:{GRIDFORGE_COLORS['text_main']};
                {GRIDFORGE_FONTS['header']}
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# SECTION DIVIDER
# ---------------------------------------------------------

def section_divider():
    """
    TXU-style soft gradient divider.
    """
    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #e6ecf5 0%, #ffffff 100%);
            margin: 30px 0;
        "></div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# ALTAIR THEME
# ---------------------------------------------------------

def gridforge_chart_theme():
    """
    Altair theme for consistent chart styling.
    """
    return {
        "config": {
            "title": {
                "fontSize": 18,
                "font": "Segoe UI",
                "color": GRIDFORGE_COLORS["text_main"],
            },
            "axis": {
                "labelFont": "Segoe UI",
                "titleFont": "Segoe UI",
                "labelColor": GRIDFORGE_COLORS["text_subtle"],
                "titleColor": GRIDFORGE_COLORS["text_main"],
            },
            "legend": {
                "labelFont": "Segoe UI",
                "titleFont": "Segoe UI",
            },
            "view": {
                "stroke": "transparent"
            }
        }
    }


def enable_chart_theme():
    """
    Register and enable the GridForge Altair theme.
    """
    alt.themes.register("gridforge", gridforge_chart_theme)
    alt.themes.enable("gridforge")
