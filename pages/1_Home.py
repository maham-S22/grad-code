import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.style import apply_theme

st.set_page_config(
    page_title="ABM Inventory Dashboard",
    page_icon="🏠",
    layout="wide",
)
apply_theme()

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🎓 Integrated ML & OR Approach to Adaptive Inventory Lot Sizing for ABM Eşyaları")
st.markdown("---")

# ── Project Description ───────────────────────────────────────────────────────
st.subheader("📌 About This Project")
st.markdown(
    """
    This dashboard provides an end-to-end analysis and forecasting tool built for the
    graduation project. It loads real-world data from an Excel file and allows you to:

    - 🔍 **Explore raw data** with filters and statistics
    - 💰 **Analyse price trends** over time
    - 🔮 **Forecast using Prophet** – a time-series model by Meta
    - 🤖 **Forecast using XGBoost** – a gradient-boosted tree model
    - 📈 **Forecast using PX** – an additional forecasting approach
    """
)

st.markdown("---")

# ── Instructions ─────────────────────────────────────────────────────────────
st.subheader("🗺️ How to Use")
st.markdown(
    """
    1. **Navigate** using the sidebar on the left — click any page name to open it.
    2. Start with **Raw Data** to verify the loaded dataset looks correct.
    3. Move to **Price** to explore price behaviour across the dataset.
    4. Use the **Forecast** pages to generate and compare predictions.
    5. All pages read from `Grad Proj.xlsx` placed in the same folder as this app.
    """
)

st.info(
    "💡 Make sure `Grad Proj.xlsx` is present in the project folder before navigating to any data page.",
    icon="📁",
)

st.markdown("---")
st.caption("Graduation Project Dashboard · Built with Streamlit")
