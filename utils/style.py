import streamlit as st


def apply_theme():
    """Inject the professional blue CSS theme into every Streamlit page."""
    st.markdown(
        """
        <style>
        /* ── Google Font ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* ── Global reset ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Main background ── */
        .stApp {
            background-color: #f0f4f8;
        }

        /* ── Main content area ── */
        .main .block-container {
            padding: 2rem 3rem 2rem 3rem;
            max-width: 1200px;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3a5f 0%, #15294a 100%);
            border-right: none;
        }
        [data-testid="stSidebar"] * {
            color: #cdd9e8 !important;
        }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: #ffffff !important;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        /* Sidebar nav links */
        [data-testid="stSidebar"] a {
            color: #a8c4e0 !important;
            font-weight: 500;
            text-decoration: none;
            transition: color 0.2s;
        }
        [data-testid="stSidebar"] a:hover {
            color: #ffffff !important;
        }
        /* Active page link */
        [data-testid="stSidebarNav"] li[aria-selected="true"] span {
            color: #ffffff !important;
            font-weight: 600;
        }
        [data-testid="stSidebarNav"] li[aria-selected="true"] {
            background-color: rgba(255,255,255,0.12) !important;
            border-radius: 8px;
        }
        /* Sidebar nav links hover */
        [data-testid="stSidebarNav"] li:hover {
            background-color: rgba(255,255,255,0.07) !important;
            border-radius: 8px;
        }
        [data-testid="stSidebarNav"] span {
            color: #cdd9e8 !important;
            font-size: 0.92rem;
        }

        /* ── Sidebar info box ── */
        [data-testid="stSidebar"] .stAlert {
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #a8c4e0 !important;
            border-radius: 10px;
        }

        /* ── Page headings ── */
        h1 {
            color: #1e3a5f !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            letter-spacing: -0.5px;
        }
        h2 {
            color: #1e3a5f !important;
            font-weight: 600 !important;
        }
        h3 {
            color: #2563a8 !important;
            font-weight: 600 !important;
        }

        /* ── Horizontal rule ── */
        hr {
            border: none;
            border-top: 2px solid #dbe6f3;
            margin: 1rem 0;
        }

        /* ── Info / success / warning boxes ── */
        .stAlert {
            border-radius: 10px !important;
            border-left-width: 4px !important;
        }
        [data-baseweb="notification"] {
            border-radius: 10px !important;
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dbe6f3;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            box-shadow: 0 2px 8px rgba(30, 58, 95, 0.07);
        }
        [data-testid="stMetricLabel"] {
            color: #5a7a9f !important;
            font-size: 0.82rem !important;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        [data-testid="stMetricValue"] {
            color: #1e3a5f !important;
            font-weight: 700 !important;
        }

        /* ── DataFrames / tables ── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #dbe6f3;
            box-shadow: 0 2px 8px rgba(30, 58, 95, 0.07);
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #2563a8 0%, #1e3a5f 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.6rem 0.8rem !important;
            white-space: normal !important;
            height: auto !important;
            min-height: 3.5rem !important;
            line-height: 1.3 !important;
            transition: opacity 0.2s, transform 0.1s !important;
        }
        .stButton > button:hover {
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
        }

        /* ── Selectbox / dropdown ── */
        .stSelectbox > div > div {
            border-color: #c0d4ea !important;
            border-radius: 8px !important;
        }

        /* ── Hide Streamlit branding ── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
