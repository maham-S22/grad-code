import os
import pandas as pd
import streamlit as st

# The exact working absolute path
EXCEL_PATH = r"C:\Users\maham\Desktop\University(8)\Grad Proj dashboard\Grad Proj .xlsx"


@st.cache_data(show_spinner=False)
def load_specific_sheet(sheet_name):
    """Load a single Excel sheet with cache. Casts all column names to str
    to prevent pd.concat crashes from mixed int/str headers."""
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, engine="openpyxl")

        # 1. Prevent column duplication crashes
        df.columns = df.columns.astype(str)
        df = df.loc[:, ~df.columns.duplicated()].copy()

        # 2. Prevent Streamlit from displaying "None"
        for col in df.columns:
            if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].fillna("")
            else:
                df[col] = df[col].fillna(0.0)

        return df
    except Exception as e:
        st.error(f"❌ Failed to load {sheet_name}. Error: {e}")
        return pd.DataFrame()


def save_sheet_to_excel(df, sheet_name):
    """Atomic file-swap save: writes to a temp file first, then replaces
    the original in one shot so the main file is never left in a corrupt state."""
    try:
        df.columns = df.columns.astype(str)
        df_clean = df.loc[:, ~df.columns.duplicated()].copy()

        # 1. Read the existing workbook safely
        try:
            all_sheets = pd.read_excel(EXCEL_PATH, sheet_name=None, engine="openpyxl")
        except Exception:
            all_sheets = {}

        all_sheets[sheet_name] = df_clean

        # 2. Write to a temporary ghost file first
        temp_path = EXCEL_PATH.replace(".xlsx", "_temp.xlsx")
        with pd.ExcelWriter(temp_path, engine="openpyxl", mode="w") as writer:
            for s_name, s_df in all_sheets.items():
                s_df.to_excel(writer, sheet_name=s_name, index=False)

        # 3. ATOMIC SWAP: Instantly replace the real file with the perfect temp file
        os.replace(temp_path, EXCEL_PATH)

        st.cache_data.clear()
        return True
    except Exception as e:
        # Clean up the ghost file if something failed
        temp_path = EXCEL_PATH.replace(".xlsx", "_temp.xlsx")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        st.error(f"❌ Save Failed: {e}")
        return False
