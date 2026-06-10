"""Email-verification landing view (?verify=TOKEN)."""

import streamlit as st

from bike_app.db import verify_token
from bike_app.i18n import clear_query_params_keep_lang, t
from bike_app.ui.components import hero


def render_verify_view(token: str) -> None:
    ok = verify_token(token)
    hero()
    if ok:
        st.success(t("verify_ok"))
    else:
        st.error(t("verify_bad"))
    if st.button(t("back_home"), type="primary"):
        clear_query_params_keep_lang()
        st.rerun()
