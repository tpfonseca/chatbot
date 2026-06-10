"""Email-verification landing view (?verify=TOKEN)."""

import streamlit as st

from bike_app.db import verify_token
from bike_app.ui.components import hero


def render_verify_view(token: str) -> None:
    ok = verify_token(token)
    hero()
    if ok:
        st.success("Report verified. It will now appear in searches.")
    else:
        st.error("This verification link is invalid or has already been used.")
    if st.button("Back to homepage", type="primary"):
        st.query_params.clear()
        st.rerun()
