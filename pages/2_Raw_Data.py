import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.style import apply_theme

st.set_page_config(page_title="Raw Data", page_icon="📋", layout="wide")
apply_theme()

st.title("📋 Raw Data")
st.info("This page will display the raw data from the Excel file. Coming soon!", icon="🔧")
