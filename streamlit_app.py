import os
import re
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

from bike_app.db import (
    init_db,
    insert_report,
    mark_recovered,
    search_by_serial,
    verified_report_count,
    verify_token,
)
from bike_app.email_utils import send_verification
from bike_app.seed import DEMO_BIKES, seed_if_empty

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")
DEMO_MODE = os.getenv("DEMO_MODE", "1") != "0"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

init_db()
if DEMO_MODE:
    seed_if_empty()

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
    "Before you buy a used bike, check whether it's been reported stolen. "
    "Owners can also file reports here so future buyers are warned."
)

n_reports = verified_report_count()
st.caption(f"📋 {n_reports} verified stolen-bike report(s) in the database.")

with st.expander("How it works"):
    st.markdown(
        "1. **Check a bike** — enter the frame serial. We match against verified "
        "stolen reports (spaces and punctuation are ignored).\n"
        "2. **Report stolen** — submit your serial, description, and contact email. "
        "We send you a verification link; once you click it, your report appears "
        "in searches.\n"
        "3. **Mark recovered** — if your bike comes back, take your report down so "
        "no one sees a false warning."
    )

check_tab, report_tab, recovered_tab = st.tabs(
    ["Check a bike", "Report stolen", "Mark recovered"]
)


with check_tab:
    st.subheader("Search by serial number")
    st.caption("Enter the bike's frame serial. Spaces and punctuation are ignored.")
    serial = st.text_input("Serial number", key="search_serial")
    if DEMO_MODE and DEMO_BIKES:
        examples = ", ".join(f"`{b['serial']}`" for b in DEMO_BIKES[:2])
        st.caption(f"Try a demo serial: {examples}")
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
                        else:
                            st.caption("(no photo)")
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
        r_serial = st.text_input("Serial number *", key="rep_serial")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            brand = st.text_input("Brand", key="rep_brand")
        with col_b:
            model = st.text_input("Model", key="rep_model")
        with col_c:
            color = st.text_input("Color", key="rep_color")
        col_d, col_e = st.columns(2)
        with col_d:
            theft_date = st.date_input(
                "Theft date", value=None, max_value=date.today(),
                format="YYYY-MM-DD", key="rep_date",
            )
        with col_e:
            theft_location = st.text_input(
                "Theft location (city, area)", key="rep_location"
            )
        owner_email = st.text_input(
            "Your email *", key="rep_email",
            help="Used to verify the report and contact you if there's a match.",
        )
        photo = st.file_uploader(
            "Photo", type=["jpg", "jpeg", "png", "webp"], key="rep_photo"
        )
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


with recovered_tab:
    st.subheader("Mark a bike as recovered")
    st.caption(
        "Got your bike back? Take down your report so future searches don't show "
        "a stolen warning. We match on the serial and the email you used to report it."
    )
    with st.form("recovered_form", clear_on_submit=False):
        rec_serial = st.text_input("Serial number *", key="rec_serial")
        rec_email = st.text_input("Email used in the original report *", key="rec_email")
        rec_submit = st.form_submit_button("Mark recovered", type="primary")

    if rec_submit:
        if not rec_serial.strip() or not rec_email.strip():
            st.error("Serial number and email are required.")
        elif mark_recovered(rec_serial.strip(), rec_email.strip()):
            st.success("Marked as recovered. The report no longer appears in searches.")
        else:
            st.error(
                "Couldn't find a verified report matching that serial and email. "
                "Double-check both, or contact us if your bike is still listed."
            )


st.divider()
st.caption(
    "Prototype only — reports here are user-submitted and not a substitute for a "
    "police report or an official registry."
)
