"""
pages/2_Raw_Data.py  –  Phase 2 (Full CRUD: Add, Edit, Delete)
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from utils.style import apply_theme
from utils.data_loader import ExcelManager, TOTAL_MONTHS

st.set_page_config(page_title="Raw Data – ABM Dashboard", page_icon="📋", layout="wide")
apply_theme()

# ── Red danger-button CSS (scoped to [data-testid="stBaseButton-secondary"]) ──
st.markdown("""
<style>
[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, #dc2626, #991b1b) !important;
    color: white !important;
    border: 1px solid #991b1b !important;
    font-weight: 600 !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

ExcelManager.load_all()

# ── Session-state keys ────────────────────────────────────────────────────────
for key, default in [
    ("pending_save",        False),
    ("validation_error",    None),
    ("new_product_name",    ""),
    ("temp_monthly_data",   []),
    ("current_month_value", 0),
    ("confirm_delete",      False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Load working copy ─────────────────────────────────────────────────────────
st.title("📋 Raw Data")
st.markdown(f"Source: **Raw Data** sheet · Months 1–{TOTAL_MONTHS}")
st.markdown("---")

df = ExcelManager.get_raw_data()
if df.empty:
    st.error("Could not load Raw Data. Ensure `Grad Proj.xlsx` is in the project folder.")
    st.stop()

MONTH_COLS = [str(i) for i in range(1, TOTAL_MONTHS + 1)]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – Add New Product  (sequential month entry)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➕ Add New Product", expanded=False):
    st.session_state["new_product_name"] = st.text_input(
        "Product Name / Code",
        value=st.session_state["new_product_name"],
        placeholder="e.g. A 999 XX",
        key="product_name_input",
    )
    months_entered = len(st.session_state["temp_monthly_data"])
    next_month     = months_entered + 1
    st.markdown("---")

    if next_month <= TOTAL_MONTHS:
        st.markdown(f"**📅 Enter value for Month {next_month}** of {TOTAL_MONTHS}")
        col_input, col_add, col_undo = st.columns([3, 1, 1])
        with col_input:
            month_val = st.number_input(
                f"Month {next_month} demand",
                min_value=0, value=st.session_state["current_month_value"],
                step=1, key="seq_month_input", label_visibility="collapsed",
            )
        with col_add:
            if st.button("➕ Add Month", use_container_width=True, type="primary"):
                st.session_state["temp_monthly_data"].append(int(month_val))
                st.session_state["current_month_value"] = 0
                st.rerun()
        with col_undo:
            if st.button("↩️ Undo", use_container_width=True,
                         disabled=months_entered == 0, type="primary"):
                st.session_state["temp_monthly_data"].pop()
                st.rerun()
    else:
        st.success(f"✅ All {TOTAL_MONTHS} months entered! Ready to save.")

    st.progress(months_entered / TOTAL_MONTHS,
                text=f"{months_entered} / {TOTAL_MONTHS} months filled")

    if st.session_state["temp_monthly_data"]:
        st.markdown("**📊 Live Preview:**")
        st.dataframe(
            pd.DataFrame({f"M{i+1}": [v]
                          for i, v in enumerate(st.session_state["temp_monthly_data"])}),
            use_container_width=True, hide_index=True,
        )
    st.markdown("---")

    can_save = bool(st.session_state["new_product_name"].strip()) and months_entered > 0
    if st.button("💾 Save Changes to Excel", type="primary",
                 disabled=not can_save, use_container_width=True, key="seq_save_btn"):
        pname = st.session_state["new_product_name"].strip()
        if pname in df["Period"].astype(str).values:
            st.warning(f"⚠️ **{pname}** already exists — edit it in the table below.")
        else:
            values  = st.session_state["temp_monthly_data"]
            new_row = {"Period": pname}
            for i in range(TOTAL_MONTHS):
                new_row[str(i + 1)] = values[i] if i < len(values) else 0
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            if ExcelManager.save_raw_data(df):
                st.success(f"✅ **{pname}** saved to Excel!")
                st.session_state["new_product_name"]    = ""
                st.session_state["temp_monthly_data"]   = []
                st.session_state["current_month_value"] = 0
                df = ExcelManager.get_raw_data()
                st.rerun()
            else:
                st.error("❌ Save failed — check the Excel file is not open elsewhere.")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Inline Edit via st.data_editor  (on_change validation + save)
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("✏️ Edit Monthly Data")
st.caption("Double-click any cell to edit. Validated on every change.")

column_config: dict = {
    "Period": st.column_config.TextColumn("Product", width="medium", disabled=True),
}
for m in range(1, TOTAL_MONTHS + 1):
    column_config[str(m)] = st.column_config.NumberColumn(
        f"M{m}", min_value=0, step=1, format="%d", width="small",
    )

def _on_editor_change():
    edits: dict = st.session_state.get("raw_editor", {})
    for _idx, row_edits in edits.get("edited_rows", {}).items():
        for col, val in row_edits.items():
            if col == "Period" or val is None:
                continue
            try:
                int(float(str(val)))
            except (ValueError, TypeError):
                st.session_state["validation_error"] = (
                    f"Invalid value in Month {col}: `{val}` is not a number.")
                st.session_state["pending_save"] = False
                return
    for added in edits.get("added_rows", []):
        for col, val in added.items():
            if col == "Period" or val is None:
                continue
            try:
                int(float(str(val)))
            except (ValueError, TypeError):
                st.session_state["validation_error"] = (
                    f"Invalid value in Month {col}: `{val}` is not a number.")
                st.session_state["pending_save"] = False
                return
    st.session_state["validation_error"] = None
    st.session_state["pending_save"]     = True

if st.session_state["validation_error"]:
    st.error(f"🚫 {st.session_state['validation_error']}")
if st.session_state["pending_save"]:
    st.warning("⚠️ You have unsaved changes — press **Save Edits to Excel** below.", icon="💾")

edit_cols = ["Period"] + MONTH_COLS
edited_df: pd.DataFrame = st.data_editor(
    df[edit_cols].copy(),
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    height=420,
    key="raw_editor",
    on_change=_on_editor_change,
)

col_save, col_discard, _ = st.columns([2, 1, 4])
with col_save:
    if st.button(
        "💾 Save Edits to Excel", type="primary",
        disabled=not st.session_state["pending_save"], use_container_width=True,
    ):
        for col in MONTH_COLS:
            if col in edited_df.columns:
                edited_df[col] = (pd.to_numeric(edited_df[col], errors="coerce")
                                  .fillna(0).astype(int))
        if ExcelManager.save_raw_data(edited_df):
            st.session_state["pending_save"]     = False
            st.session_state["validation_error"] = None
            st.success("✅ Edits saved to Excel successfully!")
            st.rerun()
        else:
            st.error("❌ Save failed — close the Excel file if it's open elsewhere.")
with col_discard:
    if st.button(
        "↩️ Discard", type="primary",
        disabled=not st.session_state["pending_save"], use_container_width=True,
    ):
        ExcelManager.load_all(force=True)
        st.session_state["pending_save"]     = False
        st.session_state["validation_error"] = None
        st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – Delete Product
# (secondary button type is styled red via CSS at top of page)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🗑️ Delete Product", expanded=False):
    product_list = df["Period"].astype(str).tolist()
    selected_to_delete = st.selectbox(
        "Select product to delete", options=product_list, key="delete_selectbox"
    )

    st.session_state["confirm_delete"] = st.checkbox(
        f'I confirm I want to permanently delete **{selected_to_delete}** from the dataset.',
        value=st.session_state["confirm_delete"],
        key="confirm_delete_checkbox",
    )

    if st.button(
        "🗑️ Delete Selected Product",
        type="secondary",           # ← styled red via CSS injected at page top
        disabled=not st.session_state["confirm_delete"],
        use_container_width=False,
        key="delete_product_btn",
    ):
        df_updated = df[df["Period"].astype(str) != selected_to_delete].reset_index(drop=True)
        if ExcelManager.save_raw_data(df_updated):
            st.success(f"✅ **{selected_to_delete}** deleted and Excel updated.")
            st.session_state["confirm_delete"] = False
            df = ExcelManager.get_raw_data()
            st.rerun()
        else:
            st.error("❌ Delete failed — close the Excel file if it's open elsewhere.")

st.markdown("---")
st.caption("ABM Inventory Dashboard · Raw Data")
