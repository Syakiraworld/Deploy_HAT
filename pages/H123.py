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

# Manual refresh
if st.sidebar.button("🔄 Update Data"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# =====================================================
# DATA SOURCE (GOOGLE SHEET)
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
SHEET_GID = "513906626"  # TRACKING ONLINE HOTLINE

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

# =====================================================
# LOAD DATA (CACHE + TTL)
# =====================================================
@st.cache_data(ttl=300)
def load_data():
    # 🔥 INI KUNCI: dtype=str supaya CUSTOMER NO gak jadi float
    df = pd.read_csv(CSV_URL, dtype=str)

    # rapihin header
    df.columns = df.columns.astype(str).str.strip()

    # normalisasi isi kolom penting
    for col in ["CUSTOMER NO", "ORDER STAR NO", "DONO"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(".0", "", regex=False)
            )

    return df


df = load_data()

# =====================================================
# FILTER BY ROLE
# =====================================================
if st.session_state.role == "ADMIN":

    st.sidebar.markdown("### 🔎 Pilih AHASS")

    if "CUSTOMER NO" in df.columns:
        ahass_list = sorted(df["CUSTOMER NO"].dropna().unique())

        selected_ahass = st.sidebar.selectbox(
            "AHASS",
            ["ALL AHASS"] + list(ahass_list)
        )

        if selected_ahass != "ALL AHASS":
            df = df[df["CUSTOMER NO"] == selected_ahass]

    else:
        st.sidebar.warning("⚠️ Kolom CUSTOMER NO tidak ditemukan di data.")

else:
    cust_no = str(st.session_state.customer_no).strip().replace(".0", "")

    if "CUSTOMER NO" in df.columns:
        df = df[df["CUSTOMER NO"] == cust_no]

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
    po_list = sorted(df["ORDER STAR NO"].dropna().unique())

    selected_po = st.selectbox(
        "Nomor PO (ORDER STAR NO)",
        ["ALL PO"] + list(po_list)
    )

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

# =====================================================
# INFO JUMLAH DATA
# =====================================================
st.caption(f"📌 Total data tampil: {len(df)} baris")
