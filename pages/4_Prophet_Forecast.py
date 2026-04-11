import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.style import apply_theme

st.set_page_config(page_title="Prophet Forecast", page_icon="🔮", layout="wide")
apply_theme()

st.title("🔮 Prophet Forecast")
st.info("This page will show Prophet time-series forecasting results. Coming soon!", icon="🔧")
