import os
import re
import uuid
from datetime import date, datetime
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
from bike_app.geocode import geocode
from bike_app.seed import DEMO_BIKES, seed_if_empty
from bike_app.share import make_check_token, verify_check_token

try:
    from streamlit_searchbox import st_searchbox
    _HAS_SEARCHBOX = True
except Exception:
    _HAS_SEARCHBOX = False

try:
    import folium
    from streamlit_folium import st_folium
    _HAS_FOLIUM = True
except Exception:
    _HAS_FOLIUM = False


def _field_label(label: str, required: bool = False) -> None:
    tag = ' <span class="required-tag">Required</span>' if required else ""
    st.markdown(
        f'<div class="field-label">{label}{tag}</div>', unsafe_allow_html=True
    )


def _current_base_url() -> str:
    """Detect the public URL the visitor is actually using.

    Reads it from the request headers Streamlit exposes via st.context so
    that verification links work whether the app is on localhost, Streamlit
    Cloud, behind a proxy, etc. Falls back to the BASE_URL env var when no
    request context is available (e.g. AppTest).
    """
    try:
        headers = st.context.headers
        host = headers.get("Host") or headers.get("host")
        if host:
            proto = (
                headers.get("X-Forwarded-Proto")
                or headers.get("x-forwarded-proto")
                or ("http" if host.startswith("localhost") else "https")
            )
            return f"{proto}://{host}"
    except Exception:
        pass
    return os.getenv("BASE_URL", "http://localhost:8501")


