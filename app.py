
import streamlit as st
import sqlite3
import cv2
import numpy as np
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="SRNHS ECO POINTS",
    page_icon="♻️",
    layout="centered"
)

SECTIONS = [
    "7-Clark", "7-Cybernauts", "7-Archer",
    "8-Euclid", "8-Phytagoras", "8-Euler", "8-Phyton",
    "9-Azure", "9-Charles", "9-Einstein",
    "10-Artificial Intelligence", "10-Alcala", "10-Alcaraz",
    "11-Earth", "11-Mars", "11-Jupiter",
    "12-Sapphire", "12-Pearl", "12-Ametyhst"
]

RATES = {
    "Plastic Bottles": 5,
    "Papers": 3
}

ADMIN_PASSWORD = "eco-demo-2026"
DB = "eco_points.db"

# DATABASE
def connect_db():
    return sqlite3.connect(DB)

def setup_database():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT,
                material TEXT,
                kilograms REAL,
                points INTEGER,
                date TEXT
            )
        """)

setup_database()

# SESSION
defaults = {
    "page": "welcome",
    "section": "",
    "material": "Plastic Bottles",
    "kg": 1.0,
    "pending": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def go(page):
    st.session_state.page = page
    st.rerun()

def make_qr(section):
    qr = qrcode.make(section)
    output = BytesIO()
    qr.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()

# HEADER
st.title("♻️ SRNHS ECO POINTS")
st.caption("QR Code-Based Incentives System for Recyclable Materials")
st.divider()

# WELCOME PAGE
if st.session_state.page == "welcome":

    st.title("WELCOME!")
    st.write("Welcome to SRNHS ECO POINTS.")
    st.write("Recycle today and earn Eco Points!")

    if st.button("SCAN SECTION QR", use_container_width=True):
        go("scan")

    if st.button("SECTION QR CODES", use_container_width=True):
        go("qr")

    if st.button("ADMIN DASHBOARD", use_container_width=True):
        go("admin_login")

# QR SCANNER
elif st.session_state.page == "scan":

    st.header("SCAN SECTION QR")
    st.write("Allow camera access and capture your section QR code.")

    photo = st.camera_input("Open Camera")

    if photo is not None:
        image_bytes = np.frombuffer(
            photo.getvalue(), np.uint8
        )

        image = cv2.imdecode(
            image_bytes, cv2.IMREAD_COLOR
        )

        detector = cv2.QRCodeDetector()
        qr_text, points, _ = detector.detectAndDecode(image)

        if qr_text:
            scanned = qr_text.strip()

            if scanned in SECTIONS:
                st.session_state.section = scanned
                st.success("QR CODE DETECTED!")
                st.success("WELCOME, " + scanned.upper() + "!")
                st.button(
                    "CONTINUE TO EXCHANGE",
                    on_click=lambda: go("exchange"),
                    use_container_width=True
                )
            else:
                st.error("Unknown section QR code.")

        else:
            st.warning("QR code not detected. Try again.")

    if st.button("BACK", use_container_width=True):
        go("welcome")

# EXCHANGE PAGE
elif st.session_state.page == "exchange":

    st.header("WELCOME, " + st.session_state.section.upper() + "!")

    st.subheader("EXCHANGE YOUR RECYCLABLES")

    st.write("Choose your recyclable material.")

    st.session_state.material = st.selectbox(
        "Material",
        ["Plastic Bottles", "Papers"]
    )

    st.session_state.kg = st.number_input(
        "Quantity (KG)",
        min_value=0.1,
        max_value=1000.0,
        value=1.0,
        step=0.1
    )

    points = round(
        st.session_state.kg *
        RATES[st.session_state.material]
    )

    st.metric("YOUR ECO POINTS", points)

    if st.button("CONTINUE TO RECEIPT",
                 use_container_width=True):
        st.session_state.pending = {
            "section": st.session_state.section,
            "material": st.session_state.material,
            "kg": st.session_state.kg,
            "points": points
        }
        go("receipt")

    if st.button("BACK TO QR", use_container_width=True):
        st.session_state.section = ""
        go("scan")

# RECEIPT PAGE
elif st.session_state.page == "receipt":

    st.header("TRANSACTION RECEIPT")

    data = st.session_state.pending

    if data is None:
        st.warning("No transaction found.")
        if st.button("BACK TO QR"):
            go("scan")
    else:
        st.write("Section:", data["section"])
        st.write("Material:", data["material"])
        st.write("Quantity:", data["kg"], "KG")
        st.write("Points:", data["points"])

        st.info("Please review your transaction.")

        if st.button("CONFIRM RECEIPT",
                     use_container_width=True):
            go("verify")

        if st.button("BACK TO EXCHANGE",
                     use_container_width=True):
            go("exchange")

# ADMIN VERIFICATION
elif st.session_state.page == "verify":

    st.header("ADMIN VERIFICATION")

    password = st.text_input(
        "Enter Admin Password",
        type="password"
    )

    if st.button("VERIFY AND RECORD",
                 use_container_width=True):

        if password == ADMIN_PASSWORD:

            data = st.session_state.pending

            with connect_db() as conn:
                conn.execute("""
                    INSERT INTO transactions
                    (section, material, kilograms, points, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data["section"],
                    data["material"],
                    data["kg"],
                    data["points"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            go("success")

        else:
            st.error("Incorrect admin password.")

    if st.button("BACK TO RECEIPT"):
        go("receipt")

# SUCCESS PAGE
elif st.session_state.page == "success":

    st.success("TRANSACTION SUCCESSFULLY RECORDED!")
    st.balloons()

    data = st.session_state.pending

    st.write("Section:", data["section"])
    st.write("Points Earned:", data["points"])

    if st.button("SCAN NEXT SECTION QR",
                 use_container_width=True):
        st.session_state.section = ""
        st.session_state.pending = None
        go("scan")

    if st.button("HOME", use_container_width=True):
        st.session_state.section = ""
        st.session_state.pending = None
        go("welcome")

# QR CODE GENERATOR
elif st.session_state.page == "qr":

    st.header("SECTION QR CODES")
    st.write("Each section has its own unique QR code.")

    selected = st.selectbox(
        "Choose Section",
        SECTIONS
    )

    qr_image = make_qr(selected)

    st.image(qr_image, width=250)

    st.download_button(
        "DOWNLOAD SECTION QR",
        data=qr_image,
        file_name=selected.replace(" ", "_") + "_QR.png",
        mime="image/png",
        use_container_width=True
    )

    if st.button("BACK TO HOME"):
        go("welcome")

# ADMIN LOGIN
elif st.session_state.page == "admin_login":

    st.header("ADMIN LOGIN")

    password = st.text_input(
        "Admin Password",
        type="password"
    )

    if st.button("LOGIN"):
        if password == ADMIN_PASSWORD:
            go("admin")
        else:
            st.error("Incorrect password.")

    if st.button("BACK"):
        go("welcome")

# ADMIN DASHBOARD
elif st.session_state.page == "admin":

    st.header("ADMIN DASHBOARD")

    with connect_db() as conn:
        rows = conn.execute("""
            SELECT section, material, kilograms, points, date
            FROM transactions
            ORDER BY id DESC
        """).fetchall()

    st.subheader("SECTION POINTS")

    for section in SECTIONS:
        total = sum(
            row[3] for row in rows
            if row[0] == section
        )
        st.write(section, "-", total, "points")

    st.divider()
    st.subheader("TRANSACTION HISTORY")

    if rows:
        for row in rows:
            st.write(
                f"{row[0]} | {row[1]} | "
                f"{row[2]} KG | {row[3]} points | {row[4]}"
            )
            st.divider()
    else:
        st.info("No transactions recorded yet.")

    if st.button("BACK TO HOME"):
        go("welcome")
