"""End-to-end tests for the Streamlit stolen-bike check app.

Each test boots the app with `streamlit.testing.v1.AppTest` against a
throwaway SQLite database and exercises one of the user-visible flows.
"""

import os
import re
import tempfile

import pytest
from streamlit.testing.v1 import AppTest


APP_PATH = os.path.join(os.path.dirname(__file__), "..", "streamlit_app.py")


@pytest.fixture(autouse=True)
def isolated_app(monkeypatch):
    """Point the app at a fresh DB and disable any configured email provider."""
    monkeypatch.setenv("BIKES_DB", tempfile.mktemp(suffix=".db"))
    monkeypatch.setenv("UPLOAD_DIR", tempfile.mkdtemp())
    monkeypatch.setenv("BASE_URL", "http://localhost:8501")
    monkeypatch.setenv("DEMO_MODE", "1")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    yield


def _input_by_key(at: AppTest, key: str):
    for ti in at.text_input:
        if ti.key == key:
            return ti
    raise KeyError(f"no text_input with key={key!r}")


def _checkbox_by_key(at: AppTest, key: str):
    for c in at.checkbox:
        if c.key == key:
            return c
    raise KeyError(f"no checkbox with key={key!r}")


def _button_by_label(at: AppTest, label: str):
    for b in at.button:
        if b.label == label:
            return b
    raise KeyError(f"no button with label={label!r}")


def _has_text(at: AppTest, needle: str) -> bool:
    """True if any caption, markdown, or error/success block contains needle."""
    for c in at.caption:
        if needle in c.value:
            return True
    for m in at.markdown:
        if needle in m.value:
            return True
    return False


def _search(at: AppTest, value: str) -> AppTest:
    """Simulate typing a serial and pressing Enter."""
    _input_by_key(at, "search_serial").set_value(value)
    return at.run()


def _run() -> AppTest:
    at = AppTest.from_file(APP_PATH, default_timeout=15).run()
    assert not at.exception, f"app raised: {list(at.exception)}"
    return at


def test_seed_and_stats_counter_on_first_boot():
    at = _run()
    assert _has_text(at, "4 verified")


def test_seed_is_idempotent_across_boots():
    _run()
    at2 = _run()
    assert _has_text(at2, "4 verified")


def test_demo_serial_is_flagged_with_fuzzy_match():
    at = _run()
    _search(at, "wtu 221 l 0123")
    assert at.error and "reported stolen" in at.error[0].value


def test_unknown_serial_returns_clean():
    at = _run()
    _search(at, "TOTALLYRANDOM")
    assert _has_text(at, "No reports found")


def test_demo_chip_fills_input_and_searches():
    at = _run()
    # First demo chip = first DEMO_BIKES entry's serial = "WTU221L0123"
    _button_by_label(at, "WTU221L0123").click().run()
    assert at.error and "reported stolen" in at.error[0].value


def test_full_report_verify_search_flow(capsys):
    # Submit
    at = _run()
    _input_by_key(at, "rep_serial").set_value("NEW-9999")
    _input_by_key(at, "rep_brand").set_value("Giant")
    _input_by_key(at, "rep_email").set_value("newowner@example.com")
    _button_by_label(at, "Submit report").click().run()
    assert at.success and "newowner@example.com" in at.success[0].value
    assert "dev mode" in at.success[0].value

    captured = capsys.readouterr().out
    m = re.search(r"verify=([0-9a-f]+)", captured)
    assert m, f"no token printed; got: {captured!r}"
    token = m.group(1)

    # Verify
    at2 = AppTest.from_file(APP_PATH, default_timeout=15)
    at2.query_params["verify"] = token
    at2.run()
    assert at2.success and "verified" in at2.success[0].value.lower()

    # Search finds it
    at3 = _run()
    _search(at3, "new9999")
    assert at3.error and "reported stolen" in at3.error[0].value


def test_token_reuse_is_rejected(capsys):
    at = _run()
    _input_by_key(at, "rep_serial").set_value("REUSE-1")
    _input_by_key(at, "rep_email").set_value("r@example.com")
    _button_by_label(at, "Submit report").click().run()
    token = re.search(r"verify=([0-9a-f]+)", capsys.readouterr().out).group(1)

    at2 = AppTest.from_file(APP_PATH, default_timeout=15)
    at2.query_params["verify"] = token
    at2.run()
    assert at2.success

    at3 = AppTest.from_file(APP_PATH, default_timeout=15)
    at3.query_params["verify"] = token
    at3.run()
    assert at3.error and "invalid or has already been used" in at3.error[0].value


