"""
utils/data_prep.py
==================
Centralized data preparation pipeline for the ABM Inventory Dashboard.

Transforms the raw Wide-format Excel data
    (Period | 1 | 2 | 3 | … | 60)
into a Long-format time-series DataFrame
    (Date | Product | Demand)
suitable for Prophet, XGBoost, and other ML forecasting models.

Missing-value strategy (documented):
  • Numeric month columns: fill NaN → 0
    Rationale: a missing demand entry most likely represents zero sales, not
    an unrecorded observation. Using 0 is conservative and prevents leakage
    from forward/backward-fill across product boundaries.
  • After the 0-fill, a backward-fill (bfill) pass is NOT applied because
    demand data is sparse and bfill would inject artificial demand signals.
  • If a future use-case requires bfill, set `impute_strategy="bfill"` when
    calling `prepare_long_format()`.
"""

import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

# Make the project root importable when this module is run directly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import ExcelManager, TOTAL_MONTHS  # noqa: E402

# ── Constants ─────────────────────────────────────────────────────────────────
BASELINE_DATE   = datetime(2020, 1, 1)   # Period 1 maps to this date
PRODUCT_COL     = "Period"               # name of the product-ID column in raw data
MONTH_COLS      = [str(i) for i in range(1, TOTAL_MONTHS + 1)]


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
def validate_raw_df(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Check that the raw wide-format DataFrame has all required columns.

    Returns
    -------
    (ok: bool, message: str)
    """
    if df.empty:
        return False, "Raw Data is empty."

    if PRODUCT_COL not in df.columns:
        return False, f"Column '{PRODUCT_COL}' not found. Got: {list(df.columns[:5])}"

    missing_months = [m for m in MONTH_COLS if m not in df.columns]
    if missing_months:
        return False, (
            f"{len(missing_months)} month column(s) missing "
            f"(e.g. {missing_months[:3]}). "
            "Run ExcelManager.get_raw_data() to auto-expand to 60 months."
        )

    # Spot-check that month columns are numeric (or coercible)
    sample = df[MONTH_COLS[:5]].apply(pd.to_numeric, errors="coerce")
    if sample.isnull().all(axis=None):
        return False, "Month columns do not appear to contain numeric data."

    return True, "OK"


# ══════════════════════════════════════════════════════════════════════════════
# IMPUTATION
# ══════════════════════════════════════════════════════════════════════════════
def _impute(df: pd.DataFrame, strategy: str = "zero") -> pd.DataFrame:
    """
    Fill missing values in numeric month columns.

    Parameters
    ----------
    strategy : "zero" (default) or "bfill"
        "zero"  – replace NaN with 0 (conservative; treats gaps as no demand)
        "bfill" – backward-fill within each row (experimental)
    """
    df = df.copy()
    if strategy == "bfill":
        # bfill along axis=1 (across months), then fill any remaining NaN with 0
        df[MONTH_COLS] = (
            df[MONTH_COLS]
            .apply(pd.to_numeric, errors="coerce")
            .bfill(axis=1)
            .fillna(0)
            .astype(int)
        )
    else:  # default: zero-fill
        df[MONTH_COLS] = (
            df[MONTH_COLS]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
            .astype(int)
        )
    return df


# ══════════════════════════════════════════════════════════════════════════════
# WIDE → LONG TRANSFORMATION  (heavily cached)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Preparing time-series data…")
def prepare_long_format(
    df_wide: pd.DataFrame,
    impute_strategy: str = "zero",
    baseline: datetime = BASELINE_DATE,
) -> pd.DataFrame:
    """
    Transform the wide-format raw data into a long-format time-series.

    Parameters
    ----------
    df_wide : pd.DataFrame
        Wide-format DataFrame with columns: Period | 1 | 2 | … | 60
    impute_strategy : str
        Missing value strategy — "zero" (default) or "bfill"
    baseline : datetime
        The calendar date that Period/Month 1 maps to (default 2020-01-01).

    Returns
    -------
    pd.DataFrame with columns:
        Date     – datetime, one row per product-month
        Product  – product code (from the 'Period' column)
        Demand   – integer demand value
        Month    – integer month index (1–60)
    """
    ok, msg = validate_raw_df(df_wide)
    if not ok:
        raise ValueError(f"Data validation failed: {msg}")

    # 1. Impute missing values
    df = _impute(df_wide, strategy=impute_strategy)

    # 2. Melt wide → long
    df_long = df[[PRODUCT_COL] + MONTH_COLS].melt(
        id_vars=PRODUCT_COL,
        value_vars=MONTH_COLS,
        var_name="Month",
        value_name="Demand",
    )

    # 3. Cast types
    df_long["Month"]  = df_long["Month"].astype(int)
    df_long["Demand"] = df_long["Demand"].astype(int)

    # 4. Map month index → calendar date (Period 1 = baseline)
    #    Month N  →  baseline + (N-1) months
    df_long["Date"] = df_long["Month"].apply(
        lambda m: pd.Timestamp(baseline) + pd.DateOffset(months=int(m) - 1)
    )

    # 5. Rename & reorder columns
    df_long = df_long.rename(columns={PRODUCT_COL: "Product"})
    df_long = df_long[["Date", "Product", "Month", "Demand"]].sort_values(
        ["Product", "Date"]
    ).reset_index(drop=True)

    return df_long


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE: per-product series (used by forecast pages)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def get_product_series(
    df_long: pd.DataFrame,
    product: str,
) -> pd.DataFrame:
    """
    Extract the demand time-series for a single product.

    Returns a DataFrame with columns: Date, Demand
    (index reset, sorted by Date).
    """
    series = (
        df_long[df_long["Product"] == product][["Date", "Demand"]]
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return series


# ══════════════════════════════════════════════════════════════════════════════
# CACHED LOADER (called by forecast pages — avoids re-running the pipeline)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Loading & preparing data…", ttl=300)
def get_long_df(impute_strategy: str = "zero") -> pd.DataFrame:
    """
    Convenience wrapper: load raw data from session_state + run pipeline.
    TTL of 300 s ensures the cache refreshes if the Excel file is updated.
    """
    ExcelManager.load_all()
    raw = ExcelManager.get_raw_data()
    return prepare_long_format(raw, impute_strategy=impute_strategy)
