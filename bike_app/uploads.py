"""Validated handling of user-uploaded photos.

Uploads are attacker-controlled input: we cap the size, allow only a
fixed set of extensions, and confirm the bytes actually decode as an
image before anything is written to disk. Stored filenames are random
hex, never derived from the user's filename.
"""

import io
import uuid
from pathlib import Path

from PIL import Image

from bike_app.config import upload_dir

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # keep in sync with server.maxUploadSize


def save_photo(filename: str, data: bytes) -> str:
    """Validate an uploaded photo and persist it; returns the stored path.

    Raises ValueError with a user-facing message if the file is too
    large, has an unsupported extension, or isn't a decodable image.
    """
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Photo is larger than 10 MB.")
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image type. Use JPG, PNG, or WebP.")
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception:
        raise ValueError("That file doesn't look like a valid image.")
    dest = upload_dir() / f"{uuid.uuid4().hex}{ext}"
    dest.write_bytes(data)
    return str(dest)
