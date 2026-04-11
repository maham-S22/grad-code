import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.style import apply_theme

st.set_page_config(page_title="XGBoost Forecast", page_icon="🤖", layout="wide")
apply_theme()

st.title("🤖 XGBoost Forecast")
st.info("This page will show XGBoost forecasting results. Coming soon!", icon="🔧")
