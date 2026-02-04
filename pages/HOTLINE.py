import streamlit as st
import pandas as pd

# =====================================================
# AUTH
# =====================================================
if "login" not in st.session_state or not st.session_state.login:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

if st.session_state.role != "ADMIN":
    st.error("⛔ Fitur ini hanya dapat diakses ADMIN")
    st.stop()

st.set_page_config(page_title="HAT – Admin Insight", layout="wide")

# =====================================================
# DATA SOURCE
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
SHEET_GID = "513906626"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)
    df["ORDER STAR NO"] = df["ORDER STAR NO"].astype(str)
    df["Order Qty"] = pd.to_numeric(df["Order Qty"], errors="coerce").fillna(0)
    return df

df = load_data()

# =====================================================
# HEADER
# =====================================================
st.title("📊 Fitur 2 – Admin Insight")

# =====================================================
# KPI
# =====================================================
k1, k2, k3 = st.columns(3)
k1.metric("Total AHASS", df["CUSTOMER NO"].nunique())
k2.metric("Total PO", df["ORDER STAR NO"].nunique())
k3.metric("Total Qty", int(df["Order Qty"].sum()))

# =====================================================
# TREND
# =====================================================
st.subheader("📈 Trend PO")

df["Month"] = pd.to_datetime(df["ORDER STAR DATE"], errors="coerce").dt.to_period("M").astype(str)
trend = df.groupby("Month")["ORDER STAR NO"].nunique()

st.line_chart(trend)
