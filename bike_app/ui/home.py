"""Home view: hero, serial search, results, share card, action tiles."""

from datetime import datetime

import streamlit as st

from bike_app.badge import generate_badge_png, make_check_token
from bike_app.config import current_base_url, demo_mode
from bike_app.db import search_by_serial, verified_report_count
from bike_app.seed import DEMO_BIKES
from bike_app.ui.components import (
    advisory,
    disclaimer,
    hero,
    match_card,
    section_rule,
)
from bike_app.ui.recover import recover_dialog


def render_home_view() -> None:
    hero("Know it's not stolen. In seconds.")
    st.markdown(
        f'<div class="stats">{verified_report_count()} verified report(s) '
        "in the database.</div>",
        unsafe_allow_html=True,
    )

    serial = _render_search()
    if serial.strip():
        _render_results(serial)

    _render_action_tiles()
    _render_footer()


def _render_search() -> str:
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

    if demo_mode() and DEMO_BIKES:
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
    return serial


def _render_results(serial: str) -> None:
    matches = search_by_serial(serial)
    if not matches:
        st.markdown(
            '<div class="clean-result"><h3>No reports found.</h3>'
            "<p>That's a good sign — but it doesn't guarantee the bike isn't stolen. "
            "Many thefts are never reported here.</p></div>",
            unsafe_allow_html=True,
        )
        _render_share_card(serial.strip())
        return

    st.error(f"This bike has been reported stolen ({len(matches)} report(s)).")
    for m in matches:
        match_card(m)
    advisory(
        "Don't buy this bike.",
        "Contact your local police and, if you can, keep a record of the "
        "seller's details. Buying a bike you believe was stolen can be a "
        "crime in your jurisdiction.",
    )


def _render_share_card(serial: str) -> None:
    """Share card — only after a clean result."""
    ts = int(datetime.now().timestamp())
    token = make_check_token(serial, ts)
    share_url = f"{current_base_url().rstrip('/')}/?v={serial}&c={token}"

    with st.container(border=True):
        st.markdown("### Selling this bike?")
        st.caption(
            "Add proof to your listing — buyers trust it, "
            "and your bike sells faster."
        )

        link_col, btn_col = st.columns([4, 1])
        with link_col:
            st.text_input(
                "Share link", value=share_url, key="share_url",
                label_visibility="collapsed",
            )
        with btn_col:
            badge_bytes = generate_badge_png(serial, share_url, ts)
            st.download_button(
                "Badge PNG",
                data=badge_bytes,
                file_name=f"bikecheck-{serial}.png",
                mime="image/png",
                use_container_width=True,
            )

        st.caption(
            "Paste the link into your listing, or download the badge image "
            "(with QR code) to upload as a photo. When a buyer clicks the "
            "link or scans the QR, we re-check the serial live."
        )


def _render_action_tiles() -> None:
    section_rule()
    tile_left, tile_right = st.columns(2, gap="medium")

    with tile_left:
        with st.container(border=True):
            st.markdown(
                '<div class="action-tile">'
                '<span class="material-symbols-rounded icon danger">report</span>'
                "<h3>Report a stolen bike</h3>"
                "<p>Tell future buyers it's gone, so no one buys your bike from the thief.</p>"
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
                "<h3>Mark a bike as recovered</h3>"
                "<p>Got your bike back? Take down your warning so future searches stay accurate.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            if st.button(
                "Open →", key="open_recover", type="primary", use_container_width=True,
            ):
                recover_dialog()


def _render_footer() -> None:
    st.write("")
    with st.expander("How it works"):
        st.markdown(
            "**Search.** Type a frame serial. We match it against verified reports — "
            "spaces, dashes, and casing are ignored.\n\n"
            "**Report.** Submit your serial and email. Click the link we send you and "
            "your report goes live.\n\n"
            "**Recover.** Got your bike back? Take your report down with the same serial and email."
        )
    disclaimer()
