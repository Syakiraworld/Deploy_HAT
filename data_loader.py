import pandas as pd
import streamlit as st

SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"

# ===============================
# LOAD USERS
# ===============================
@st.cache_data
def load_users():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet=USERS"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)
    return df


# ===============================
# LOAD TRANSACTION DATA
# ===============================
@st.cache_data
def load_transactions():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=513906626"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)
    df["ORDER STAR NO"] = df["ORDER STAR NO"].astype(str)
    df["ORDER NO"] = df["ORDER NO"].astype(str)

    return df
