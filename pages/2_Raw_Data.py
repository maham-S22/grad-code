"""
pages/2_Raw_Data.py
Phase 2 – Raw Data page: view, add products, edit monthly values, save.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from utils.style import apply_theme
from utils.data_loader import ExcelManager, TOTAL_MONTHS

st.set_page_config(page_title="Raw Data – ABM Dashboard", page_icon="📋", layout="wide")
apply_theme()

# ── Ensure data is loaded ─────────────────────────────────────────────────────
ExcelManager.load_all()

st.title("📋 Raw Data")
st.markdown("Source: **Raw Data** sheet · 447 products · Months 1 – 60")
st.markdown("---")

# ── Get working copy from session_state ──────────────────────────────────────
df = ExcelManager.get_raw_data()

if df.empty:
    st.error("Could not load Raw Data. Make sure `Grad Proj.xlsx` is in the project folder.")
    st.stop()

MONTH_COLS = [str(i) for i in range(1, TOTAL_MONTHS + 1)]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – View (read-only overview)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📊 View Full Dataset", expanded=True):
    st.caption(f"{len(df)} products · {TOTAL_MONTHS} months")
    # Show all 60 month columns
    display_cols = ["Period"] + MONTH_COLS
    st.dataframe(
        df[display_cols].set_index("Period"),
        use_container_width=True,
        height=320,
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Add New Product
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("➕ Add New Product")

with st.form("add_product_form", clear_on_submit=True):
    new_name = st.text_input("Product Name / Code", placeholder="e.g. A 999 XX")
    st.caption("Monthly demand values (Month 1 – 60) — you can leave as 0 and update later.")

    # 6 columns × 10 rows of number inputs
    cols_per_row = 6
    month_values: dict[str, int] = {}
    for row_start in range(0, TOTAL_MONTHS, cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            m = row_start + i + 1
            if m <= TOTAL_MONTHS:
                month_values[str(m)] = col.number_input(
                    f"M{m}", min_value=0, value=0, step=1, key=f"add_m{m}"
                )

    submitted = st.form_submit_button("✅ Add Product", use_container_width=True)

if submitted:
    if not new_name.strip():
        st.warning("Please enter a product name.")
    elif new_name.strip() in df["Period"].astype(str).values:
        st.warning(f"Product **{new_name.strip()}** already exists. Use the Edit section below.")
    else:
        new_row = {"Period": new_name.strip()} | month_values
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        if ExcelManager.save_raw_data(df):
            st.success(f"✅ Product **{new_name.strip()}** added and saved!")
            df = ExcelManager.get_raw_data()   # reload from session_state
        else:
            st.error("Save failed — see error above.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – Edit Monthly Data for Existing Product
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("✏️ Edit Monthly Data")

product_list = df["Period"].astype(str).tolist()
selected_product = st.selectbox("Select Product", options=product_list, index=0)

if selected_product:
    row = df[df["Period"].astype(str) == selected_product].iloc[0]

    with st.form("edit_product_form"):
        st.markdown(f"**Editing:** `{selected_product}`")
        updated_values: dict[str, int] = {}
        cols_per_row = 6
        for row_start in range(0, TOTAL_MONTHS, cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                m = row_start + i + 1
                if m <= TOTAL_MONTHS:
                    cur_val = int(row.get(str(m), 0)) if pd.notna(row.get(str(m), 0)) else 0
                    updated_values[str(m)] = col.number_input(
                        f"M{m}", min_value=0, value=cur_val, step=1, key=f"edit_m{m}"
                    )

        save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

    if save_btn:
        idx = df[df["Period"].astype(str) == selected_product].index[0]
        for col, val in updated_values.items():
            df.at[idx, col] = val
        if ExcelManager.save_raw_data(df):
            st.success(f"✅ Data for **{selected_product}** saved successfully!")
            df = ExcelManager.get_raw_data()
        else:
            st.error("Save failed — see error above.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – Inline editable table (power users)
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("🗂️ Bulk Edit via Table")
st.caption("Double-click any cell to edit. Press **Save Table** when done.")

edit_cols = ["Period"] + MONTH_COLS
column_config = {"Period": st.column_config.TextColumn("Product", width="medium")}
for m in range(1, TOTAL_MONTHS + 1):
    column_config[str(m)] = st.column_config.NumberColumn(
        f"M{m}", min_value=0, step=1, format="%d"
    )

edited_df = st.data_editor(
    df[edit_cols].copy(),
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    height=400,
    key="bulk_editor",
)

if st.button("💾 Save Table", type="primary", use_container_width=False):
    # Merge edits back into full df (keep any non-displayed columns)
    other_cols = [c for c in df.columns if c not in edit_cols]
    merged = edited_df.copy()
    for col in other_cols:
        merged[col] = df[col].values[: len(merged)]
    if ExcelManager.save_raw_data(merged):
        st.success("✅ Table saved successfully!")
        df = ExcelManager.get_raw_data()
        st.rerun()
    else:
        st.error("Save failed — see error above.")

st.markdown("---")
st.caption("ABM Inventory Dashboard · Raw Data")
