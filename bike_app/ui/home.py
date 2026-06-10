"""Home view: hero, serial search, results, share card, action tiles."""

from datetime import datetime

import streamlit as st

from bike_app.badge import generate_badge_png, make_check_token
from bike_app.config import current_base_url, demo_mode
from bike_app.db import search_by_serial, verified_report_count
from bike_app.i18n import DEFAULT_LANG, current_lang, t
from bike_app.seed import DEMO_BIKES
from bike_app.ui.components import (
    advisory,
    disclaimer,
    hero,
    match_card,
    section_rule,
)
from bike_app.ui.recover import open_recover_dialog


def render_home_view() -> None:
    hero(t("tagline"))
    st.markdown(
        f'<div class="stats">{t("stats", n=verified_report_count())}</div>',
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
        placeholder=t("search_placeholder"),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if demo_mode() and DEMO_BIKES:
        st.caption(t("try_demo"))
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

    with st.expander(t("serial_help_title")):
        st.markdown(t("serial_help_body"))
    return serial


def _render_results(serial: str) -> None:
    matches = search_by_serial(serial)
    if not matches:
        st.markdown(
            f'<div class="clean-result"><h3>{t("no_reports_title")}</h3>'
            f"<p>{t('no_reports_body')}</p></div>",
            unsafe_allow_html=True,
        )
        _render_share_card(serial.strip())
        return

    st.error(t("stolen_banner", n=len(matches)))
    for m in matches:
        match_card(m)
    advisory(t("dont_buy_title"), t("advisory_home_body"))


def _render_share_card(serial: str) -> None:
    """Share card — only after a clean result."""
    ts = int(datetime.now().timestamp())
    token = make_check_token(serial, ts)
    lang = current_lang()
    lang_param = f"&lang={lang}" if lang != DEFAULT_LANG else ""
    share_url = (
        f"{current_base_url().rstrip('/')}/?v={serial}&c={token}{lang_param}"
    )

    with st.container(border=True):
        st.markdown(f"### {t('selling_title')}")
        st.caption(t("selling_caption"))

        link_col, btn_col = st.columns([4, 1])
        with link_col:
            st.text_input(
                "Share link", value=share_url, key="share_url",
                label_visibility="collapsed",
            )
        with btn_col:
            badge_bytes = generate_badge_png(serial, share_url, ts, lang=lang)
            st.download_button(
                t("badge_png"),
                data=badge_bytes,
                file_name=f"bikecheck-{serial}.png",
                mime="image/png",
                use_container_width=True,
            )

        st.caption(t("selling_explainer"))


def _render_action_tiles() -> None:
    section_rule()
    tile_left, tile_right = st.columns(2, gap="medium")

    with tile_left:
        with st.container(border=True):
            st.markdown(
                '<div class="action-tile">'
                '<span class="material-symbols-rounded icon danger">report</span>'
                f"<h3>{t('tile_report_title')}</h3>"
                f"<p>{t('tile_report_body')}</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            if st.button(
                t("tile_report_cta"), key="open_report",
                type="primary", use_container_width=True,
            ):
                st.session_state.view = "report"
                st.rerun()

    with tile_right:
        with st.container(border=True):
            st.markdown(
                '<div class="action-tile">'
                '<span class="material-symbols-rounded icon success">task_alt</span>'
                f"<h3>{t('tile_recover_title')}</h3>"
                f"<p>{t('tile_recover_body')}</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            if st.button(
                t("tile_recover_cta"), key="open_recover",
                type="primary", use_container_width=True,
            ):
                open_recover_dialog()


def _render_footer() -> None:
    st.write("")
    with st.expander(t("how_title")):
        st.markdown(t("how_body"))
    disclaimer()
