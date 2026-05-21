"""Signed share links for the 'Selling this bike?' flow.

A clean search produces a verification URL that the seller can paste
into a marketplace listing (DBA, Blocket, Facebook Marketplace). The
URL carries an HMAC-signed timestamp so the landing page can show
'seller checked this on X' without us having to persist anything per
link. The actual stolen-or-not check on the landing page is always
done live against the DB, so a bike reported AFTER the link was minted
shows up as flagged — the URL is a pointer, not a snapshot.
"""

import hmac
import hashlib
import os
import time

# Override in production via env so links can't be forged by anyone with
# the source code.
SECRET = os.getenv(
    "CHECK_TOKEN_SECRET", "dev-secret-please-set-CHECK_TOKEN_SECRET"
).encode()


def _payload(serial: str, ts: int) -> bytes:
    return f"{serial.upper()}:{ts}".encode()


def make_check_token(serial: str, ts: int | None = None) -> str:
    """Produce a token that ties a serial to a 'checked at' timestamp."""
    ts = int(ts if ts is not None else time.time())
    sig = hmac.new(SECRET, _payload(serial, ts), hashlib.sha256).hexdigest()[:16]
    return f"{ts}.{sig}"


def verify_check_token(serial: str, token: str) -> int | None:
    """Return the timestamp encoded in the token if valid, else None."""
    if not token or "." not in token:
        return None
    ts_str, sig = token.split(".", 1)
    try:
        ts = int(ts_str)
    except ValueError:
        return None
    expected = hmac.new(SECRET, _payload(serial, ts), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected):
        return None
    return ts
