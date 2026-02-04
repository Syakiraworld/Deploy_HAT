import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="HAT – Fitur 3", layout="wide")

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

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# =====================================================
# DATA SOURCE (GOOGLE SHEET)
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
DATABASE_SO_GID = "1063430792"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={DATABASE_SO_GID}"
)

# =====================================================
# DATA LOADER (CACHE + TTL)
# =====================================================
@st.cache_data(ttl=300)  # refresh otomatis tiap 5 menit
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)
    return df

# =====================================================
# MANUAL REFRESH (ADMIN / USER)
# =====================================================
if st.sidebar.button("🔄 Update Data"):
    st.cache_data.clear()
    st.rerun()

df = load_data()

# =====================================================
# FILTER BY ROLE
# =====================================================
if st.session_state.role == "ADMIN":
    st.sidebar.markdown("### 🔎 Pilih AHASS")
    ahass_list = sorted(df["CUSTOMER NO"].unique())

    selected_ahass = st.sidebar.selectbox(
        "AHASS",
        ["ALL AHASS"] + ahass_list
    )

    if selected_ahass != "ALL AHASS":
        df = df[df["CUSTOMER NO"] == selected_ahass]

else:
    cust_no = st.session_state.customer_no
    df = df[df["CUSTOMER NO"] == cust_no]
    st.sidebar.info(f"🔒 AHASS: {cust_no}")

# =====================================================
# HEADER
# =====================================================
st.title("📑 Fitur 3 – Database Sales Order")
st.caption(
    f"📅 Data terakhir ditarik: "
    f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
)

# =====================================================
# EXCLUDE COLUMN (E, F, K, W)
# =====================================================
exclude_index = [4, 5, 10, 22]  # E, F, K, W
final_cols = [
    col for i, col in enumerate(df.columns)
    if i not in exclude_index
]

# =====================================================
# TABLE
# =====================================================
st.subheader("📋 Hotline Tracking SO")
st.dataframe(df[final_cols], use_container_width=True)
