import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))
from utils.style import apply_theme

st.set_page_config(
    page_title="ABM Inventory Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# ── Sidebar header ────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 Dashboard")
st.sidebar.markdown("---")
st.sidebar.info("Select a page from the menu above to get started.", icon="👆")

# ── Landing content (shown when user visits root) ─────────────────────────────
st.title("📊 Integrated ML & OR Approach to Adaptive Inventory Lot Sizing for ABM Eşyaları")
st.markdown("---")

st.markdown(
    """
    Welcome! Use the **sidebar** on the left to navigate between pages.

    | Page | Description |
    |---|---|
    | 🏠 Home | Project overview & instructions |
    | 📋 Raw Data | Browse and filter the dataset |
    | 💰 Price | Price trend analysis |
    | 🔮 Prophet Forecast | Time-series forecasting with Prophet |
    | 🤖 XGBoost Forecast | Gradient-boosted tree forecasting |
    | 📈 PX Forecast | PX forecasting approach |
    """
)
