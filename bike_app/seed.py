"""Seed the local database with demo stolen-bike reports.

Used so a live demo of the app has data to search against.
"""

from bike_app.db import connect, normalize_serial

DEMO_BIKES = [
    {
        "serial": "WTU221L0123",
        "brand": "Trek",
        "model": "Domane SL 5",
        "color": "Matte black",
        "theft_date": "2026-05-02",
        "theft_location": "Cedofeita, Porto, Portugal",
        "theft_lat": 41.1547,
        "theft_lng": -8.6160,
        "owner_email": "ana@example.com",
    },
    {
        "serial": "WSBC602173456E",
        "brand": "Specialized",
        "model": "Allez Sport",
        "color": "Rocket red",
        "theft_date": "2026-04-12",
        "theft_location": "Príncipe Real, Lisbon, Portugal",
        "theft_lat": 38.7186,
        "theft_lng": -9.1497,
        "owner_email": "joao@example.com",
    },
    {
        "serial": "CT-9928 761K",
        "brand": "Cannondale",
        "model": "Topstone 4",
        "color": "Slate blue",
        "theft_date": "2026-04-30",
        "theft_location": "Baixa, Coimbra, Portugal",
        "theft_lat": 40.2110,
        "theft_lng": -8.4292,
        "owner_email": "miguel@example.com",
    },
    {
        "serial": "GNT-AVANCE2-7781",
        "brand": "Giant",
        "model": "Avance 2",
        "color": "White",
        "theft_date": "2026-05-15",
        "theft_location": "São Vítor, Braga, Portugal",
        "theft_lat": 41.5470,
        "theft_lng": -8.4220,
        "owner_email": "sofia@example.com",
    },
]


def seed_if_empty() -> int:
    """Insert demo reports if the bikes table has no rows. Returns rows added."""
    with connect() as conn:
        (count,) = conn.execute("SELECT COUNT(*) FROM bikes").fetchone()
        if count > 0:
            return 0
        for b in DEMO_BIKES:
            conn.execute(
                """
                INSERT INTO bikes (
                    serial, serial_normalized, brand, model, color,
                    theft_date, theft_location, theft_lat, theft_lng,
                    owner_email, status, verified_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'verified', datetime('now'))
                """,
                (
                    b["serial"],
                    normalize_serial(b["serial"]),
                    b["brand"],
                    b["model"],
                    b["color"],
                    b["theft_date"],
                    b["theft_location"],
                    b["theft_lat"],
                    b["theft_lng"],
                    b["owner_email"],
                ),
            )
        return len(DEMO_BIKES)
