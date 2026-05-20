# 🚲 Stolen Bike Check

A single-page Streamlit app for checking whether a bike has been reported
stolen, and for owners to file new stolen-bike reports.

- **Check a bike** — search by frame serial number (spaces and punctuation
  are ignored).
- **Report stolen** — owners submit serial, brand/model/color, theft date
  and location, contact email, and an optional photo. Reports require an
  email verification click before they appear in searches.

Data is stored locally in SQLite at `data/bikes.db`; uploaded photos go
under `data/uploads/`. Both are gitignored.

### Run it locally

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Email delivery

The verification email uses whichever of these is configured (in order):

- `RESEND_API_KEY` — send via [Resend](https://resend.com)
  (`EMAIL_FROM` overrides the default `onboarding@resend.dev` sender).
- `SMTP_HOST` (+ optional `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`,
  `EMAIL_FROM`) — send via SMTP with STARTTLS.
- Neither set — the verification link is printed to the server log and
  shown in the UI, so you can verify reports without sending real email.

Set `BASE_URL` to the public URL of the app so verification links in
sent emails point to the right place (defaults to `http://localhost:8501`).
