import streamlit as st
import sqlite3
import uuid
from datetime import datetime
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="SRNHS ECO POINTS", page_icon="♻️", layout="centered")

# Set ADMIN_PASSWORD in Streamlit Cloud > App settings > Secrets.
# The fallback is for initial testing only. Change it before using the app at school.
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "CHANGE-THIS-ADMIN-PASSWORD")

DB_NAME = "eco_points.db"
RATES = {"Plastic Bottles": 5, "Papers": 3}

SECTIONS = {
    "SEC-7-CLARK": "7-Clark",
    "SEC-7-CYBERNAUTS": "7-Cybernauts",
    "SEC-7-ARCHER": "7-Archer",
    "SEC-8-EUCLID": "8-Euclid",
    "SEC-8-PHYTAGORAS": "8-Phytagoras",
    "SEC-8-EULER": "8-Euler",
    "SEC-8-PHYTON": "8-Phyton",
    "SEC-9-AZURE": "9-Azure",
    "SEC-9-CHARLES": "9-Charles",
    "SEC-9-EINSTEIN": "9-Einstein",
    "SEC-10-AI": "10-Artificial Intelligence",
    "SEC-10-ALCALA": "10-Alcala",
    "SEC-10-ALCARAZ": "10-Alcaraz",
    "SEC-11-EARTH": "11-Earth",
    "SEC-11-MARS": "11-Mars",
    "SEC-11-JUPITER": "11-Jupiter",
    "SEC-12-SAPPHIRE": "12-Sapphire",
    "SEC-12-PEARL": "12-Pearl",
    "SEC-12-AMETYHST": "12-Ametyhst",
    "SEC-JH-FACULTY": "JH-Faculty",
    "SEC-SH-FACULTY": "SH-Faculty",
}

def db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def setup_database():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                section_id TEXT NOT NULL,
                section_name TEXT NOT NULL,
                category TEXT NOT NULL,
                material TEXT NOT NULL,
                quantity REAL NOT NULL,
                points INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

def decode_section(raw_value):
    if not raw_value:
        return None
    value = raw_value.strip()
    prefix = "ecopoints://section/"
    if value.startswith(prefix):
        section_id = value[len(prefix):].strip().upper()
        return section_id if section_id in SECTIONS else None
    # Also accept a plain section ID if QR format is changed later.
    section_id = value.upper()
    return section_id if section_id in SECTIONS else None

