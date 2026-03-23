import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_data

# Load shared CSS
with open(os.path.join(os.path.dirname(__file__), "..", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

df = load_data()

st.title("🏠 Home")
st.markdown("Welcome to the **Grad Project Dashboard**. Use the sidebar to navigate between sections.")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("### 📌 Dataset Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Rows",    f"{len(df):,}")
col2.metric("Total Columns", f"{df.shape[1]}")
col3.metric("Missing Values",f"{df.isnull().sum().sum():,}")

# ── Column Summary ─────────────────────────────────────────────────────────────
st.markdown("### 🗂️ Column Summary")
import pandas as pd
summary = pd.DataFrame({
    "Column":    df.columns,
    "Type":      df.dtypes.values,
    "Non-Null":  df.notnull().sum().values,
    "Nulls":     df.isnull().sum().values,
})
st.dataframe(summary, use_container_width=True, hide_index=True)
