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

st.set_page_config(
    page_title="Bike Check.",
    page_icon="🚲",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ──────────────────────────────────────────────────────────────────────
# Look and feel
# ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      :root {
        --ink: #1d1d1f;
        --ink-soft: #6e6e73;
        --ink-faint: #86868b;
        --line: #d2d2d7;
        --bg: #ffffff;
        --bg-soft: #f5f5f7;
        --blue: #0071e3;
        --red: #d70015;
        --green: #248a3d;
      }

      html, body, [class*="st-"], [class*="css-"], button, input, textarea {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
          "SF Pro Text", "Helvetica Neue", "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
      }

      /* Hide Streamlit chrome */
      #MainMenu, footer { visibility: hidden; }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stToolbar"] { right: 0.5rem; }

      /* Tighter, narrower main column */
      .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 760px;
      }

      /* Hero */
      .hero { text-align: center; padding: 2rem 0 1.25rem; }
      .hero h1 {
        font-size: clamp(3rem, 7vw, 4.25rem);
        font-weight: 700;
        letter-spacing: -0.04em;
        color: var(--ink);
        margin: 0 0 0.5rem;
        line-height: 1.05;
      }
      .hero p {
        font-size: clamp(1.1rem, 2.2vw, 1.4rem);
        color: var(--ink-soft);
        font-weight: 400;
        margin: 0;
        letter-spacing: -0.01em;
      }
      .stats {
        text-align: center;
        color: var(--ink-faint);
        font-size: 0.95rem;
        margin: 0.75rem 0 2.25rem;
      }

      /* Section headers (subheaders inside tabs) */
      h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
        color: var(--ink) !important;
      }

      /* Tabs — centered, larger, no harsh underline */
      [data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 2.5rem;
        border-bottom: 1px solid var(--line) !important;
      }
      [data-baseweb="tab"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.75rem 0.25rem !important;
      }
      [data-baseweb="tab"][aria-selected="true"] {
        color: var(--ink) !important;
      }
      [data-baseweb="tab-highlight"] { background: var(--blue) !important; }

      /* Inputs — rounded, subtle */
      .stTextInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid var(--line) !important;
        background: var(--bg) !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
      }
      .stTextInput input:focus, .stDateInput input:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15) !important;
      }

      /* Buttons — pill, blue, prominent */
      .stButton button, .stFormSubmitButton button {
        border-radius: 980px !important;
        padding: 0.6rem 1.75rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        border: none !important;
        transition: filter 0.15s ease, transform 0.05s ease;
      }
      .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
        background: var(--blue) !important;
        color: white !important;
      }
      .stButton button[kind="primary"]:hover,
      .stFormSubmitButton button[kind="primary"]:hover { filter: brightness(1.05); }
      .stButton button:disabled { opacity: 0.4 !important; }

      /* Cards / containers with border */
      [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border-color: var(--line) !important;
        background: var(--bg) !important;
        padding: 1.25rem !important;
      }

      /* Alerts — soften them */
      [data-testid="stAlert"] {
        border-radius: 14px !important;
        border: 1px solid var(--line) !important;
        padding: 1rem 1.25rem !important;
      }

      /* Expander */
      [data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid var(--line) !important;
      }

      /* Captions */
      [data-testid="stCaptionContainer"], .stCaption { color: var(--ink-faint) !important; }

      /* File uploader */
      [data-testid="stFileUploaderDropzone"] {
        border-radius: 14px !important;
        border: 1px dashed var(--line) !important;
        background: var(--bg-soft) !important;
      }

      /* Footer disclaimer */
      .disclaimer {
        text-align: center;
        font-size: 0.85rem;
        color: var(--ink-faint);
        margin-top: 3rem;
        line-height: 1.5;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────
# Email verification deep-link
# ──────────────────────────────────────────────────────────────────────
params = st.query_params
if "verify" in params:
    token = params["verify"]
    ok = verify_token(token)
    st.markdown(
        '<div class="hero"><h1>Bike Check.</h1></div>',
        unsafe_allow_html=True,
    )
    if ok:
        st.success("Report verified. It will now appear in searches.")
    else:
        st.error("This verification link is invalid or has already been used.")
    if st.button("Back to homepage", type="primary"):
        st.query_params.clear()
        st.rerun()
    st.stop()


# ──────────────────────────────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <h1>Bike Check.</h1>
      <p>Know it's not stolen. In seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

n_reports = verified_report_count()
st.markdown(
    f'<div class="stats">{n_reports} verified report(s) in the database.</div>',
    unsafe_allow_html=True,
)


check_tab, report_tab, recovered_tab = st.tabs(["Check", "Report", "Recover"])


# ──────────────────────────────────────────────────────────────────────
# Check
# ──────────────────────────────────────────────────────────────────────
with check_tab:
    st.subheader("Enter the serial.")
    st.caption("We'll match it against verified stolen-bike reports. Spaces and punctuation are ignored.")
    serial = st.text_input(
        "Serial number", key="search_serial", label_visibility="collapsed",
        placeholder="e.g. WTU221L0123",
    )
    if DEMO_MODE and DEMO_BIKES:
        examples = " · ".join(b["serial"] for b in DEMO_BIKES[:2])
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
                        st.markdown(f"**Serial** · `{m['serial']}`")
                        descr = " · ".join(
                            b for b in (m.get("brand"), m.get("model"), m.get("color")) if b
                        )
                        if descr:
                            st.markdown(f"**Bike** · {descr}")
                        if m.get("theft_date"):
                            st.markdown(f"**Stolen** · {m['theft_date']}")
                        if m.get("theft_location"):
                            st.markdown(f"**Where** · {m['theft_location']}")
                        st.markdown(f"**Reported** · {m['created_at']}")
            st.info(
                "Do not buy this bike. Contact your local police and, if you can, "
                "keep a record of the seller's details."
            )


# ──────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────
with report_tab:
    st.subheader("Lost your bike?")
    st.caption(
        "Tell us about it. We'll warn the next buyer. Your email stays private — "
        "we use it only to verify the report."
    )

    with st.form("report_form", clear_on_submit=False):
        r_serial = st.text_input("Serial number", key="rep_serial", placeholder="Frame serial number")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            brand = st.text_input("Brand", key="rep_brand", placeholder="Trek")
        with col_b:
            model = st.text_input("Model", key="rep_model", placeholder="Domane SL 5")
        with col_c:
            color = st.text_input("Color", key="rep_color", placeholder="Matte black")
        col_d, col_e = st.columns(2)
        with col_d:
            theft_date = st.date_input(
                "Theft date", value=None, max_value=date.today(),
                format="YYYY-MM-DD", key="rep_date",
            )
        with col_e:
            theft_location = st.text_input(
                "Theft location", key="rep_location", placeholder="City, neighborhood",
            )
        owner_email = st.text_input(
            "Email", key="rep_email", placeholder="you@example.com",
            help="Used to verify the report and contact you on a match.",
        )
        photo = st.file_uploader(
            "Photo", type=["jpg", "jpeg", "png", "webp"], key="rep_photo",
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
                    "click your verification link below."
                )
                st.code(result[4:])
            elif result == "sent":
                st.success("Report submitted. Check your inbox for a verification link.")
            else:
                st.warning(
                    f"Report submitted, but the verification email failed to send ({result}). "
                    "Check server logs."
                )


# ──────────────────────────────────────────────────────────────────────
# Recover
# ──────────────────────────────────────────────────────────────────────
with recovered_tab:
    st.subheader("Got it back?")
    st.caption("Take your report down so future searches don't show a false warning.")
    with st.form("recovered_form", clear_on_submit=False):
        rec_serial = st.text_input("Serial number", key="rec_serial", placeholder="Frame serial number")
        rec_email = st.text_input(
            "Email used in the original report", key="rec_email",
            placeholder="you@example.com",
        )
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


# ──────────────────────────────────────────────────────────────────────
# How it works + disclaimer
# ──────────────────────────────────────────────────────────────────────
st.write("")
with st.expander("How it works"):
    st.markdown(
        "**Search.** Enter a frame serial. We match it against verified stolen-bike reports.\n\n"
        "**Report.** Submit your serial, a description, and your email. Click the verification "
        "link we send you and your report goes live.\n\n"
        "**Recover.** If your bike comes back, take your report down with the same serial and email."
    )

st.markdown(
    '<div class="disclaimer">A prototype. Reports are user-submitted and not a substitute '
    "for a police report or an official registry.</div>",
    unsafe_allow_html=True,
)
