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
from bike_app.ui.components import advisory, disclaimer, hero, section_rule
from bike_app.util import human_date


def render_landing_view(serial: str, token: str) -> None:
    seller_checked_ts = verify_check_token(serial, token)

    hero()

    matches = search_by_serial(serial)
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
        advisory(
            "Don't buy this bike.",
            "Even though the seller shared a check link, this serial is now "
            "flagged as stolen. Contact your local police.",
        )
    else:
        st.markdown(
            f'<div class="clean-result">'
            f"<h3>No reports for this bike.</h3>"
            f"<p>Serial <code style='font-size:1.1rem;'>{html.escape(serial)}</code> "
            f"doesn't match any reported-stolen bike in our database.</p></div>",
            unsafe_allow_html=True,
        )
        if seller_checked_ts:
            st.caption(
                f"Seller posted this check on {human_date(seller_checked_ts)}."
            )
        st.info(
            "**Heads up.** This means the serial isn't on our list — it does "
            "not prove the seller owns the bike. When you meet, check the "
            "serial on the badge matches the serial etched on the frame."
        )

    section_rule()
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

    disclaimer()
