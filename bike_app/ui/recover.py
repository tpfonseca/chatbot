"""Mark-as-recovered modal dialog."""

import streamlit as st

from bike_app.db import mark_recovered
from bike_app.i18n import t


def open_recover_dialog() -> None:
    """Open the dialog with its title in the current language.

    st.dialog fixes the title at decoration time, so we decorate at call
    time instead of import time to keep it translatable.
    """
    st.dialog(t("tile_recover_title"))(_recover_dialog_body)()


def _recover_dialog_body() -> None:
    """Short modal: take down a verified stolen-bike report."""
    st.caption(t("recover_caption"))
    rec_serial = st.text_input(
        t("label_serial"), key="rec_serial",
        placeholder=t("ph_serial"),
    )
    rec_email = st.text_input(
        t("recover_email_label"), key="rec_email",
        placeholder=t("ph_email"),
    )
    rec_confirm = st.checkbox(t("recover_checkbox"), key="rec_confirm")
    if st.button(
        t("recover_submit"), type="primary",
        disabled=not rec_confirm, key="rec_submit",
    ):
        if not rec_serial.strip() or not rec_email.strip():
            st.error(t("err_required"))
        elif mark_recovered(rec_serial.strip(), rec_email.strip()):
            st.success(t("recover_success"))
        else:
            st.error(t("recover_error"))
