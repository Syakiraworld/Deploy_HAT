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

# Sheet TRACKING (yang sudah kamu pakai)
SHEET_GID_TRACKING = "513906626"

# Sheet DATABASE & DATABASE SO (WAJIB ISI)
SHEET_GID_DATABASE = "513906626"
SHEET_GID_DATABASE_SO = "1063430792"

# URL CSV
CSV_URL_TRACKING = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID_TRACKING}"
)

CSV_URL_DATABASE = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID_DATABASE}"
)

CSV_URL_DATABASE_SO = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID_DATABASE_SO}"
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data(ttl=300)
def load_tracking():
    df = pd.read_csv(CSV_URL_TRACKING)
    df.columns = df.columns.str.strip()

    if "CUSTOMER NO" in df.columns:
        df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)

    if "ORDER STAR NO" in df.columns:
        df["ORDER STAR NO"] = df["ORDER STAR NO"].astype(str)

    if "Order Qty" in df.columns:
        df["Order Qty"] = pd.to_numeric(df["Order Qty"], errors="coerce").fillna(0)

    return df


@st.cache_data(ttl=300)
def load_sheet(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df


df = load_tracking()

# =====================================================
# HEADER
# =====================================================
st.title("📊 Fitur 2 – Admin Insight")

# =====================================================
# KPI
# =====================================================
k1, k2, k3 = st.columns(3)

k1.metric("Total AHASS", df["CUSTOMER NO"].nunique() if "CUSTOMER NO" in df.columns else 0)
k2.metric("Total PO", df["ORDER STAR NO"].nunique() if "ORDER STAR NO" in df.columns else 0)
k3.metric("Total Qty", int(df["Order Qty"].sum()) if "Order Qty" in df.columns else 0)

st.divider()

# =====================================================
# TREND PO (PER BULAN)
# =====================================================
st.subheader("📈 Trend PO (per bulan)")

if "ORDER STAR DATE" in df.columns and "ORDER STAR NO" in df.columns:
    df["Month"] = pd.to_datetime(df["ORDER STAR DATE"], errors="coerce").dt.to_period("M").astype(str)
    trend = df.groupby("Month")["ORDER STAR NO"].nunique().sort_index()
    st.line_chart(trend)
else:
    st.warning("⚠️ Kolom ORDER STAR DATE / ORDER STAR NO tidak ditemukan.")

st.divider()

# =====================================================
# CHART: TOTAL PO PER AHASS
# =====================================================
st.subheader("🏪 Total PO per AHASS")

if "CUSTOMER NO" in df.columns and "ORDER STAR NO" in df.columns:
    po_ahass = (
        df.groupby("CUSTOMER NO")["ORDER STAR NO"]
        .nunique()
        .sort_values(ascending=False)
    )

    top_ahass = st.slider("Tampilkan Top AHASS", 5, 50, 20)
    st.bar_chart(po_ahass.head(top_ahass))
else:
    st.warning("⚠️ Kolom CUSTOMER NO / ORDER STAR NO tidak ditemukan.")

st.divider()

# =====================================================
# TOP ITEM (DATABASE + DATABASE SO)
# M = ITEM
# N = DESKRIPSI (VLOOKUP)
# O = QTY
# =====================================================
st.subheader("📦 Item Paling Sering Dipesan (Total Qty)")

try:
    df_db = load_sheet(CSV_URL_DATABASE)
    df_so = load_sheet(CSV_URL_DATABASE_SO)

    def extract_item_data(dataframe):
        # Minimal harus sampai kolom O (15 kolom)
        if dataframe.shape[1] < 15:
            return pd.DataFrame(columns=["ITEM", "DESKRIPSI", "QTY"])

        col_item = dataframe.columns[12]  # M
        col_desc = dataframe.columns[13]  # N
        col_qty = dataframe.columns[14]   # O

        temp = dataframe[[col_item, col_desc, col_qty]].copy()
        temp.columns = ["ITEM", "DESKRIPSI", "QTY"]

        temp["ITEM"] = temp["ITEM"].astype(str).str.strip()
        temp["DESKRIPSI"] = temp["DESKRIPSI"].astype(str).str.strip()
        temp["QTY"] = pd.to_numeric(temp["QTY"], errors="coerce").fillna(0)

        # buang item kosong
        temp = temp[temp["ITEM"] != ""]
        return temp

    data_db = extract_item_data(df_db)
    data_so = extract_item_data(df_so)

    all_items = pd.concat([data_db, data_so], ignore_index=True)

    if all_items.empty:
        st.warning("⚠️ Data item kosong. Pastikan sheet DATABASE dan DATABASE SO sudah benar.")
    else:
        # VLOOKUP ITEM -> DESKRIPSI
        desc_map = (
            all_items[all_items["DESKRIPSI"] != ""]
            .drop_duplicates(subset=["ITEM"])
            .set_index("ITEM")["DESKRIPSI"]
            .to_dict()
        )

        # total qty per item
        summary = (
            all_items.groupby("ITEM", as_index=False)["QTY"]
            .sum()
            .sort_values("QTY", ascending=False)
        )

        summary["DESKRIPSI"] = summary["ITEM"].map(desc_map).fillna("-")

        top_item = st.slider("Tampilkan Top Item", 5, 50, 20)

        # chart
        chart_data = summary.head(top_item).set_index("ITEM")["QTY"]
        st.bar_chart(chart_data)

        # tabel
        st.dataframe(summary.head(top_item), use_container_width=True)

except Exception as e:
    st.error("❌ Gagal load data DATABASE / DATABASE SO")
    st.code(str(e))
    st.info("Pastikan GID sheet DATABASE dan DATABASE SO sudah benar.")
