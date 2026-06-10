"""Mark-as-recovered modal dialog."""

import streamlit as st

from bike_app.db import mark_recovered


@st.dialog("Mark a bike as recovered")
def recover_dialog() -> None:
    """Short modal: take down a verified stolen-bike report."""
    st.caption(
        "We'll take your report down so future searches don't show a false "
        "warning. We match on the serial and the email you used to report it."
    )
    rec_serial = st.text_input(
        "Serial number", key="rec_serial",
        placeholder="Frame serial number",
    )
    rec_email = st.text_input(
        "Email used in the original report", key="rec_email",
        placeholder="you@example.com",
    )
    rec_confirm = st.checkbox(
        "Yes, I have my bike back. Take the warning down.",
        key="rec_confirm",
    )
    if st.button(
        "Mark recovered", type="primary",
        disabled=not rec_confirm, key="rec_submit",
    ):
        if not rec_serial.strip() or not rec_email.strip():
            st.error("Serial number and email are required.")
        elif mark_recovered(rec_serial.strip(), rec_email.strip()):
            st.success(
                "Marked as recovered. The report no longer appears in searches."
            )
        else:
            st.error(
                "Couldn't find a verified report matching that serial and email. "
                "Double-check both, or contact us if your bike is still listed."
            )
