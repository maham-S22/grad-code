import streamlit as st
import pandas as pd
import os

# Path relative to project root
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "Grad Proj.xlsx")

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the main Excel dataset."""
    return pd.read_excel(DATA_FILE)

def save_data(df: pd.DataFrame) -> None:
    """Save the DataFrame back to the Excel file and clear cache."""
    df.to_excel(DATA_FILE, index=False)
    load_data.clear()  # bust cache so next load_data() call re-reads the file
