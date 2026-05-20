import os
import re
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

from bike_app.db import init_db, insert_report, search_by_serial, verify_token
from bike_app.email_utils import send_verification

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

init_db()

st.set_page_config(page_title="Stolen Bike Check", page_icon="🚲")

# Handle the email verification deep-link before rendering the rest of the UI.
params = st.query_params
if "verify" in params:
    token = params["verify"]
    ok = verify_token(token)
    if ok:
        st.success("Report verified. It will now appear in searches.")
    else:
        st.error("This verification link is invalid or has already been used.")
    if st.button("Back to homepage"):
        st.query_params.clear()
        st.rerun()
    st.stop()


st.title("🚲 Stolen Bike Check")
st.write(
    "Check whether a bike has been reported stolen before you buy it, "
    "or report your own bike as stolen so future buyers are warned."
)

check_tab, report_tab = st.tabs(["Check a bike", "Report stolen"])


with check_tab:
    st.subheader("Search by serial number")
    st.caption("Enter the bike's frame serial. Spaces and punctuation are ignored.")
    serial = st.text_input("Serial number", key="search_serial")
    if st.button("Check", type="primary", disabled=not serial.strip()):
        matches = search_by_serial(serial)
        if not matches:
            st.success(
                "No reports found for this serial. "
                "Note: this does not guarantee the bike isn't stolen — many thefts go unreported here."
            )
        else:
            st.error(f"This bike has been reported stolen ({len(matches)} report(s)).")
            for m in matches:
                with st.container(border=True):
                    cols = st.columns([1, 2])
                    with cols[0]:
                        if m.get("photo_path") and Path(m["photo_path"]).exists():
                            st.image(m["photo_path"])
                    with cols[1]:
                        st.markdown(f"**Serial:** `{m['serial']}`")
                        descr = " · ".join(
                            b for b in (m.get("brand"), m.get("model"), m.get("color")) if b
                        )
                        if descr:
                            st.markdown(f"**Bike:** {descr}")
                        if m.get("theft_date"):
                            st.markdown(f"**Stolen on:** {m['theft_date']}")
                        if m.get("theft_location"):
                            st.markdown(f"**Stolen in:** {m['theft_location']}")
                        st.markdown(f"**Reported:** {m['created_at']}")
            st.info(
                "Do not buy this bike. Contact your local police and, if you can, "
                "keep a record of the seller's details."
            )


with report_tab:
    st.subheader("Report a stolen bike")
    st.caption(
        "Reports are verified by email before appearing in searches. "
        "Your email is never shown publicly."
    )

    with st.form("report_form", clear_on_submit=False):
        r_serial = st.text_input("Serial number *")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            brand = st.text_input("Brand")
        with col_b:
            model = st.text_input("Model")
        with col_c:
            color = st.text_input("Color")
        col_d, col_e = st.columns(2)
        with col_d:
            theft_date = st.date_input(
                "Theft date", value=None, max_value=date.today(), format="YYYY-MM-DD"
            )
        with col_e:
            theft_location = st.text_input("Theft location (city, area)")
        owner_email = st.text_input(
            "Your email *",
            help="Used to verify the report and contact you if there's a match.",
        )
        photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button("Submit report", type="primary")

    if submitted:
        if not r_serial.strip() or not owner_email.strip():
            st.error("Serial number and email are required.")
        elif not EMAIL_RE.match(owner_email.strip()):
            st.error("That email doesn't look right.")
        else:
            photo_path = None
            if photo is not None:
                ext = Path(photo.name).suffix.lower() or ".jpg"
                dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
                dest.write_bytes(photo.getbuffer())
                photo_path = str(dest)

            token = uuid.uuid4().hex
            insert_report(
                serial=r_serial.strip(),
                brand=brand.strip() or None,
                model=model.strip() or None,
                color=color.strip() or None,
                theft_date=theft_date.isoformat() if theft_date else None,
                theft_location=theft_location.strip() or None,
                owner_email=owner_email.strip(),
                photo_path=photo_path,
                token=token,
            )
            result = send_verification(owner_email.strip(), token, BASE_URL)
            if result.startswith("dev:"):
                st.success(
                    "Report submitted. Email delivery is in dev mode — "
                    "click your verification link below:"
                )
                st.code(result[4:])
            elif result == "sent":
                st.success("Report submitted. Check your inbox for a verification link.")
            else:
                st.warning(
                    f"Report submitted, but the verification email failed to send ({result}). "
                    "Check server logs."
                )
