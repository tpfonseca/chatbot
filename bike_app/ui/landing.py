"""Shareable check-link landing view (?v=SERIAL&c=TOKEN).

A seller shares this link (or the QR badge pointing at it) on a listing.
The token only proves *when* the seller ran their check — the page
always re-checks the serial live, so a bike reported after the badge
was made still shows as flagged.
"""

import html

import streamlit as st

from bike_app.badge import verify_check_token
from bike_app.db import search_by_serial
from bike_app.i18n import clear_query_params_keep_lang, current_lang, t
from bike_app.ui.components import advisory, disclaimer, hero, section_rule
from bike_app.util import human_date


def render_landing_view(serial: str, token: str) -> None:
    seller_checked_ts = verify_check_token(serial, token)

    hero()

    matches = search_by_serial(serial)
    if matches:
        st.error(t("stolen_banner", n=len(matches)))
        for m in matches:
            with st.container(border=True):
                st.markdown(f"**{t('serial_word')}** · `{m['serial']}`")
                bits = [m.get("brand"), m.get("model"), m.get("color")]
                descr = " · ".join(b for b in bits if b)
                if descr:
                    st.markdown(f"**{t('bike_word')}** · {descr}")
                if m.get("theft_date"):
                    st.markdown(f"**{t('stolen_on')}** · {m['theft_date']}")
                if m.get("theft_location"):
                    st.markdown(f"**{t('stolen_in')}** · {m['theft_location']}")
        advisory(t("dont_buy_title"), t("advisory_landing_body"))
    else:
        serial_html = (
            f"<code style='font-size:1.1rem;'>{html.escape(serial)}</code>"
        )
        st.markdown(
            f'<div class="clean-result">'
            f"<h3>{t('landing_clean_title')}</h3>"
            f"<p>{t('landing_clean_body', serial=serial_html)}</p></div>",
            unsafe_allow_html=True,
        )
        if seller_checked_ts:
            st.caption(
                t("seller_posted",
                  date=human_date(seller_checked_ts, current_lang()))
            )
        st.info(t("heads_up"))

    section_rule()
    st.subheader(t("check_another"))
    new_serial = st.text_input(
        "Serial number", key="landing_search",
        placeholder=t("search_placeholder"),
        label_visibility="collapsed",
    )
    if new_serial.strip():
        # Switch back to home with the new serial pre-filled.
        st.session_state["_pending_search"] = new_serial.strip()
        clear_query_params_keep_lang()
        st.rerun()

    disclaimer()
