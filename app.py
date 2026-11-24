
import streamlit as st
import sqlite3
import uuid
from datetime import datetime
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(
    page_title="SRNHS ECO POINTS",
    page_icon="♻️",
    layout="centered"
)

# GREEN AND WHITE THEME
st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF;
    color: #14532D;
}
h1, h2, h3 {
    color: #168447 !important;
}
.stButton > button {
    background-color: #168447;
    color: white;
    border: 1px solid #168447;
    border-radius: 10px;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #116B38;
    color: white;
    border-color: #116B38;
}
section[data-testid="stSidebar"] {
    background-color: #F0FFF4;
}
</style>
""", unsafe_allow_html=True)

# ADMIN PASSWORD: Set in Streamlit Cloud Secrets
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

DB_NAME = "eco_points.db"

RATES = {
    "Plastic Bottles": 5,
    "Papers": 3
}

# OFFICIAL 21 SECTION QR IDENTIFIERS
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
    "SEC-SH-FACULTY": "SH-Faculty"
}

def connect_db():
    return sqlite3.connect(DB_NAME)

def setup_database():
    with connect_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            section_id TEXT,
            section_name TEXT,
            category TEXT,
            material TEXT,
            quantity REAL,
            points INTEGER,
            created_at TEXT,
            status TEXT
        )
        """)

def decode_section(value):
    if not value:
        return None

    value = value.strip()
    prefix = "ecopoints://section/"

    if value.startswith(prefix):
        section_id = value[len(prefix):].upper()
        if section_id in SECTIONS:
            return section_id

    return None

