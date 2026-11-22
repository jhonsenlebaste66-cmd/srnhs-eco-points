
import streamlit as st
import cv2
import numpy as np

st.set_page_config(
    page_title="SRNHS ECO POINTS",
    page_icon="♻️",
    layout="centered"
)

SECTIONS = [
    "7-Clark",
    "7-Cybernauts",
    "7-Archer",
    "8-Euclid",
    "8-Phytagoras",
    "8-Euler",
    "8-Phyton",
    "9-Azure",
    "9-Charles",
    "9-Einstein",
    "10-Artificial Intelligence",
    "10-Alcala",
    "10-Alcaraz",
    "11-Earth",
    "11-Mars",
    "11-Jupiter",
    "12-Sapphire",
    "12-Pearl",
    "12-Ametyhst"
]

if "section" not in st.session_state:
    st.session_state.section = None

st.title("♻️ SRNHS ECO POINTS")
st.subheader("QR Code Camera Scanner")

st.write("Scan your section QR code to continue.")

camera = st.camera_input("Open Camera and Scan QR")

if camera is not None:
    image_bytes = np.frombuffer(
        camera.getvalue(), np.uint8
    )

    image = cv2.imdecode(
        image_bytes, cv2.IMREAD_COLOR
    )

    detector = cv2.QRCodeDetector()
    qr_text, points, _ = detector.detectAndDecode(image)

    if qr_text:
        scanned_section = qr_text.strip()

        if scanned_section in SECTIONS:
            st.session_state.section = scanned_section
            st.success("QR CODE SUCCESSFULLY SCANNED!")
        else:
            st.error("Unknown section QR code.")

    else:
        st.warning("QR code not detected. Try again.")

if st.session_state.section:
    st.success("WELCOME, " + st.session_state.section.upper() + "!")
    st.write("Your section has been recognized.")

    if st.button("SCAN ANOTHER SECTION"):
        st.session_state.section = None
        st.rerun()
