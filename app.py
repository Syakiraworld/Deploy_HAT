import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="HAT Login",
    layout="centered"
)

# =====================================================
# SIDEBAR – CONTACT
# =====================================================
st.sidebar.markdown("### ☎️ Call Center")
st.sidebar.markdown(
    """
    📞 **Butuh bantuan?**  
    Hubungi Call Center HAT melalui WhatsApp:
    
    👉 [Chat WhatsApp](https://wa.me/6285369225697)
    
    📱 **0853-6922-5697**
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# =====================================================
# GOOGLE SHEET USERS CONFIG
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
USERS_GID = "372076464"

USERS_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={USERS_GID}"
)

# =====================================================
# LOAD USERS (SUPER SAFE)
# =====================================================
@st.cache_data
def load_users():
    df = pd.read_csv(USERS_URL, dtype=str)  # 🔒 paksa STRING sejak awal

    # normalisasi nama kolom
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # kolom wajib
    required_cols = [
        "username",
        "password",
        "role",
        "customer_no",
        "customer_name"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.error(f"Kolom '{col}' tidak ditemukan di sheet USERS")
            st.stop()

    # normalisasi isi data
    for col in ["username", "password", "role", "customer_no"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
        )

    # username case-insensitive
    df["username"] = df["username"].str.lower()

    return df

users_df = load_users()

# =====================================================
# LOGIN UI
# =====================================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("assets/logo.png", width=250)
    st.markdown("<h2 style='text-align:center;'>🔐 Login HAT</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;'>Hotline Activity Tracker</p>",
        unsafe_allow_html=True
    )

username = st.text_input("Username")
password = st.text_input("Password", type="password")

# =====================================================
# LOGIN LOGIC (ROLE BASED ROUTING)
# =====================================================
if st.button("Login"):
    input_username = username.strip().lower()
    input_password = password.strip()

    user = users_df[
        (users_df["username"] == input_username) &
        (users_df["password"] == input_password)
    ]

    if not user.empty:
        user = user.iloc[0]

        # ===============================
        # SESSION STATE
        # ===============================
        st.session_state.login = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.session_state.customer_no = user["customer_no"]
        st.session_state.customer_name = user["customer_name"]

        st.success("Login berhasil")

        # ===============================
        # ROUTING BY ROLE
        # ===============================
        if st.session_state.role == "ADMIN":
            st.switch_page("pages/HOTLINE.py")

        elif st.session_state.role == "AHASS":
            st.switch_page("pages/H123.py")

        elif st.session_state.role == "SO":
            st.switch_page("pages/SO.py")

        else:
            st.error("Role tidak dikenali")
            st.session_state.clear()

    else:
        st.error("Username atau password salah")