def save_transaction(tx):
    with db() as conn:
        conn.execute("""
            INSERT INTO transactions
            (transaction_id, section_id, section_name, category, material,
             quantity, points, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["id"], tx["section_id"], tx["section"], tx["category"],
            tx["material"], tx["quantity"], tx["points"],
            tx["created_at"], "Verified"
        ))

def get_history():
    with db() as conn:
        return conn.execute("""
            SELECT transaction_id, section_name, category, material,
                   quantity, points, created_at, status
            FROM transactions ORDER BY created_at DESC
        """).fetchall()

def reset_for_next_scan():
    for key in ["section_id", "section", "material", "quantity", "pending_tx"]:
        st.session_state.pop(key, None)
    st.session_state.page = "Scan QR"

setup_database()
if "page" not in st.session_state:
    st.session_state.page = "Scan QR"

st.title("♻️ SRNHS ECO POINTS")
st.caption("QR Code-Based Incentives System for Recyclables")

with st.sidebar:
    st.header("Navigation")
    if st.button("Scan Section QR", use_container_width=True):
        st.session_state.page = "Scan QR"
    if st.button("Admin Dashboard", use_container_width=True):
        st.session_state.page = "Admin"
    st.divider()
    st.caption("Plastic Bottles: 5 points/kg")
    st.caption("Papers: 3 points/kg")

if st.session_state.page == "Scan QR":
    st.header("Scan Section QR Code")
    st.write("Iharap ang official section QR code sa camera.")
    try:
        scanned_value = qrcode_scanner()
    except Exception as exc:
        scanned_value = None
        st.error("Hindi mabuksan ang QR scanner. Payagan ang camera access sa browser at i-refresh ang page.")
        st.caption(f"Scanner detail: {exc}")

    if scanned_value:
        section_id = decode_section(scanned_value)
        if section_id:
            st.session_state.section_id = section_id
            st.session_state.section = SECTIONS[section_id]
            st.session_state.page = "Welcome"
            st.rerun()
        else:
            st.error("Hindi kilala ang QR code na ito. Gamitin lamang ang official SRNHS section QR codes.")

    st.divider()
    st.subheader("Camera not working?")
    st.info("Subukan ang Chrome browser, i-check ang site camera permission, at tiyaking HTTPS ang app link.")

elif st.session_state.page == "Welcome":
    st.title(f"WELCOME, {st.session_state.section.upper()}!")
    st.write("Welcome to SRNHS ECO POINTS.")
    if st.button("Continue", type="primary", use_container_width=True):
        st.session_state.page = "Exchange Form"
        st.rerun()
    if st.button("Scan Another Section", use_container_width=True):
        reset_for_next_scan()
        st.rerun()

elif st.session_state.page == "Exchange Form":
    st.header("Exchange Form")
    st.write(f"**Section:** {st.session_state.section}")
    category = st.selectbox("Category", ["Recyclables"])
    material = st.selectbox("Material", ["Plastic Bottles", "Papers"])
    quantity = st.number_input("Quantity (kg)", min_value=0.1, step=0.1, format="%.1f")
    points = int(round(quantity * RATES[material]))
    st.metric("Estimated Eco Points", points)

    if st.button("Review Transaction", type="primary", use_container_width=True):
        st.session_state.material = material
        st.session_state.quantity = float(quantity)
        st.session_state.pending_tx = {
            "id": uuid.uuid4().hex[:12].upper(),
            "section_id": st.session_state.section_id,
            "section": st.session_state.section,
            "category": category,
            "material": material,
            "quantity": float(quantity),
            "points": points,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.page = "Review"
        st.rerun()

    if st.button("Cancel / Scan Another Section", use_container_width=True):
        reset_for_next_scan()
        st.rerun()

elif st.session_state.page == "Review":
    st.header("Review Transaction")
    tx = st.session_state.pending_tx
    st.write("Pakisuri kung tama ang mga detalye bago i-verify.")
    st.table({
        "Details": ["Section", "Category", "Material", "Quantity", "Points Earned"],
        "Information": [
            tx["section"], tx["category"], tx["material"],
            f'{tx["quantity"]:.1f} kg', str(tx["points"])
        ]
    })
    st.subheader("Verification of Transaction Code")
    password = st.text_input("Admin verification password", type="password")
    if st.button("Verified Transaction", type="primary", use_container_width=True):
        if password == ADMIN_PASSWORD and ADMIN_PASSWORD != "CHANGE-THIS-ADMIN-PASSWORD":
            save_transaction(tx)
            st.session_state.page = "Receipt"
            st.rerun()
        elif ADMIN_PASSWORD == "CHANGE-THIS-ADMIN-PASSWORD":
            st.error("I-set muna ng admin ang sariling password sa Streamlit Cloud Secrets.")
        else:
            st.error("Mali ang admin password. Hindi na-record ang transaction.")

    if st.button("Back to Edit Form", use_container_width=True):
        st.session_state.page = "Exchange Form"
        st.rerun()

elif st.session_state.page == "Receipt":
    st.header("Transaction Receipt")
    tx = st.session_state.pending_tx
    st.success("Transaction successfully verified and recorded!")
    st.write(f"**Transaction Code:** {tx['id']}")
    st.write(f"**Section:** {tx['section']}")
    st.write(f"**Category:** {tx['category']}")
    st.write(f"**Material:** {tx['material']}")
    st.write(f"**Quantity:** {tx['quantity']:.1f} kg")
    st.write(f"**Points Earned:** {tx['points']}")
    st.write("**Transaction Status:** Verified")
    st.divider()
    if st.button("Scan Next Section QR", type="primary", use_container_width=True):
        reset_for_next_scan()
        st.rerun()

elif st.session_state.page == "Admin":
    st.header("Admin Dashboard")
    admin_pw = st.text_input("Admin password to view records", type="password", key="dashboard_pw")
    if admin_pw == ADMIN_PASSWORD and ADMIN_PASSWORD != "CHANGE-THIS-ADMIN-PASSWORD":
        rows = get_history()
        st.subheader("Points per Section")
        totals = {name: 0 for name in SECTIONS.values()}
        for row in rows:
            totals[row[1]] = totals.get(row[1], 0) + row[5]
        st.dataframe(
            [{"Section": name, "Total Points": pts} for name, pts in totals.items()],
            use_container_width=True, hide_index=True
        )
        st.subheader("Transaction History")
        if rows:
            st.dataframe(
                [{
                    "Transaction Code": r[0], "Section": r[1], "Category": r[2],
                    "Material": r[3], "Quantity (kg)": r[4], "Points": r[5],
                    "Date": r[6], "Status": r[7]
                } for r in rows],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("Wala pang recorded transactions.")
    elif admin_pw:
        st.error("Mali ang password o hindi pa naka-set ang admin password.")

st.caption("Reminder: Streamlit Cloud local SQLite storage may reset when the app restarts. For permanent school records, connect a hosted database before actual deployment.")
