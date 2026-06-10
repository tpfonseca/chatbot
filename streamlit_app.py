"""Bike Check — entry point.

Thin router only. Views live in bike_app/ui/, business logic in the
other bike_app modules. The order matters: query-param deep links
(?verify=…, ?v=…) short-circuit before the session-state view router.
"""

import streamlit as st

from bike_app.config import demo_mode
from bike_app.db import init_db
from bike_app.i18n import init_language
from bike_app.seed import seed_if_empty
from bike_app.ui.components import inject_styles, language_picker
from bike_app.ui.home import render_home_view
from bike_app.ui.landing import render_landing_view
from bike_app.ui.report import render_report_view
from bike_app.ui.verify import render_verify_view

st.set_page_config(
    page_title="Bike Check.",
    page_icon="🚲",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_db()
if demo_mode():
    seed_if_empty()

inject_styles()
init_language()
language_picker()

params = st.query_params
if "verify" in params:
    render_verify_view(params["verify"])
    st.stop()

if "v" in params:
    render_landing_view(params["v"], params.get("c", ""))
    st.stop()

if st.session_state.get("view") == "report":
    render_report_view()
    st.stop()

render_home_view()
