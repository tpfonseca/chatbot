"""Shareable 'Bike Check' badges.

A successful clean search produces a signed verification URL plus a
downloadable PNG badge (with embedded QR code) that the seller can paste
into a marketplace listing. The badge image is just a hint — the URL
is the source of truth. When the buyer clicks or scans the QR, the
landing page re-checks the serial live against the DB, so a bike that
gets reported AFTER the seller made the badge still shows up as flagged.
"""

import hmac
import hashlib
import io
import os
import time

from PIL import Image, ImageDraw, ImageFont
import qrcode

from bike_app.i18n import t_for
from bike_app.util import human_date

# A seed for the HMAC. Override in production via env so badges can't be
# forged by anyone with the source code.
SECRET = os.getenv(
    "CHECK_TOKEN_SECRET", "dev-secret-please-set-CHECK_TOKEN_SECRET"
).encode()
if "CHECK_TOKEN_SECRET" not in os.environ:
    print(
        "[bike_app] CHECK_TOKEN_SECRET is not set — check tokens are signed "
        "with the public dev secret and can be forged. Set it before release.",
        flush=True,
    )


def _payload(serial: str, ts: int) -> bytes:
    return f"{serial.upper()}:{ts}".encode()


def make_check_token(serial: str, ts: int | None = None) -> str:
    """Produce a token that ties a serial to a 'checked at' timestamp."""
    ts = int(ts if ts is not None else time.time())
    sig = hmac.new(SECRET, _payload(serial, ts), hashlib.sha256).hexdigest()[:16]
    return f"{ts}.{sig}"


def verify_check_token(serial: str, token: str) -> int | None:
    """Return the timestamp encoded in the token if it's valid, else None."""
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


def _try_font(paths: list[str], size: int) -> ImageFont.ImageFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# Common font locations on Streamlit Cloud's Debian base.
_SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
_SANS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]


def generate_badge_png(
    serial: str, verification_url: str, checked_at: int, lang: str = "en"
) -> bytes:
    """Render a sharable PNG badge.

    Layout (1200x400 @ 2x for crisp display, scaled down to 600x200 in CSS):
      Left:   check icon, headline, serial, date
      Right:  QR code linking to the verification URL
    """
    W, H = 1200, 400
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Rounded border
    draw.rounded_rectangle(
        (2, 2, W - 3, H - 3), radius=36, outline=(210, 210, 215), width=3
    )

    # Fonts
    f_header = _try_font(_SANS_BOLD, 44)
    f_serial = _try_font(_MONO, 38)
    f_date = _try_font(_SANS, 28)
    f_footer = _try_font(_SANS, 22)

    pad = 56

    # Green check disc
    cx, cy, r = pad + 28, pad + 32, 32
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(36, 138, 61))
    # Draw the checkmark (3-point polyline)
    draw.line(
        [(cx - 14, cy + 2), (cx - 4, cy + 14), (cx + 16, cy - 12)],
        fill="white",
        width=6,
    )

    # Headline
    draw.text(
        (pad + 80, pad + 4), "Bike Check", fill=(29, 29, 31), font=f_header
    )

    # Serial
    draw.text(
        (pad, pad + 108), serial.upper(), fill=(29, 29, 31), font=f_serial
    )

    # Date
    draw.text(
        (pad, pad + 168),
        t_for(lang, "badge_checked", date=human_date(checked_at, lang)),
        fill=(110, 110, 115),
        font=f_date,
    )

    # Footer
    draw.text(
        (pad, H - pad - 12),
        t_for(lang, "badge_scan"),
        fill=(134, 134, 139),
        font=f_footer,
    )

    # QR code on the right
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=0,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_size = 280
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
    img.paste(qr_img, (W - pad - qr_size, (H - qr_size) // 2))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
