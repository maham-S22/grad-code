import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_data, save_data

# ── Page config & CSS ──────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "..", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📋 Raw Data")
st.markdown("Manage inventory data — add products, edit values, and save directly to Excel.")
st.markdown("---")

# ── Helper: detect month columns ──────────────────────────────────────────
def get_month_cols(df: pd.DataFrame) -> list:
    """Return all non-Product columns (treated as monthly period columns)."""
    return [c for c in df.columns if c != "Product"]

# ── Load data (always fresh after a save) ─────────────────────────────────
df = load_data().copy()
month_cols = get_month_cols(df)
N_MONTHS = 60  # maximum months supported for new products


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Display All Data
# ══════════════════════════════════════════════════════════════════════════
with st.expander("📊 View All Data", expanded=True):
    st.markdown(f"**{len(df):,} products** × **{df.shape[1]} columns**")

    # Search / filter
    search = st.text_input("🔍 Search by product name", placeholder="e.g. A 001")
    display_df = df[df["Product"].astype(str).str.contains(search, case=False, na=False)] if search else df

    # Column selector
    all_cols = df.columns.tolist()
    selected_cols = st.multiselect("Filter columns to display", options=all_cols, default=all_cols)

    st.dataframe(display_df[selected_cols], use_container_width=True, height=400)

    # Download
    csv = display_df[selected_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, "inventory_data.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Add New Product
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("➕ Add New Product")

with st.form("add_product_form", clear_on_submit=True):
    new_name = st.text_input("Product Name / Code *", placeholder="e.g. A 999 XY")

    st.markdown("**Monthly Values** (enter values for each month you have data for)")

    # How many months does the user want to fill in?
    n_months_input = st.slider(
        "Number of months to fill in", min_value=1, max_value=N_MONTHS, value=len(month_cols)
    )

    # Generate month input fields in 6-column rows
    monthly_values: dict = {}
    cols_per_row = 6
    month_keys = list(range(1, n_months_input + 1))

    for row_start in range(0, len(month_keys), cols_per_row):
        row_keys = month_keys[row_start : row_start + cols_per_row]
        row_cols = st.columns(len(row_keys))
        for col_widget, month_num in zip(row_cols, row_keys):
            with col_widget:
                val = st.number_input(
                    f"M{month_num}", min_value=0, value=0, step=1, key=f"add_m{month_num}"
                )
                monthly_values[month_num] = val

    submitted = st.form_submit_button("✅ Add Product", use_container_width=True)

    if submitted:
        if not new_name.strip():
            st.error("⚠️ Product name cannot be empty.")
        elif new_name.strip() in df["Product"].astype(str).values:
            st.error(f"⚠️ Product **{new_name}** already exists. Use the Edit section below.")
        else:
            # Build new row — align to existing columns, fill missing months with 0
            new_row: dict = {"Product": new_name.strip()}
            for col in month_cols:
                # col may be int or string — look up by position number
                try:
                    col_num = int(col)
                except (ValueError, TypeError):
                    col_num = None
                new_row[col] = monthly_values.get(col_num, 0)

            # If user entered months beyond existing columns, expand the DataFrame
            for month_num, val in monthly_values.items():
                if month_num not in [int(c) for c in month_cols if str(c).isdigit()]:
                    new_row[month_num] = val

            new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(new_df)
            st.success(f"✅ Product **{new_name}** added successfully! Page will refresh.")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Edit / Update Existing Product
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("✏️ Edit Existing Product")

product_list = df["Product"].astype(str).tolist()
selected_product = st.selectbox("Select a product to edit", options=["— select —"] + product_list)

if selected_product != "— select —":
    row_idx = df[df["Product"].astype(str) == selected_product].index[0]
    row_data = df.loc[row_idx]

    st.markdown(f"**Editing:** `{selected_product}`")

    with st.form("edit_product_form"):
        st.markdown("**Monthly Values**")

        edited_values: dict = {}
        edit_month_cols = month_cols
        cols_per_row = 6

        for row_start in range(0, len(edit_month_cols), cols_per_row):
            row_keys = edit_month_cols[row_start : row_start + cols_per_row]
            row_cols = st.columns(len(row_keys))
            for col_widget, month_col in zip(row_cols, row_keys):
                with col_widget:
                    current_val = int(row_data[month_col]) if pd.notna(row_data[month_col]) else 0
                    edited_val = st.number_input(
                        f"M{month_col}", min_value=0, value=current_val, step=1,
                        key=f"edit_{month_col}"
                    )
                    edited_values[month_col] = edited_val

        col_save, col_delete = st.columns([3, 1])
        with col_save:
            save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col_delete:
            delete_product = st.form_submit_button(
                "🗑️ Delete Product", use_container_width=True, type="secondary"
            )

        if save_edit:
            for month_col, val in edited_values.items():
                df.at[row_idx, month_col] = val
            save_data(df)
            st.success(f"✅ **{selected_product}** updated successfully!")
            st.rerun()

        if delete_product:
            df = df.drop(index=row_idx).reset_index(drop=True)
            save_data(df)
            st.warning(f"🗑️ **{selected_product}** has been deleted.")
            st.rerun()
