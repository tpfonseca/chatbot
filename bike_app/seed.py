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
        "theft_location": "Porto, Cedofeita",
        "owner_email": "ana@example.com",
    },
    {
        "serial": "WSBC602173456E",
        "brand": "Specialized",
        "model": "Allez Sport",
        "color": "Rocket red",
        "theft_date": "2026-04-12",
        "theft_location": "Lisbon, Príncipe Real",
        "owner_email": "joao@example.com",
    },
    {
        "serial": "CT-9928 761K",
        "brand": "Cannondale",
        "model": "Topstone 4",
        "color": "Slate blue",
        "theft_date": "2026-04-30",
        "theft_location": "Coimbra, Baixa",
        "owner_email": "miguel@example.com",
    },
    {
        "serial": "GNT-AVANCE2-7781",
        "brand": "Giant",
        "model": "Avance 2",
        "color": "White",
        "theft_date": "2026-05-15",
        "theft_location": "Braga, São Vítor",
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
                    theft_date, theft_location, owner_email,
                    status, verified_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'verified', datetime('now'))
                """,
                (
                    b["serial"],
                    normalize_serial(b["serial"]),
                    b["brand"],
                    b["model"],
                    b["color"],
                    b["theft_date"],
                    b["theft_location"],
                    b["owner_email"],
                ),
            )
        return len(DEMO_BIKES)
