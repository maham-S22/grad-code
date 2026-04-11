"""
pages/3_Price.py  –  Phase 2 (Prompt 2)
Price management: view, assign / update prices per product. Saves to 'Price' sheet.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from utils.style import apply_theme
from utils.data_loader import ExcelManager

st.set_page_config(page_title="Price – ABM Dashboard", page_icon="💰", layout="wide")
apply_theme()

ExcelManager.load_all()

st.title("💰 Price Management")
st.markdown("Assign or update the unit price for each product.")
st.markdown("---")

# ── Load data ─────────────────────────────────────────────────────────────────
raw_df = ExcelManager.get_raw_data()          # source of product names
price_df = ExcelManager.get("Price").copy()   # Product | Price columns

if raw_df.empty:
    st.error("Raw Data not found. Ensure `Grad Proj.xlsx` is in the project folder.")
    st.stop()

# Normalise Price sheet columns
if price_df.empty or "Product" not in price_df.columns:
    price_df = pd.DataFrame(columns=["Product", "Price"])
price_df["Price"] = pd.to_numeric(price_df["Price"], errors="coerce").fillna(0.0)

# All unique products from Raw Data (source of truth for product names)
all_products = raw_df["Period"].astype(str).tolist()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – Current Price Table (editable)
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("📊 Current Prices")

col_cfg = {
    "Product": st.column_config.TextColumn("Product", disabled=True, width="medium"),
    "Price":   st.column_config.NumberColumn(
        "Unit Price (₺)", min_value=0.0, step=0.01, format="%.2f", width="small"
    ),
}

# Merge so every Raw Data product appears (fill missing prices with 0)
merged_price = (
    pd.DataFrame({"Product": all_products})
    .merge(price_df[["Product", "Price"]], on="Product", how="left")
)
merged_price["Price"] = merged_price["Price"].fillna(0.0)

# on_change for inline price edits
def _on_price_change():
    st.session_state["price_pending_save"] = True

if "price_pending_save" not in st.session_state:
    st.session_state["price_pending_save"] = False

if st.session_state["price_pending_save"]:
    st.warning("⚠️ You have unsaved price changes — press **Save Prices** below.", icon="💾")

edited_price: pd.DataFrame = st.data_editor(
    merged_price,
    column_config=col_cfg,
    num_rows="fixed",            # products come from Raw Data; add via Add-Product form
    use_container_width=True,
    height=380,
    key="price_editor",
    on_change=_on_price_change,
)

col_save, col_discard, _ = st.columns([1, 1, 5])
with col_save:
    if st.button(
        "💾 Save Prices",
        type="primary",
        disabled=not st.session_state["price_pending_save"],
        use_container_width=True,
    ):
        edited_price["Price"] = (
            pd.to_numeric(edited_price["Price"], errors="coerce").fillna(0.0)
        )
        if ExcelManager.save("Price", edited_price[["Product", "Price"]]):
            st.session_state["price_pending_save"] = False
            st.success("✅ Prices saved!")
            st.rerun()
        else:
            st.error("Save failed — check that the Excel file is not open in another program.")

with col_discard:
    if st.button(
        "↩️ Discard",
        disabled=not st.session_state["price_pending_save"],
        use_container_width=True,
    ):
        ExcelManager.load_all(force=True)
        st.session_state["price_pending_save"] = False
        st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Quick Assign / Update single product price
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("✏️ Quick Price Update")

with st.form("quick_price_form", clear_on_submit=False):
    col_a, col_b = st.columns([3, 1])
    with col_a:
        selected = st.selectbox("Product", options=all_products)
    with col_b:
        # Pre-fill current price if exists
        cur_price = 0.0
        if selected:
            match = price_df[price_df["Product"].astype(str) == selected]
            cur_price = float(match["Price"].values[0]) if not match.empty else 0.0
        new_price = st.number_input(
            "Unit Price (₺)", min_value=0.0, value=cur_price, step=0.01, format="%.2f"
        )

    quick_save = st.form_submit_button("💾 Update Price", use_container_width=True)

if quick_save and selected:
    # Reload latest price df from session_state
    latest = ExcelManager.get("Price").copy()
    if "Product" not in latest.columns:
        latest = pd.DataFrame(columns=["Product", "Price"])
    latest["Price"] = pd.to_numeric(latest["Price"], errors="coerce").fillna(0.0)

    if selected in latest["Product"].astype(str).values:
        latest.loc[latest["Product"].astype(str) == selected, "Price"] = new_price
    else:
        latest = pd.concat(
            [latest, pd.DataFrame([{"Product": selected, "Price": new_price}])],
            ignore_index=True,
        )

    if ExcelManager.save("Price", latest):
        st.success(f"✅ Price for **{selected}** set to **₺{new_price:.2f}**")
        st.rerun()
    else:
        st.error("Save failed.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – Summary stats
# ═══════════════════════════════════════════════════════════════════════════════
st.subheader("📈 Price Summary")
price_vals = merged_price["Price"].replace(0, pd.NA).dropna()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Products with Price", f"{len(price_vals)}")
c2.metric("Avg Unit Price", f"₺{price_vals.mean():.2f}" if len(price_vals) else "—")
c3.metric("Min Price", f"₺{price_vals.min():.2f}" if len(price_vals) else "—")
c4.metric("Max Price", f"₺{price_vals.max():.2f}" if len(price_vals) else "—")

st.markdown("---")
st.caption("ABM Inventory Dashboard · Price Management")