def _location_options(query: str):
    """Format Nominatim results as (display, value) tuples for the searchbox."""
    return [(label, (label, lat, lng)) for (label, lat, lng) in geocode(query)]

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
        --red-soft: #fff1f1;
        --green: #248a3d;
      }

      html, body, .stApp, [data-testid="stAppViewContainer"],
      h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput,
      .stDateInput, .stTextArea, .stButton, .stFormSubmitButton,
      button, input, textarea {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
          "SF Pro Text", "Helvetica Neue", "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
      }

      /* Don't ever override Material Symbols on icon spans — Streamlit
         uses ligatures and an SF override would render the literal
         icon name as text (e.g. "arrow_right"). */
      [data-testid="stIconMaterial"],
      .material-symbols-rounded,
      .material-symbols-outlined,
      .material-icons,
      [class*="material-symbols"],
      [class*="material-icons"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined",
          "Material Icons" !important;
        letter-spacing: normal !important;
      }

      #MainMenu, footer { visibility: hidden; }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stToolbar"] { right: 0.5rem; }

      .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 760px;
      }

      /* Hero */
      .hero { text-align: center; padding: 2rem 0 0.5rem; }
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
      }
      .stats {
        text-align: center;
        color: var(--ink-faint);
        font-size: 0.9rem;
        margin: 0.5rem 0 2rem;
      }

      h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
        color: var(--ink) !important;
      }

      /* Inputs */
      .stTextInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid var(--line) !important;
        background: var(--bg) !important;
        font-size: 1rem !important;
        padding: 0.85rem 1rem !important;
      }
      .stTextInput input:focus, .stDateInput input:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15) !important;
      }
      /* Make the primary search input bigger */
      .search-block .stTextInput input {
        font-size: 1.2rem !important;
        padding: 1.1rem 1.25rem !important;
        text-align: center;
      }

      /* Buttons */
      .stButton button, .stFormSubmitButton button {
        border-radius: 980px !important;
        padding: 0.6rem 1.75rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        border: 1px solid transparent !important;
        transition: filter 0.15s ease, background 0.15s ease;
      }
      .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
        background: var(--blue) !important;
        color: white !important;
      }
      .stButton button[kind="primary"]:hover,
      .stFormSubmitButton button[kind="primary"]:hover { filter: brightness(1.05); }
      .stButton button[kind="primary"]:disabled,
      .stFormSubmitButton button[kind="primary"]:disabled {
        opacity: 0.35 !important; filter: none !important;
      }
      /* Secondary / chip buttons */
      .stButton button[kind="secondary"] {
        background: var(--bg-soft) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
      }
      .stButton button[kind="secondary"]:hover { background: #ececef !important; }

      /* Cards with border */
      [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border-color: var(--line) !important;
        background: var(--bg) !important;
        padding: 1.5rem !important;
      }

      /* Alerts */
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
      [data-testid="stExpander"] summary { font-weight: 500 !important; }

      [data-testid="stFileUploaderDropzone"] {
        border-radius: 14px !important;
        border: 1px dashed var(--line) !important;
        background: var(--bg-soft) !important;
      }

      /* The big match card */
      .match-card {
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1rem;
        background: var(--bg);
      }
      .match-card .badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--red);
        background: var(--red-soft);
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        margin-bottom: 0.75rem;
      }
      .match-card h3 {
        margin: 0 0 0.25rem !important;
        font-size: 1.5rem !important;
      }
      .match-card .color { color: var(--ink-soft); margin: 0 0 0.75rem; }
      .match-card .serial {
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        color: var(--ink-soft);
        font-size: 0.95rem;
        margin: 0 0 1rem;
      }
      .match-card .meta { color: var(--ink-soft); font-size: 0.95rem; line-height: 1.6; }
      .match-card .meta strong { color: var(--ink); font-weight: 500; }

      .advisory {
        background: var(--red-soft);
        border: 1px solid #f5c2c0;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-top: 1.25rem;
      }
      .advisory h4 {
        margin: 0 0 0.25rem !important;
        color: var(--red) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
      }
      .advisory p { margin: 0 !important; color: var(--ink) !important; font-size: 0.95rem; }

      .clean-result {
        text-align: center;
        padding: 1.5rem;
        color: var(--ink-soft);
      }
      .clean-result h3 {
        color: var(--green) !important;
        margin: 0 0 0.5rem !important;
        font-size: 1.5rem !important;
      }

      /* Action tiles — the visual replacement for the bottom expanders */
      .action-tile {
        text-align: center;
        padding: 1.75rem 1rem 0.5rem;
      }
      .action-tile .icon {
        font-size: 56px;
        display: inline-block;
        margin-bottom: 0.5rem;
        line-height: 1;
      }
      .action-tile .icon.danger { color: var(--red); }
      .action-tile .icon.success { color: var(--green); }
      .action-tile h3 {
        margin: 0.4rem 0 0.4rem !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
      }
      .action-tile p {
        color: var(--ink-soft);
        margin: 0 0 1.25rem !important;
        font-size: 0.95rem;
        line-height: 1.45;
      }

      /* Page header on dedicated views (Report) */
      .page-header { padding: 0.5rem 0 1.5rem; }
      .page-header h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        margin: 0 0 0.25rem !important;
      }
      .page-header p { color: var(--ink-soft); margin: 0 !important; }

      .section-rule {
        border: 0;
        border-top: 1px solid var(--line);
        margin: 3rem 0 2rem;
      }

      /* Field labels (separate from Streamlit's built-in label, so we can
         add a "Required" tag inline). */
      .field-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--ink);
        margin: 0.5rem 0 0.4rem;
      }
      .field-label .required-tag {
        font-weight: 400;
        color: var(--ink-faint);
        font-size: 0.8rem;
        margin-left: 0.5rem;
      }

      .disclaimer {
        text-align: center;
        font-size: 0.85rem;
        color: var(--ink-faint);
        margin-top: 3rem;
        line-height: 1.5;
      }

      /* Share-card paste snippet: wrap long URLs on mobile and keep the
         copy-to-clipboard button visible without requiring hover (touch
         devices have no hover state). */
      [data-testid="stCode"] pre,
      [data-testid="stCode"] code {
        white-space: pre-wrap !important;
        overflow-wrap: anywhere !important;
      }
      /* The toolbar wrapper (Streamlit's absolutely-positioned div that
         holds the copy button) is hidden by default and only fades in on
         hover. Force it visible so touch users see the copy affordance. */
      [data-testid="stCode"] > div {
        opacity: 1 !important;
        visibility: visible !important;
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
    st.markdown('<div class="hero"><h1>Bike Check.</h1></div>', unsafe_allow_html=True)
    if ok:
        st.success("Report verified. It will now appear in searches.")
    else:
        st.error("This verification link is invalid or has already been used.")
    if st.button("Back to homepage", type="primary"):
        st.query_params.clear()
        st.rerun()
    st.stop()


# ──────────────────────────────────────────────────────────────────────
# Shareable check-link landing page  (?v=SERIAL&c=TOKEN)
# ──────────────────────────────────────────────────────────────────────
if "v" in st.query_params:
    landing_serial = st.query_params["v"]
    landing_token = st.query_params.get("c", "")
    seller_checked_ts = verify_check_token(landing_serial, landing_token)

    st.markdown(
        '<div class="hero"><h1>Bike Check.</h1></div>', unsafe_allow_html=True
    )

    # Re-check live — the badge is just a hint; the DB is the truth.
    matches = search_by_serial(landing_serial)
    if matches:
        st.error(f"This bike has been reported stolen ({len(matches)} report(s)).")
        for m in matches:
            with st.container(border=True):
                st.markdown(f"**Serial** · `{m['serial']}`")
                bits = [m.get("brand"), m.get("model"), m.get("color")]
                descr = " · ".join(b for b in bits if b)
                if descr:
                    st.markdown(f"**Bike** · {descr}")
                if m.get("theft_date"):
                    st.markdown(f"**Stolen on** · {m['theft_date']}")
                if m.get("theft_location"):
                    st.markdown(f"**Stolen in** · {m['theft_location']}")
        st.markdown(
            '<div class="advisory">'
            "<h4>Don't buy this bike.</h4>"
            "<p>Even though the seller shared a check link, this serial is now "
            "flagged as stolen. Contact your local police.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="clean-result">'
            f"<h3>No reports for this bike.</h3>"
            f"<p>Serial <code style='font-size:1.1rem;'>{landing_serial}</code> "
            f"doesn't match any reported-stolen bike in our database.</p></div>",
            unsafe_allow_html=True,
        )
        if seller_checked_ts:
            checked_str = datetime.fromtimestamp(seller_checked_ts).strftime(
                "%B %-d, %Y"
            )
            st.caption(f"Seller posted this check on {checked_str}.")
        st.info(
            "**Heads up.** This means the serial isn't on our list — it does "
            "not prove the seller owns the bike. When you meet, check the "
            "serial on the badge matches the serial etched on the frame."
        )

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    st.subheader("Check another bike")
    new_serial = st.text_input(
        "Serial number", key="landing_search",
        placeholder="Type the frame serial and press Enter",
        label_visibility="collapsed",
    )
    if new_serial.strip():
        # Switch back to home with the new serial pre-filled.
        st.session_state["_pending_search"] = new_serial.strip()
        st.query_params.clear()
        st.rerun()

    st.markdown(
        '<div class="disclaimer">A prototype. Reports are user-submitted and '
        "not a substitute for a police report or an official registry.</div>",
        unsafe_allow_html=True,
    )
    st.stop()


# ──────────────────────────────────────────────────────────────────────
# Dedicated Report view + Recover dialog
# ──────────────────────────────────────────────────────────────────────
def _render_report_form() -> None:
    """The report-a-stolen-bike form, rendered on a dedicated view because
    it has too many fields to fit comfortably in a modal."""

    _field_label("Serial number", required=True)
    r_serial = st.text_input(
        "Serial number", key="rep_serial",
        placeholder="Frame serial number",
        label_visibility="collapsed",
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        _field_label("Brand")
        brand = st.text_input(
            "Brand", key="rep_brand", placeholder="Trek", label_visibility="collapsed",
        )
    with col_b:
        _field_label("Model")
        model = st.text_input(
            "Model", key="rep_model", placeholder="Domane SL 5", label_visibility="collapsed",
        )
    with col_c:
        _field_label("Color")
        color = st.text_input(
            "Color", key="rep_color", placeholder="Matte black", label_visibility="collapsed",
        )

    _field_label("Theft date")
    theft_date = st.date_input(
        "Theft date", value=None, max_value=date.today(),
        format="YYYY-MM-DD", key="rep_date", label_visibility="collapsed",
    )

    _field_label("Theft location")
    st.caption(
        "Start typing a city, area, or street. We fetch real geo data so the "
        "report shows up in the right place."
    )
    location_value = None
    if _HAS_SEARCHBOX:
        location_value = st_searchbox(
            _location_options,
            placeholder="Start typing…",
            key="rep_location_searchbox",
            clear_on_submit=False,
        )
    else:
        text = st.text_input(
            "Theft location", key="rep_location_text",
            placeholder="City, neighborhood",
            label_visibility="collapsed",
        )
        location_value = (text.strip(), None, None) if text.strip() else None

    final_lat, final_lng, final_label = None, None, None
    if location_value:
        loc_label, lat, lng = location_value
        final_label = loc_label
        final_lat, final_lng = lat, lng

        override_key = f"_map_override::{loc_label}"
        if override_key in st.session_state:
            final_lat, final_lng = st.session_state[override_key]

        if lat is not None and lng is not None:
            st.caption(f"📍 {loc_label} · {final_lat:.5f}, {final_lng:.5f}")
        else:
            st.caption(f"📍 {loc_label}")

        if _HAS_FOLIUM and lat is not None and lng is not None:
            if st.toggle("Adjust the pin on a map", key="rep_show_map"):
                m = folium.Map(
                    location=[final_lat, final_lng], zoom_start=15,
                    tiles="OpenStreetMap",
                )
                folium.Marker(
                    [final_lat, final_lng],
                    tooltip="Click anywhere on the map to move the pin",
                ).add_to(m)
                map_result = st_folium(
                    m, height=320, width=None, key="rep_map",
                    returned_objects=["last_clicked"],
                )
                if map_result and map_result.get("last_clicked"):
                    new_lat = map_result["last_clicked"]["lat"]
                    new_lng = map_result["last_clicked"]["lng"]
                    if (round(new_lat, 5), round(new_lng, 5)) != (
                        round(final_lat, 5), round(final_lng, 5)
                    ):
                        st.session_state[override_key] = (new_lat, new_lng)
                        st.rerun()

    _field_label("Email", required=True)
    owner_email = st.text_input(
        "Email", key="rep_email",
        placeholder="you@example.com",
        label_visibility="collapsed",
        help="Used to verify the report and contact you on a match.",
    )

    _field_label("Photo")
    photo = st.file_uploader(
        "Photo", type=["jpg", "jpeg", "png", "webp"],
        key="rep_photo", label_visibility="collapsed",
    )

    submitted = st.button("Submit report", type="primary", key="rep_submit")

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
                theft_location=final_label,
                theft_lat=final_lat,
                theft_lng=final_lng,
                owner_email=owner_email.strip(),
                photo_path=photo_path,
                token=token,
            )
            email_addr = owner_email.strip()
            result = send_verification(email_addr, token, _current_base_url())
            if result.startswith("dev:"):
                link = result[4:]
                st.success(
                    f"Report submitted. Email delivery is in dev mode — "
                    f"this is the link we'd send to {email_addr}."
                )
                st.link_button("Open verification link →", link)
            elif result == "sent":
                st.success(
                    f"Report submitted. We sent a verification link to {email_addr}. "
                    "Click it to make your report live."
                )
            else:
                st.warning(
                    f"Report submitted, but the verification email failed to send ({result}). "
                    "Check server logs."
                )


@st.dialog("Mark a bike as recovered")
def _recover_dialog() -> None:
    """Short modal: take down a verified stolen-bike report."""
    st.caption(
        "We'll take your report down so future searches don't show a false "
        "warning. We match on the serial and the email you used to report it."
    )
    rec_serial = st.text_input(
        "Serial number", key="rec_serial",
        placeholder="Frame serial number",
    )
    rec_email = st.text_input(
        "Email used in the original report", key="rec_email",
        placeholder="you@example.com",
    )
    rec_confirm = st.checkbox(
        "Yes, I have my bike back. Take the warning down.",
        key="rec_confirm",
    )
    if st.button(
        "Mark recovered", type="primary",
        disabled=not rec_confirm, key="rec_submit",
    ):
        if not rec_serial.strip() or not rec_email.strip():
            st.error("Serial number and email are required.")
        elif mark_recovered(rec_serial.strip(), rec_email.strip()):
            st.success(
                "Marked as recovered. The report no longer appears in searches."
            )
        else:
            st.error(
                "Couldn't find a verified report matching that serial and email. "
                "Double-check both, or contact us if your bike is still listed."
            )


# View router. ?verify=… already short-circuited above; here we just decide
# between the home view (default) and the dedicated Report view.
if st.session_state.get("view") == "report":
    if st.button("← Back", key="back_to_home"):
        st.session_state.view = "home"
        st.rerun()
    st.markdown(
        '<div class="page-header">'
        '<h1>Report a stolen bike</h1>'
        "<p>Tell us about it. We'll warn the next buyer. "
        "Your email stays private — we only use it to verify the report.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    _render_report_form()
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
st.markdown(
    f'<div class="stats">{verified_report_count()} verified report(s) in the database.</div>',
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────
# Search (primary)
# ──────────────────────────────────────────────────────────────────────
# A chip click sets _pending_search; we move it into the widget's
# session_state BEFORE the widget is instantiated, since Streamlit forbids
# writing to a widget's key after it's been created in the same run.
if "_pending_search" in st.session_state:
    st.session_state.search_serial = st.session_state.pop("_pending_search")

st.markdown('<div class="search-block">', unsafe_allow_html=True)
serial = st.text_input(
    "Serial number",
    key="search_serial",
    label_visibility="collapsed",
    placeholder="Type the frame serial and press Enter",
)
st.markdown("</div>", unsafe_allow_html=True)

if DEMO_MODE and DEMO_BIKES:
    st.caption("Try a demo serial")
    chip_cols = st.columns(min(3, len(DEMO_BIKES)))
    for i, b in enumerate(DEMO_BIKES[: len(chip_cols)]):
        with chip_cols[i]:
            if st.button(
                b["serial"],
                key=f"chip_{i}",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state["_pending_search"] = b["serial"]
                st.rerun()

with st.expander("Where do I find the serial?"):
    st.markdown(
        "The serial number is etched onto the bike frame. The most common spot "
        "is **under the bottom bracket** — flip the bike over and look at the "
        "joint where the pedals attach. It can also be on the **seat tube**, "
        "the **head tube**, or near the **rear wheel mount**. Numbers and "
        "letters only; spaces and dashes are ignored when we search."
    )


# ──────────────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────────────
def _format_date(s: str | None) -> str:
    if not s:
        return ""
    try:
        return date.fromisoformat(s).strftime("%B %-d, %Y")
    except Exception:
        return s


if serial.strip():
    matches = search_by_serial(serial)
    if not matches:
        st.markdown(
            '<div class="clean-result"><h3>No reports found.</h3>'
            "<p>That's a good sign — but it doesn't guarantee the bike isn't stolen. "
            "Many thefts are never reported here.</p></div>",
            unsafe_allow_html=True,
        )

        # Share card — only after a clean result.
        clean_serial = serial.strip().upper()
        ts = int(datetime.now().timestamp())
        token = make_check_token(clean_serial, ts)
        share_url = (
            f"{_current_base_url().rstrip('/')}/?v={clean_serial}&c={token}"
        )

        with st.container(border=True):
            st.markdown("### Your bike checks out")
            st.markdown(
                "Help start a Danish norm: **serials in every listing.** "
                "Paste this into your DBA or Blocket ad — buyers can "
                "re-verify live with one click."
            )

            en_tab, da_tab = st.tabs(["English", "Dansk"])
            with en_tab:
                st.code(
                    f"Frame serial: {clean_serial}\n"
                    f"✓ Verified on Bike Check — no theft reports:\n"
                    f"{share_url}",
                    language=None,
                )
            with da_tab:
                st.code(
                    f"Stelnummer: {clean_serial}\n"
                    f"✓ Tjekket på Bike Check — ingen tyverianmeldelser:\n"
                    f"{share_url}",
                    language=None,
                )

            st.caption(
                "Click the copy icon, then paste into the listing description. "
                "The link re-checks the serial against the database every time "
                "it's opened, so it stays honest if the bike gets reported later."
            )
    else:
        st.error(f"This bike has been reported stolen ({len(matches)} report(s)).")
        for m in matches:
            name = " ".join(b for b in (m.get("brand"), m.get("model")) if b) or "Unknown bike"
            color = m.get("color") or ""
            when = _format_date(m.get("theft_date"))
            where = m.get("theft_location") or ""
            reported = (m.get("created_at") or "").split(" ")[0]

            meta_lines = []
            if when or where:
                bits = []
                if when:
                    bits.append(f"<strong>{when}</strong>")
                if where:
                    bits.append(f"in <strong>{where}</strong>")
                meta_lines.append(f"Stolen {' '.join(bits)}")
            if m.get("theft_lat") is not None and m.get("theft_lng") is not None:
                lat, lng = m["theft_lat"], m["theft_lng"]
                map_url = (
                    f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}"
                    f"#map=15/{lat}/{lng}"
                )
                meta_lines.append(
                    f'<a href="{map_url}" target="_blank" '
                    f'style="color: var(--blue); text-decoration: none;">'
                    f'View on map ↗</a>'
                )
            meta_lines.append(f"Reported on <strong>{reported}</strong>")

            photo_html = ""
            if m.get("photo_path") and Path(m["photo_path"]).exists():
                photo_html = ""  # rendered with st.image below the card

            st.markdown(
                f'''
                <div class="match-card">
                  <div class="badge">Reported stolen</div>
                  <h3>{name}</h3>
                  {f'<p class="color">{color}</p>' if color else ''}
                  <p class="serial">Serial · {m["serial"]}</p>
                  <div class="meta">{"<br>".join(meta_lines)}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
            if m.get("photo_path") and Path(m["photo_path"]).exists():
                st.image(m["photo_path"])

        st.markdown(
            '<div class="advisory">'
            "<h4>Don't buy this bike.</h4>"
            "<p>Contact your local police and, if you can, keep a record of the seller's details. "
            "Buying a bike you believe was stolen can be a crime in your jurisdiction.</p>"
            "</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────
# Secondary actions — visual tiles
# ──────────────────────────────────────────────────────────────────────
st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

tile_left, tile_right = st.columns(2, gap="medium")

with tile_left:
    with st.container(border=True):
        st.markdown(
            '<div class="action-tile">'
            '<span class="material-symbols-rounded icon danger">report</span>'
            '<h3>Report a stolen bike</h3>'
            '<p>Tell future buyers it\'s gone, so no one buys your bike from the thief.</p>'
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Start →", key="open_report", type="primary", use_container_width=True,
        ):
            st.session_state.view = "report"
            st.rerun()

with tile_right:
    with st.container(border=True):
        st.markdown(
            '<div class="action-tile">'
            '<span class="material-symbols-rounded icon success">task_alt</span>'
            '<h3>Mark a bike as recovered</h3>'
            "<p>Got your bike back? Take down your warning so future searches stay accurate.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Open →", key="open_recover", type="primary", use_container_width=True,
        ):
            _recover_dialog()


# ──────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────
st.write("")
with st.expander("How it works"):
    st.markdown(
        "**Search.** Type a frame serial. We match it against verified reports — "
        "spaces, dashes, and casing are ignored.\n\n"
        "**Report.** Submit your serial and email. Click the link we send you and "
        "your report goes live.\n\n"
        "**Recover.** Got your bike back? Take your report down with the same serial and email."
    )

st.markdown(
    '<div class="disclaimer">A prototype. Reports are user-submitted and not a substitute '
    "for a police report or an official registry.</div>",
    unsafe_allow_html=True,
)
