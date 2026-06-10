"""Dedicated report-a-stolen-bike view."""

import uuid
from datetime import date

import streamlit as st

from bike_app.config import current_base_url, is_valid_email
from bike_app.db import insert_report
from bike_app.email_utils import send_verification
from bike_app.geocode import geocode
from bike_app.ui.components import field_label
from bike_app.uploads import save_photo

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


def _location_options(query: str):
    """Format Nominatim results as (display, value) tuples for the searchbox."""
    return [(label, (label, lat, lng)) for (label, lat, lng) in geocode(query)]


def render_report_view() -> None:
    if st.button("← Back", key="back_to_home"):
        st.session_state.view = "home"
        st.rerun()
    st.markdown(
        '<div class="page-header">'
        "<h1>Report a stolen bike</h1>"
        "<p>Tell us about it. We'll warn the next buyer. "
        "Your email stays private — we only use it to verify the report.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    _render_report_form()


def _render_report_form() -> None:
    field_label("Serial number", required=True)
    r_serial = st.text_input(
        "Serial number", key="rep_serial",
        placeholder="Frame serial number",
        label_visibility="collapsed",
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        field_label("Brand")
        brand = st.text_input(
            "Brand", key="rep_brand", placeholder="Trek", label_visibility="collapsed",
        )
    with col_b:
        field_label("Model")
        model = st.text_input(
            "Model", key="rep_model", placeholder="Domane SL 5", label_visibility="collapsed",
        )
    with col_c:
        field_label("Color")
        color = st.text_input(
            "Color", key="rep_color", placeholder="Matte black", label_visibility="collapsed",
        )

    field_label("Theft date")
    theft_date = st.date_input(
        "Theft date", value=None, max_value=date.today(),
        format="YYYY-MM-DD", key="rep_date", label_visibility="collapsed",
    )

    field_label("Theft location")
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

    field_label("Email", required=True)
    owner_email = st.text_input(
        "Email", key="rep_email",
        placeholder="you@example.com",
        label_visibility="collapsed",
        help="Used to verify the report and contact you on a match.",
    )

    field_label("Photo")
    photo = st.file_uploader(
        "Photo", type=["jpg", "jpeg", "png", "webp"],
        key="rep_photo", label_visibility="collapsed",
    )

    submitted = st.button("Submit report", type="primary", key="rep_submit")

    if submitted:
        if not r_serial.strip() or not owner_email.strip():
            st.error("Serial number and email are required.")
            return
        if not is_valid_email(owner_email):
            st.error("That email doesn't look right.")
            return

        photo_path = None
        if photo is not None:
            try:
                photo_path = save_photo(photo.name, photo.getbuffer().tobytes())
            except ValueError as e:
                st.error(str(e))
                return

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
        result = send_verification(email_addr, token, current_base_url())
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
