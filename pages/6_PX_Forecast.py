import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.style import apply_theme

st.set_page_config(page_title="PX Forecast", page_icon="📈", layout="wide")
apply_theme()

st.title("📈 PX Forecast")
st.info("This page will show PX forecasting results. Coming soon!", icon="🔧")
