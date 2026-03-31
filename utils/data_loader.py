"""
utils/data_loader.py
Safe Excel I/O with session_state caching and write-lock mechanism.
"""
import os
import shutil
import tempfile
import pandas as pd
import streamlit as st

EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Grad Proj.xlsx")
TOTAL_MONTHS = 60
RAW_SHEET = "Raw Data"


class ExcelManager:
    """Load sheets into st.session_state (once per session) and write safely."""

    # ── Loading ──────────────────────────────────────────────────────────────
    @staticmethod
    def load_all(force: bool = False):
        """Read every sheet into session_state['sheets'][sheet_name]."""
        if "sheets" not in st.session_state or force:
            st.session_state["sheets"] = {}
        if not os.path.exists(EXCEL_PATH):
            st.error(f"Excel file not found: `{EXCEL_PATH}`")
            return

        xl = pd.ExcelFile(EXCEL_PATH)
        for name in xl.sheet_names:
            if name not in st.session_state["sheets"] or force:
                st.session_state["sheets"][name] = xl.parse(name)

    @staticmethod
    def get(sheet: str) -> pd.DataFrame:
        """Return a sheet dataframe from session_state, loading if needed."""
        if "sheets" not in st.session_state or sheet not in st.session_state["sheets"]:
            ExcelManager.load_all()
        return st.session_state["sheets"].get(sheet, pd.DataFrame())

    @staticmethod
    def set(sheet: str, df: pd.DataFrame):
        """Update a sheet in session_state without touching disk."""
        if "sheets" not in st.session_state:
            st.session_state["sheets"] = {}
        st.session_state["sheets"][sheet] = df

    # ── Saving ───────────────────────────────────────────────────────────────
    @staticmethod
    def save(sheet: str, df: pd.DataFrame) -> bool:
        """
        Write one updated sheet back to the Excel file safely:
        1. Write all sheets (updated + rest) to a temp file.
        2. Replace the original file with the temp file.
        Returns True on success.
        """
        ExcelManager.set(sheet, df)           # update session_state first

        # Collect all current sheets from session_state
        all_sheets: dict[str, pd.DataFrame] = st.session_state.get("sheets", {})

        # Write to a temp file in the same directory (same filesystem → atomic rename)
        tmp_fd, tmp_path = tempfile.mkstemp(
            suffix=".xlsx",
            dir=os.path.dirname(EXCEL_PATH),
        )
        try:
            os.close(tmp_fd)                  # close the raw fd; openpyxl will open by path
            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                for name, frame in all_sheets.items():
                    frame.to_excel(writer, sheet_name=name, index=False)
            shutil.move(tmp_path, EXCEL_PATH)  # atomic replacement
            return True
        except Exception as e:
            st.error(f"Save failed: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False

    # ── Raw Data helpers ─────────────────────────────────────────────────────
    @staticmethod
    def get_raw_data() -> pd.DataFrame:
        """Return Raw Data sheet, expanded to TOTAL_MONTHS columns."""
        df = ExcelManager.get(RAW_SHEET).copy()
        if df.empty:
            return df
        # Ensure the index column is called 'Period'
        if df.columns[0] != "Period":
            df.rename(columns={df.columns[0]: "Period"}, inplace=True)

        # Expand to 60 months — existing cols are "1".."36"
        existing = [c for c in df.columns if str(c).isdigit()]
        max_existing = max((int(c) for c in existing), default=0)
        for m in range(max_existing + 1, TOTAL_MONTHS + 1):
            df[str(m)] = 0

        # Ensure month columns are integers (not floats)
        month_cols = [str(i) for i in range(1, TOTAL_MONTHS + 1)]
        for col in month_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        return df

    @staticmethod
    def save_raw_data(df: pd.DataFrame) -> bool:
        """Persist the Raw Data dataframe back to Excel."""
        return ExcelManager.save(RAW_SHEET, df)