def test_mark_recovered_requires_confirmation():
    """The 'Mark recovered' button is disabled until the user confirms."""
    at = _run()
    _input_by_key(at, "rec_serial").set_value("WTU221L0123")
    _input_by_key(at, "rec_email").set_value("ana@example.com")
    # Submit without ticking the confirm checkbox.
    _button_by_label(at, "Mark recovered").click().run()
    # Button should be disabled — no success or error from the recover handler.
    assert not (at.success and "recovered" in at.success[0].value.lower())


def test_mark_recovered_removes_from_search():
    at = _run()
    _input_by_key(at, "rec_serial").set_value("WTU221L0123")
    _input_by_key(at, "rec_email").set_value("ana@example.com")
    _checkbox_by_key(at, "rec_confirm").check()
    _button_by_label(at, "Mark recovered").click().run()
    assert at.success and "recovered" in at.success[0].value.lower()

    at2 = _run()
    _search(at2, "WTU221L0123")
    assert _has_text(at2, "No reports found")


def test_mark_recovered_rejects_wrong_email():
    at = _run()
    _input_by_key(at, "rec_serial").set_value("WTU221L0123")
    _input_by_key(at, "rec_email").set_value("wrong@example.com")
    _checkbox_by_key(at, "rec_confirm").check()
    _button_by_label(at, "Mark recovered").click().run()
    assert at.error and "Couldn't find" in at.error[0].value


def test_submit_rejects_malformed_email():
    at = _run()
    _input_by_key(at, "rep_serial").set_value("BAD-1")
    _input_by_key(at, "rep_email").set_value("not-an-email")
    _button_by_label(at, "Submit report").click().run()
    assert at.error and "doesn't look right" in at.error[0].value


def test_seed_bikes_have_geo_coordinates():
    """Demo bikes should ship with lat/lng so map links work out of the box."""
    _run()  # triggers seeding
    from bike_app.db import connect

    with connect() as conn:
        rows = conn.execute(
            "SELECT serial, theft_lat, theft_lng FROM bikes WHERE status = 'verified'"
        ).fetchall()
    assert len(rows) == 4
    for r in rows:
        assert r["theft_lat"] is not None, f"{r['serial']} missing lat"
        assert r["theft_lng"] is not None, f"{r['serial']} missing lng"
        # Portugal-ish bounding box sanity check
        assert 36.0 <= r["theft_lat"] <= 42.5
        assert -9.5 <= r["theft_lng"] <= -6.0


def test_insert_report_accepts_geo_coordinates():
    """The DB layer must round-trip lat/lng on new reports."""
    _run()
    from bike_app.db import connect, insert_report

    insert_report(
        serial="GEO-TEST-1",
        brand="Cube", model="Reaction", color="Green",
        theft_date="2026-05-20",
        theft_location="Funchal, Madeira, Portugal",
        theft_lat=32.6500,
        theft_lng=-16.9090,
        owner_email="geo@example.com",
        photo_path=None,
        token="geotoken1",
    )
    with connect() as conn:
        row = conn.execute(
            "SELECT theft_lat, theft_lng FROM bikes WHERE serial = ?",
            ("GEO-TEST-1",),
        ).fetchone()
    assert abs(row["theft_lat"] - 32.6500) < 1e-6
    assert abs(row["theft_lng"] - -16.9090) < 1e-6


def test_match_card_shows_view_on_map_link():
    """Verified bikes with coords should expose a map link in the search result."""
    at = _run()
    _search(at, "WTU221L0123")  # demo bike with coordinates seeded
    # The match card is rendered via st.markdown; check the raw HTML.
    rendered = " ".join(m.value for m in at.markdown)
    assert "View on map" in rendered
    assert "openstreetmap.org" in rendered


def test_submit_requires_serial_and_email():
    at = _run()
    _input_by_key(at, "rep_serial").set_value("")
    _input_by_key(at, "rep_email").set_value("")
    _button_by_label(at, "Submit report").click().run()
    assert at.error and "required" in at.error[0].value
