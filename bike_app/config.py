"""Central runtime configuration.

Every deployment knob the app reads from the environment lives here, so
there is a single place to look when configuring a release. Values are
read at call time (not import time) so tests can swap them per-test.
"""

import os
import re
from pathlib import Path

import streamlit as st

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def upload_dir() -> Path:
    """Directory for user-uploaded photos. Created on first use."""
    d = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def demo_mode() -> bool:
    """Seed demo reports and show demo serial chips. On unless DEMO_MODE=0."""
    return os.getenv("DEMO_MODE", "1") != "0"


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value.strip()))


def current_base_url() -> str:
    """Detect the public URL the visitor is actually using.

    Reads it from the request headers Streamlit exposes via st.context so
    that verification links work whether the app is on localhost, Streamlit
    Cloud, behind a proxy, etc. Falls back to the BASE_URL env var when no
    request context is available (e.g. AppTest).
    """
    try:
        headers = st.context.headers
        host = headers.get("Host") or headers.get("host")
        if host:
            proto = (
                headers.get("X-Forwarded-Proto")
                or headers.get("x-forwarded-proto")
                or ("http" if host.startswith("localhost") else "https")
            )
            return f"{proto}://{host}"
    except Exception:
        pass
    return os.getenv("BASE_URL", "http://localhost:8501")
