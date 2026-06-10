"""Shared UI building blocks.

Anything here that interpolates user-supplied data into HTML must escape
it first — reports are public input, so a brand of "<script>…" has to
render as text, never as markup.
"""

import html
from pathlib import Path

import streamlit as st

from bike_app.util import human_date


def inject_styles() -> None:
    css = (Path(__file__).parent / "styles.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def hero(tagline: str | None = None) -> None:
    tag = f"<p>{html.escape(tagline)}</p>" if tagline else ""
    st.markdown(
        f'<div class="hero"><h1>Bike Check.</h1>{tag}</div>',
        unsafe_allow_html=True,
    )


def field_label(label: str, required: bool = False) -> None:
    tag = ' <span class="required-tag">Required</span>' if required else ""
    st.markdown(
        f'<div class="field-label">{html.escape(label)}{tag}</div>',
        unsafe_allow_html=True,
    )


def section_rule() -> None:
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)


def disclaimer() -> None:
    st.markdown(
        '<div class="disclaimer">A prototype. Reports are user-submitted and '
        "not a substitute for a police report or an official registry.</div>",
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
    name = " ".join(b for b in (m.get("brand"), m.get("model")) if b) or "Unknown bike"
    color = m.get("color") or ""
    when = human_date(m.get("theft_date"))
    where = m.get("theft_location") or ""
    reported = (m.get("created_at") or "").split(" ")[0]

    meta_lines = []
    if when or where:
        bits = []
        if when:
            bits.append(f"<strong>{html.escape(when)}</strong>")
        if where:
            bits.append(f"in <strong>{html.escape(where)}</strong>")
        meta_lines.append(f"Stolen {' '.join(bits)}")
    if m.get("theft_lat") is not None and m.get("theft_lng") is not None:
        lat, lng = float(m["theft_lat"]), float(m["theft_lng"])
        map_url = (
            f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}"
            f"#map=15/{lat}/{lng}"
        )
        meta_lines.append(
            f'<a href="{map_url}" target="_blank" '
            f'style="color: var(--blue); text-decoration: none;">'
            f"View on map ↗</a>"
        )
    meta_lines.append(f"Reported on <strong>{html.escape(reported)}</strong>")

    color_html = f'<p class="color">{html.escape(color)}</p>' if color else ""
    st.markdown(
        f'''
        <div class="match-card">
          <div class="badge">Reported stolen</div>
          <h3>{html.escape(name)}</h3>
          {color_html}
          <p class="serial">Serial · {html.escape(m["serial"])}</p>
          <div class="meta">{"<br>".join(meta_lines)}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    if m.get("photo_path") and Path(m["photo_path"]).exists():
        st.image(m["photo_path"])
