
import streamlit as st
import sqlite3
from datetime import datetime

# PAGE SETTINGS
st.set_page_config(
    page_title="SRNHS Eco Points",
    page_icon="🌱",
    layout="centered"
)

# DESIGN
st.markdown("""
<style>
.stApp {
    background-color: #9FB5A8;
}
h1, h2, h3 {
    color: #06452F;
    text-align: center;
}
.stButton button {
    background-color: #06452F;
    color: white;
    width: 100%;
    min-height: 50px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# DATABASE
def save_transaction(section, material, quantity, points):
    conn = sqlite3.connect("eco_points.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT,
            material TEXT,
            quantity REAL,
            points REAL,
            date TEXT
        )
    """)
    conn.execute("""
        INSERT INTO transactions
        (section, material, quantity, points, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        section, material, quantity, points,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# SESSION
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "section" not in st.session_state:
    st.session_state.section = ""

if "receipt" not in st.session_state:
    st.session_state.receipt = {}

# POINT RATES
rates = {
    "Plastic Bottles": 5,
    "Papers": 3
}

# WELCOME PAGE
if st.session_state.page == "welcome":

    st.title("SRNHS ECO POINTS")
    st.subheader("by: Group 1_A.I.")

    st.title("Welcome!")

    st.markdown("""
    <p style="text-align:center;">
    Utilization of EcoPoints: A QR Code Based
    Incentives System for Recyclable
    </p>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("Scan your section QR code to begin.")

    if st.button("CONTINUE"):
        st.session_state.page = "scan"
        st.rerun()

# QR PAGE
elif st.session_state.page == "scan":

    st.title("SCAN SECTION QR")

    st.write("Enter the text from your official section QR code.")

    section = st.text_input("Section QR Code")

    if st.button("CONTINUE"):

        if section.strip():
            st.session_state.section = section.strip()
            st.session_state.page = "exchange"
            st.rerun()
        else:
            st.warning("Please enter your section.")

    if st.button("BACK"):
        st.session_state.page = "welcome"
        st.rerun()

# EXCHANGE PAGE
elif st.session_state.page == "exchange":

    st.title("ECOPOINTS EXCHANGE")

    st.subheader("Welcome, " + st.session_state.section + "!")

    st.write("Bottles: 5 points/kg | Papers: 3 points/kg")

    material = st.selectbox(
        "Choose Material",
        ["Plastic Bottles", "Papers"]
    )

    quantity = st.number_input(
        "Quantity (kg)",
        min_value=0.0,
        step=0.5
    )

    points = quantity * rates[material]

    st.subheader("Converted EcoPoints:")
    st.title(f"{points:.1f}")

    if st.button("CONTINUE TO RECEIPT"):

        if quantity > 0:
            st.session_state.receipt = {
                "section": st.session_state.section,
                "material": material,
                "quantity": quantity,
                "points": points
            }
            st.session_state.page = "review"
            st.rerun()
        else:
            st.warning("Enter a valid quantity.")

    if st.button("BACK TO QR"):
        st.session_state.section = ""
        st.session_state.page = "scan"
        st.rerun()

# REVIEW RECEIPT
elif st.session_state.page == "review":

    st.title("REVIEW TRANSACTION RECEIPT")

    r = st.session_state.receipt

    st.subheader("SRNHS ECO POINTS")
    st.markdown("### TRANSACTION RECEIPT")

    st.write("**Section:**", r["section"])
    st.write("**Category:** EcoPoints")
    st.write("**Material:**", r["material"])
    st.write("**Quantity:**", r["quantity"], "kg")
    st.write("**Points Earned:**", r["points"])

    password = st.text_input(
        "Verification of transaction password",
        type="password"
    )

    if st.button("SUBMIT VERIFIED TRANSACTION"):

        if password == "eco-demo-2026":
            save_transaction(
                r["section"],
                r["material"],
                r["quantity"],
                r["points"]
            )
            st.session_state.page = "success"
            st.rerun()
        else:
            st.error("Incorrect transaction password.")

    if st.button("BACK TO EDIT FORM"):
        st.session_state.page = "exchange"
        st.rerun()

# SUCCESS PAGE
elif st.session_state.page == "success":

    r = st.session_state.receipt

    st.title("TRANSACTION RECORDED")

    st.success("Your transaction was verified successfully.")

    st.subheader("Total EcoPoints Earned:")
    st.title(f"{r['points']:.1f}")

    st.title("THANK YOU!")

    st.markdown("### SRNHS ECO POINTS TRANSACTION RECEIPT")

    st.write("**Section:**", r["section"])
    st.write("**Category:** EcoPoints")
    st.write("**Material:**", r["material"])
    st.write("**Quantity:**", r["quantity"], "kg")
    st.write("**Points Earned:**", r["points"])
    st.write("**Status:** VERIFIED / SAVED")

    if st.button("BACK TO OPTIONS"):
        st.session_state.page = "welcome"
        st.rerun()

    if st.button("SCAN NEXT SECTION QR"):
        st.session_state.section = ""
        st.session_state.page = "scan"
        st.rerun()
