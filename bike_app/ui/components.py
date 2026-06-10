"""Shared UI building blocks.

Anything here that interpolates user-supplied data into HTML must escape
it first — reports are public input, so a brand of "<script>…" has to
render as text, never as markup.
"""

import html
from pathlib import Path

import streamlit as st

from bike_app.i18n import LANGUAGES, current_lang, t
from bike_app.util import human_date


def inject_styles() -> None:
    css = (Path(__file__).parent / "styles.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def language_picker() -> None:
    """Compact selector shown on every view; persists for the session and
    is mirrored into ?lang= so reloads and shared URLs keep the language."""
    codes = list(LANGUAGES)
    _, col = st.columns([4, 1])
    with col:
        choice = st.selectbox(
            "Language",
            codes,
            index=codes.index(current_lang()),
            format_func=LANGUAGES.get,
            key="lang_picker",
            label_visibility="collapsed",
        )
    if choice != st.session_state.get("lang"):
        st.session_state.lang = choice
        st.query_params["lang"] = choice
        st.rerun()


def hero(tagline: str | None = None) -> None:
    # Taglines are our own i18n strings (not user input); quote=False keeps
    # apostrophes readable in the markup while still escaping <, >, &.
    tag = f"<p>{html.escape(tagline, quote=False)}</p>" if tagline else ""
    st.markdown(
        f'<div class="hero"><h1>Bike Check.</h1>{tag}</div>',
        unsafe_allow_html=True,
    )


def field_label(label: str, required: bool = False) -> None:
    tag = (
        f' <span class="required-tag">{html.escape(t("required_tag"))}</span>'
        if required
        else ""
    )
    st.markdown(
        f'<div class="field-label">{html.escape(label)}{tag}</div>',
        unsafe_allow_html=True,
    )


def section_rule() -> None:
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)


def disclaimer() -> None:
    st.markdown(
        f'<div class="disclaimer">{html.escape(t("disclaimer"))}</div>',
        unsafe_allow_html=True,
    )


def advisory(title: str, body: str) -> None:
    st.markdown(
        f'<div class="advisory"><h4>{html.escape(title)}</h4>'
        f"<p>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def match_card(m: dict) -> None:
    """Render one stolen-bike report as a card. All report fields are
    user-submitted and get escaped."""
    name = " ".join(b for b in (m.get("brand"), m.get("model")) if b) or t("unknown_bike")
    color = m.get("color") or ""
    when = human_date(m.get("theft_date"), current_lang())
    where = m.get("theft_location") or ""
    reported = (m.get("created_at") or "").split(" ")[0]

    meta_lines = []
    if when or where:
        bits = []
        if when:
            bits.append(f"<strong>{html.escape(when)}</strong>")
        if where:
            bits.append(f"{t('in_word')} <strong>{html.escape(where)}</strong>")
        meta_lines.append(f"{t('stolen_word')} {' '.join(bits)}")
    if m.get("theft_lat") is not None and m.get("theft_lng") is not None:
        lat, lng = float(m["theft_lat"]), float(m["theft_lng"])
        map_url = (
            f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}"
            f"#map=15/{lat}/{lng}"
        )
        meta_lines.append(
            f'<a href="{map_url}" target="_blank" '
            f'style="color: var(--blue); text-decoration: none;">'
            f"{t('view_on_map')}</a>"
        )
    meta_lines.append(f"{t('reported_on')} <strong>{html.escape(reported)}</strong>")

    color_html = f'<p class="color">{html.escape(color)}</p>' if color else ""
    st.markdown(
        f'''
        <div class="match-card">
          <div class="badge">{html.escape(t("badge_reported_stolen"))}</div>
          <h3>{html.escape(name)}</h3>
          {color_html}
          <p class="serial">{t("serial_word")} · {html.escape(m["serial"])}</p>
          <div class="meta">{"<br>".join(meta_lines)}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    if m.get("photo_path") and Path(m["photo_path"]).exists():
        st.image(m["photo_path"])