def save_transaction(tx):
    with connect_db() as conn:
        conn.execute("""
        INSERT INTO transactions
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["id"],
            tx["section_id"],
            tx["section"],
            tx["category"],
            tx["material"],
            tx["quantity"],
            tx["points"],
            tx["date"],
            "Verified"
        ))

def clear_transaction():
    for key in [
        "section_id", "section",
        "pending_tx", "material", "quantity"
    ]:
        st.session_state.pop(key, None)

    st.session_state.page = "Scanner"

setup_database()

if "page" not in st.session_state:
    st.session_state.page = "Scanner"

# SIDEBAR
with st.sidebar:
    st.title("ECO POINTS")
    st.write("Navigation")

    if st.button("QR Scanner", use_container_width=True):
        st.session_state.page = "Scanner"
        st.rerun()

    if st.button("Admin Dashboard", use_container_width=True):
        st.session_state.page = "Admin"
        st.rerun()

    st.divider()
    st.write("Plastic Bottles: 5 points/kg")
    st.write("Papers: 3 points/kg")

st.title("♻️ SRNHS ECO POINTS")
st.caption("QR Code-Based Incentives System for Recyclables")

# QR SCANNER
if st.session_state.page == "Scanner":

    st.header("Scan Section QR Code")
    st.write("Position the official section QR code in front of your camera.")

    try:
        scanned_value = qrcode_scanner()
    except Exception:
        scanned_value = None
        st.error(
            "The QR scanner could not be opened. "
            "Please allow camera access and refresh the page."
        )

    if scanned_value:
        section_id = decode_section(scanned_value)

        if section_id:
            st.session_state.section_id = section_id
            st.session_state.section = SECTIONS[section_id]
            st.session_state.page = "Welcome"
            st.rerun()
        else:
            st.error(
                "This QR code is not recognized. "
                "Please use an official SRNHS section QR code."
            )

    st.divider()
    st.subheader("Camera Not Working?")
    st.info(
        "Use Chrome, allow camera permission, "
        "and make sure the app uses HTTPS."
    )

# WELCOME PAGE
elif st.session_state.page == "Welcome":

    st.title(
        f"WELCOME, {st.session_state.section.upper()}!"
    )

    st.write("Welcome to the SRNHS ECO POINTS Recycling System.")

    if st.button("Continue", type="primary", use_container_width=True):
        st.session_state.page = "Exchange"
        st.rerun()

    if st.button("Scan Another Section", use_container_width=True):
        clear_transaction()
        st.rerun()

# EXCHANGE FORM
elif st.session_state.page == "Exchange":

    st.header("Exchange Form")
    st.write(f"Section: **{st.session_state.section}**")

    category = st.selectbox(
        "Category",
        ["Recyclables"]
    )

    material = st.selectbox(
        "Select Material",
        ["Plastic Bottles", "Papers"]
    )

    quantity = st.number_input(
        "Quantity (kg)",
        min_value=0.1,
        step=0.1,
        format="%.1f"
    )

    points = int(round(quantity * RATES[material]))

    st.metric("Estimated Eco Points", points)

    if st.button("Review Transaction", type="primary", use_container_width=True):

        st.session_state.pending_tx = {
            "id": uuid.uuid4().hex[:12].upper(),
            "section_id": st.session_state.section_id,
            "section": st.session_state.section,
            "category": category,
            "material": material,
            "quantity": float(quantity),
            "points": points,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.page = "Review"
        st.rerun()

    if st.button("Cancel Transaction", use_container_width=True):
        clear_transaction()
        st.rerun()

# REVIEW AND VERIFICATION
elif st.session_state.page == "Review":

    st.header("Review Transaction")

    tx = st.session_state.pending_tx

    st.write("Please review all transaction details.")

    st.table({
        "Details": [
            "Section",
            "Category",
            "Material",
            "Quantity",
            "Points Earned"
        ],
        "Information": [
            tx["section"],
            tx["category"],
            tx["material"],
            f'{tx["quantity"]:.1f} kg',
            tx["points"]
        ]
    })

    st.subheader("Verification of Transaction Code")

    password = st.text_input(
        "Admin Verification Password",
        type="password"
    )

    if st.button(
        "Verified Transaction",
        type="primary",
        use_container_width=True
    ):

        if not ADMIN_PASSWORD:
            st.error("The administrator password is not configured.")

        elif password == ADMIN_PASSWORD:

            try:
                save_transaction(tx)
                st.session_state.page = "Receipt"
                st.rerun()

            except sqlite3.IntegrityError:
                st.error("This transaction has already been recorded.")

            except Exception:
                st.error("Unable to save transaction. Please try again.")

        else:
            st.error(
                "Incorrect administrator password. "
                "The transaction was not recorded."
            )

    if st.button("Back to Edit Form", use_container_width=True):
        st.session_state.page = "Exchange"
        st.rerun()

# RECEIPT
elif st.session_state.page == "Receipt":

    st.header("Transaction Receipt")

    tx = st.session_state.pending_tx

    st.success("Transaction Successfully Verified!")

    st.write(f"**Transaction Code:** {tx['id']}")
    st.write(f"**Section:** {tx['section']}")
    st.write(f"**Category:** {tx['category']}")
    st.write(f"**Material:** {tx['material']}")
    st.write(f"**Quantity:** {tx['quantity']:.1f} kg")
    st.write(f"**Points Earned:** {tx['points']}")
    st.write("**Transaction Status:** Verified")

    st.divider()

    if st.button(
        "Scan Next Section QR",
        type="primary",
        use_container_width=True
    ):
        clear_transaction()
        st.rerun()

# ADMIN DASHBOARD
elif st.session_state.page == "Admin":

    st.header("Admin Dashboard")

    admin_password = st.text_input(
        "Enter Admin Password",
        type="password",
        key="dashboard_password"
    )

    if admin_password and admin_password == ADMIN_PASSWORD:

        with connect_db() as conn:
            rows = conn.execute("""
            SELECT transaction_id, section_name, category,
                   material, quantity, points, created_at, status
            FROM transactions
            ORDER BY created_at DESC
            """).fetchall()

        st.subheader("Points Per Section")

        totals = {
            name: 0 for name in SECTIONS.values()
        }

        for row in rows:
            totals[row[1]] += row[5]

        st.dataframe(
            [
                {"Section": name, "Total Points": points}
                for name, points in totals.items()
            ],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Transaction History")

        if rows:
            st.dataframe(
                [
                    {
                        "Transaction Code": r[0],
                        "Section": r[1],
                        "Category": r[2],
                        "Material": r[3],
                        "Quantity (kg)": r[4],
                        "Points": r[5],
                        "Date": r[6],
                        "Status": r[7]
                    }
                    for r in rows
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No transactions recorded yet.")

    elif admin_password:
        st.error("Incorrect administrator password.")

st.divider()
st.caption("SRNHS ECO POINTS | Recycle Today, Earn Tomorrow!")
st.caption(
    "Important: Streamlit Cloud local database storage may reset. "
    "Use a persistent hosted database for permanent school records."
)
