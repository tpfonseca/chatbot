"""Free, no-key geocoding via OpenStreetMap's Nominatim service.

Nominatim's usage policy asks for a descriptive User-Agent and a max of
~1 request/second. We cache results so repeat queries (e.g. the user
typing slowly) don't hammer the service.
"""

import json
import os
import urllib.parse
import urllib.request
from functools import lru_cache

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = os.getenv(
    "GEOCODER_USER_AGENT",
    "BikeCheckPrototype/1.0 (https://github.com/tpfonseca/chatbot)",
)


@lru_cache(maxsize=1024)
def geocode(query: str) -> tuple[tuple[str, float, float], ...]:
    """Return up to 5 candidate places for a free-text query.

    Each candidate is (display_name, lat, lng). Returns () on any error
    or for queries shorter than 3 chars (autocomplete shouldn't fire on
    tiny inputs).
    """
    q = (query or "").strip()
    if len(q) < 3:
        return ()
    params = urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": "5", "addressdetails": "0"}
    )
    req = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return ()
    return tuple(
        (d["display_name"], float(d["lat"]), float(d["lon"])) for d in data
    )
