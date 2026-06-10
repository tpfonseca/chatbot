# 🚲 Bike Check

A Streamlit app for checking whether a bike has been reported stolen,
and for owners to file new stolen-bike reports.

- **Check a bike** — search by frame serial number (spaces, dashes, and
  casing are ignored).
- **Report stolen** — owners submit serial, brand/model/color, theft date
  and geocoded location, contact email, and an optional photo. Reports
  require an email verification click before they appear in searches.
- **Mark recovered** — owners take their report down with the same
  serial + email.
- **Share a clean check** — after a clean search, sellers get a signed
  link and a QR badge PNG for their listing. The landing page always
  re-checks the serial live, so a badge can't go stale-green.
- **Four languages** — English, Swedish, Danish, and Norwegian. A picker
  sits on every view; the choice persists for the session and travels in
  `?lang=` on shared links. The verification email and the badge PNG are
  generated in the reporter's/seller's language too.

## Project layout

```
streamlit_app.py        Entry point — page config, init, view routing only
bike_app/
  config.py             All environment-driven settings in one place
  i18n.py               Translations (en/sv/da/no) and the t() helper
  db.py                 SQLite storage (reports, verification, recovery)
  seed.py               Demo data (only when DEMO_MODE is on)
  email_utils.py        Verification email via Resend / SMTP / dev fallback
  geocode.py            Nominatim geocoding with caching
  badge.py              Signed check tokens + QR badge PNG rendering
  uploads.py            Size/type/content validation for photo uploads
  util.py               Shared helpers (portable date formatting)
  ui/
    styles.css          The whole look and feel
    components.py       Shared building blocks (hero, match card, …) —
                        escapes all user-submitted values before HTML
    home.py             Search, results, share card, action tiles
    report.py           Report-a-stolen-bike view
    recover.py          Mark-as-recovered dialog
    landing.py          Share-link landing page (?v=SERIAL&c=TOKEN)
    verify.py           Email verification page (?verify=TOKEN)
tests/test_app.py       End-to-end AppTest suite + unit tests
```

Data is stored locally in SQLite at `data/bikes.db`; uploaded photos go
under `data/uploads/`. Both are gitignored.

## Run it locally

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Run the tests with `pip install pytest && python -m pytest tests/`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `BIKES_DB` | `data/bikes.db` | SQLite database path |
| `UPLOAD_DIR` | `data/uploads` | Uploaded photo directory |
| `DEMO_MODE` | on | Seed demo reports and show demo serial chips; set `0` to disable |
| `BASE_URL` | `http://localhost:8501` | Fallback public URL when no request context is available (links normally use the live request host) |
| `CHECK_TOKEN_SECRET` | dev secret | HMAC key signing share-link check tokens |
| `GEOCODER_USER_AGENT` | project UA | User-Agent sent to Nominatim |

### Email delivery

The verification email uses whichever of these is configured (in order):

- `RESEND_API_KEY` — send via [Resend](https://resend.com)
  (`EMAIL_FROM` overrides the default `onboarding@resend.dev` sender).
- `SMTP_HOST` (+ optional `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`,
  `EMAIL_FROM`) — send via SMTP with STARTTLS.
- Neither set — the verification link is printed to the server log and
  shown in the UI, so you can verify reports without sending real email.

## Release checklist

Before pointing real users at a deployment:

- [ ] Set `CHECK_TOKEN_SECRET` to a long random value — otherwise
  share-link tokens are signed with the public dev secret and can be
  forged (a warning is logged at startup if it's unset).
- [ ] Configure a real email provider (`RESEND_API_KEY` or `SMTP_HOST`)
  so verification links are actually delivered.
- [ ] Set `DEMO_MODE=0` so demo reports aren't seeded into the
  production database.
- [ ] Put the database and uploads on persistent storage (`BIKES_DB`,
  `UPLOAD_DIR`) — on ephemeral hosts like Streamlit Cloud, local files
  are lost on every restart.
