import streamlit as st
import os

# Load shared CSS
with open(os.path.join(os.path.dirname(__file__), "..", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📈 Forecast")
st.markdown("---")
st.info("Forecast models and charts will be built here in the next step.", icon="🔧")
