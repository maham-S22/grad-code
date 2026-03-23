import streamlit as st
import os

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Grad Project Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load shared CSS ────────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar branding ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Grad Project")
    st.caption("Use the links above to navigate.")
    st.markdown("---")
    st.caption("© 2026")

# ── Home Page ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size: 2.8rem; color: #1a1a2e; margin-bottom: 0.3rem;">
        📦 Smart Inventory & Decision System
    </h1>
    <p style="font-size: 1.15rem; color: #555; max-width: 650px; margin: 0 auto;">
        An integrated platform for real-time inventory tracking, demand forecasting,
        and data-driven decision support — built as a graduation project.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Feature cards ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background:white; border-radius:14px; padding:1.8rem 1.5rem;
                box-shadow:0 4px 16px rgba(0,0,0,0.07); border-top:4px solid #6c63ff;
                height:100%;">
        <div style="font-size:2.2rem; margin-bottom:0.6rem;">🗃️</div>
        <h3 style="color:#1a1a2e; margin-bottom:0.5rem;">Inventory System</h3>
        <p style="color:#666; font-size:0.95rem; line-height:1.6;">
            Monitor stock levels, track product movements, and manage inventory
            data in real time with interactive tables and visual summaries.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:white; border-radius:14px; padding:1.8rem 1.5rem;
                box-shadow:0 4px 16px rgba(0,0,0,0.07); border-top:4px solid #00b894;
                height:100%;">
        <div style="font-size:2.2rem; margin-bottom:0.6rem;">📈</div>
        <h3 style="color:#1a1a2e; margin-bottom:0.5rem;">Forecasting</h3>
        <p style="color:#666; font-size:0.95rem; line-height:1.6;">
            Predict future demand using time-series models, helping plan restocking
            and reduce waste through accurate, model-driven projections.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background:white; border-radius:14px; padding:1.8rem 1.5rem;
                box-shadow:0 4px 16px rgba(0,0,0,0.07); border-top:4px solid #fdcb6e;
                height:100%;">
        <div style="font-size:2.2rem; margin-bottom:0.6rem;">🧠</div>
        <h3 style="color:#1a1a2e; margin-bottom:0.5rem;">Decision Support</h3>
        <p style="color:#666; font-size:0.95rem; line-height:1.6;">
            Get actionable insights and recommendations to support smarter
            purchasing, pricing, and operational decisions backed by data.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 **Select a page from the sidebar** to explore each module.")