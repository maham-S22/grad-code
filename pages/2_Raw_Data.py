"""
pages/2_Raw_Data.py  –  Phase 2 (Prompt 2 revision)
CRUD operations via st.data_editor with on_change validation + queued save.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from utils.style import apply_theme
from utils.data_loader import ExcelManager, TOTAL_MONTHS

st.set_page_config(page_title="Raw Data – ABM Dashboard", page_icon="📋", layout="wide")
apply_theme()

ExcelManager.load_all()

# ── Session-state keys ────────────────────────────────────────────────────────
if "pending_save" not in st.session_state:
    st.session_state["pending_save"] = False
if "validation_error" not in st.session_state:
    st.session_state["validation_error"] = None

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📋 Raw Data")
st.markdown("Source: **Raw Data** sheet · 447 products · Months 1–60")
st.markdown("---")

# ── Load working copy ─────────────────────────────────────────────────────────
df = ExcelManager.get_raw_data()

if df.empty:
    st.error("Could not load Raw Data. Ensure `Grad Proj.xlsx` is in the project folder.")
    st.stop()

MONTH_COLS = [str(i) for i in range(1, TOTAL_MONTHS + 1)]

# ── Session-state for sequential product entry ────────────────────────────────
if "new_product_name" not in st.session_state:
    st.session_state["new_product_name"] = ""
if "temp_monthly_data" not in st.session_state:
    st.session_state["temp_monthly_data"] = []
if "current_month_value" not in st.session_state:
    st.session_state["current_month_value"] = 0

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – Add New Product  (sequential month entry)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("➕ Add New Product", expanded=False):

    # ── Step 1: Product name ──────────────────────────────────────────────────
    st.session_state["new_product_name"] = st.text_input(
        "Product Name / Code",
        value=st.session_state["new_product_name"],
        placeholder="e.g. A 999 XX",
        key="product_name_input",
    )

    months_entered = len(st.session_state["temp_monthly_data"])
    next_month = months_entered + 1

    st.markdown("---")

    # ── Step 2: Sequential month entry ───────────────────────────────────────
    if next_month <= TOTAL_MONTHS:
        st.markdown(f"**📅 Enter value for Month {next_month}** of {TOTAL_MONTHS}")
        col_input, col_add, col_undo = st.columns([3, 1, 1])
        with col_input:
            month_val = st.number_input(
                f"Month {next_month} demand",
                min_value=0,
                value=st.session_state["current_month_value"],
                step=1,
                key=f"seq_month_input",
                label_visibility="collapsed",
            )
        with col_add:
            if st.button("➕ Add Month", use_container_width=True, type="primary"):
                st.session_state["temp_monthly_data"].append(int(month_val))
                st.session_state["current_month_value"] = 0
                st.rerun()
        with col_undo:
            if st.button(
                "↩️ Undo", use_container_width=True,
                disabled=months_entered == 0,
            ):
                st.session_state["temp_monthly_data"].pop()
                st.rerun()
    else:
        st.success(f"✅ All {TOTAL_MONTHS} months entered! Ready to save.")

    # ── Progress bar ──────────────────────────────────────────────────────────
    st.progress(months_entered / TOTAL_MONTHS, text=f"{months_entered} / {TOTAL_MONTHS} months filled")

    # ── Live preview ──────────────────────────────────────────────────────────
    if st.session_state["temp_monthly_data"]:
        st.markdown("**📊 Live Preview:**")
        preview = {
            f"M{i+1}": [v]
            for i, v in enumerate(st.session_state["temp_monthly_data"])
        }
        st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Save to Excel ─────────────────────────────────────────────────────────
    can_save = (
        bool(st.session_state["new_product_name"].strip())
        and months_entered > 0
    )
    if st.button(
        "💾 Save Changes to Excel",
        type="primary",
        disabled=not can_save,
        use_container_width=True,
        key="seq_save_btn",
    ):
        pname = st.session_state["new_product_name"].strip()
        if pname in df["Period"].astype(str).values:
            st.warning(f"⚠️ **{pname}** already exists — edit it in the table below.")
        else:
            # Build new row: pad missing months with 0
            values = st.session_state["temp_monthly_data"]
            new_row = {"Period": pname}
            for i in range(TOTAL_MONTHS):
                new_row[str(i + 1)] = values[i] if i < len(values) else 0
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            if ExcelManager.save_raw_data(df):
                st.success(f"✅ **{pname}** saved to Excel successfully!")
                # Reset state
                st.session_state["new_product_name"] = ""
                st.session_state["temp_monthly_data"] = []
                st.session_state["current_month_value"] = 0
                df = ExcelManager.get_raw_data()
                st.rerun()
            else:
                st.error("❌ Save failed — check the Excel file is not open elsewhere.")



# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Inline editable table  (on_change validation + queued save)
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("🗂️ Edit Monthly Data")
st.caption("Double-click any cell to edit. Changes are validated instantly.")

# ── Column config ─────────────────────────────────────────────────────────────
column_config: dict = {
    "Period": st.column_config.TextColumn("Product", width="medium", disabled=True),
}
for m in range(1, TOTAL_MONTHS + 1):
    column_config[str(m)] = st.column_config.NumberColumn(
        f"M{m}", min_value=0, step=1, format="%d", width="small"
    )

# ── on_change callback ────────────────────────────────────────────────────────
def _on_editor_change():
    """Validate edits and set pending_save flag."""
    edits: dict = st.session_state.get("raw_editor", {})
    
    # Validate edited_rows
    for _row_idx, row_edits in edits.get("edited_rows", {}).items():
        for col, val in row_edits.items():
            if col == "Period":
                continue
            if val is None:
                continue
            try:
                int(float(str(val)))
            except (ValueError, TypeError):
                st.session_state["validation_error"] = (
                    f"Invalid value in Month {col}: `{val}` is not a number."
                )
                st.session_state["pending_save"] = False
                return

    # Validate added_rows
    for added in edits.get("added_rows", []):
        for col, val in added.items():
            if col == "Period":
                continue
            if val is None:
                continue
            try:
                int(float(str(val)))
            except (ValueError, TypeError):
                st.session_state["validation_error"] = (
                    f"Invalid value in Month {col}: `{val}` is not a number."
                )
                st.session_state["pending_save"] = False
                return

    st.session_state["validation_error"] = None
    st.session_state["pending_save"] = True


# ── Validation error banner ───────────────────────────────────────────────────
if st.session_state["validation_error"]:
    st.error(f"🚫 {st.session_state['validation_error']}")

# ── Pending-save badge ────────────────────────────────────────────────────────
if st.session_state["pending_save"]:
    st.warning("⚠️ You have unsaved changes — press **Save Changes** below.", icon="💾")

# ── data_editor ───────────────────────────────────────────────────────────────
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

# ── Save button ───────────────────────────────────────────────────────────────
col_save, col_discard, _ = st.columns([1, 1, 5])
with col_save:
    if st.button(
        "💾 Save Changes",
        type="primary",
        disabled=not st.session_state["pending_save"],
        use_container_width=True,
    ):
        # Apply edited_df back, ensure numeric month columns
        for col in MONTH_COLS:
            if col in edited_df.columns:
                edited_df[col] = (
                    pd.to_numeric(edited_df[col], errors="coerce").fillna(0).astype(int)
                )
        if ExcelManager.save_raw_data(edited_df):
            st.session_state["pending_save"] = False
            st.session_state["validation_error"] = None
            st.success("✅ Saved successfully!")
            st.rerun()
        else:
            st.error("Save failed — check that the Excel file is not open in another program.")

with col_discard:
    if st.button(
        "↩️ Discard",
        disabled=not st.session_state["pending_save"],
        use_container_width=True,
    ):
        ExcelManager.load_all(force=True)   # reload from disk
        st.session_state["pending_save"] = False
        st.session_state["validation_error"] = None
        st.rerun()

st.markdown("---")
st.caption("ABM Inventory Dashboard · Raw Data")
