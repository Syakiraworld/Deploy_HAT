import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="HAT – Tracking", layout="wide")

# =====================================================
# AUTH
# =====================================================
if "login" not in st.session_state or not st.session_state.login:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

# =====================================================
# PATH (AMAN UNTUK DEPLOY)
# =====================================================
BASE_DIR = Path(__file__).parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

# =====================================================
# SIDEBAR
# =====================================================
if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

st.sidebar.markdown("### 📊 Navigasi")

# Tombol manual refresh data
if st.sidebar.button("🔄 Update Data"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# =====================================================
# DATA SOURCE
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
SHEET_GID = "513906626"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

# =====================================================
# LOAD DATA (CACHE + TTL)
# =====================================================
@st.cache_data(ttl=300)  # update otomatis maksimal tiap 5 menit
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()

    # ubah kolom penting jadi string supaya aman
    if "CUSTOMER NO" in df.columns:
        df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)

    if "ORDER STAR NO" in df.columns:
        df["ORDER STAR NO"] = df["ORDER STAR NO"].astype(str)

    if "DONO" in df.columns:
        df["DONO"] = df["DONO"].astype(str)

    return df


df = load_data()

# =====================================================
# FILTER BY ROLE
# =====================================================
if st.session_state.role == "ADMIN":
    st.sidebar.markdown("### 🔎 Pilih AHASS")

    if "CUSTOMER NO" in df.columns:
        ahass_list = sorted(df["CUSTOMER NO"].unique())

        selected_ahass = st.sidebar.selectbox(
            "AHASS", ["ALL AHASS"] + ahass_list
        )

        if selected_ahass != "ALL AHASS":
            df = df[df["CUSTOMER NO"] == selected_ahass]
    else:
        st.sidebar.warning("⚠️ Kolom CUSTOMER NO tidak ditemukan di data.")

else:
    cust_no = st.session_state.customer_no

    if "CUSTOMER NO" in df.columns:
        df = df[df["CUSTOMER NO"] == str(cust_no)]

    st.sidebar.info(f"🔒 AHASS: {cust_no}")

# =====================================================
# HEADER
# =====================================================
st.title("📦 Fitur 1 – Tracking Online Hotline")
st.caption(
    f"📅 Data terakhir ditarik: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
)

# =====================================================
# FILTER PO (ORDER STAR NO)
# =====================================================
if "ORDER STAR NO" in df.columns:
    po_list = sorted(df["ORDER STAR NO"].unique())
    selected_po = st.selectbox("Nomor PO (ORDER STAR NO)", ["ALL PO"] + po_list)

    if selected_po != "ALL PO":
        df = df[df["ORDER STAR NO"] == selected_po]
else:
    st.warning("⚠️ Kolom ORDER STAR NO tidak ditemukan, filter PO tidak aktif.")

# =====================================================
# TABLE
# =====================================================
st.subheader("📋 Tabel Tracking")

exclude = ["PO dan ETD"]  # kalau mau disembunyikan
final_cols = [c for c in df.columns if c not in exclude]

st.dataframe(df[final_cols], use_container_width=True)
