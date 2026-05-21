# CLAUDE.md

Operating notes for future Claude sessions on this project.

## What this is

A Danish bike-theft registry. Two flows:

1. **Check** — Anyone enters a frame serial; the app says whether it's been
   reported stolen. A clean search produces a paste-ready snippet (with a
   signed verification URL) that sellers paste into DBA / Blocket listings.
2. **Report** — Owners file a stolen-bike report (serial, brand, color,
   when/where, email, optional photo). An email-verification click is
   required before the report appears in searches.

## Mission framing (don't lose this)

The Dutch have a cultural norm: serial numbers go in marketplace listings,
buyers expect them, the registry (Stop Heling) is normalised. Denmark
doesn't. **The goal is to seed that norm.** That's why:

- Clean-result copy reads "Help start a Danish norm: serials in every
  listing." — not "Sell your bike faster."
- The share card hands sellers a paste snippet in EN and DA, framed as a
  contribution to the norm rather than a personal benefit.
- We dropped the badge PNG (`bike_app/badge.py` → renamed to `share.py`)
  because DBA/Blocket listings are mostly text — an image asset added
  friction without much value. If reviving image badges, justify why.

When working on copy, **resist generic "trust" language**. Concrete: "Buyers
in the Netherlands already expect this." Vague: "Build trust."

## Architecture

- **Single-file Streamlit app**: `streamlit_app.py` is the entry point and
  contains all UI, CSS, and the report/recover/check views. Routing is
  query-param based: `?v=SERIAL&c=TOKEN` lands a buyer on the verification
  view; otherwise the home view.
- **SQLite** at `data/bikes.db` — single table `bikes` with `status`
  (`pending` | `verified` | `recovered`). Search only returns `verified`.
- **Signed share links** (`bike_app/share.py`): HMAC-SHA256 over
  `SERIAL:timestamp`, truncated to 16 hex chars. Tokens are stateless — we
  don't persist them. The landing page always re-checks the serial live
  against the DB, so a check minted *before* a theft report still shows red.
- **No badge PNGs, no QR codes.** Just paste-ready text in `st.code()`.

```
streamlit_app.py          UI + all views
bike_app/
  db.py                   SQLite schema, queries, rate-limit helper
  share.py                Signed share-link tokens (HMAC)
  email_utils.py          Resend / SMTP / dev-mode verification email
  geocode.py              Address autocomplete for the report form
  seed.py                 Demo bikes for first-boot
tests/test_app.py         End-to-end via streamlit.testing.AppTest
```

## Dev loop

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
pytest                       # 30 tests, all should be green
rm -rf data                  # nuke local DB to re-seed demo bikes
```

The `data/` directory and `data/uploads/` are gitignored. The DB seeds
itself on first boot via `seed_if_empty()`.

## Testing

We use `streamlit.testing.v1.AppTest` for full-app integration tests.
Helpers in `tests/test_app.py`:

- `_run()` — boot fresh app
- `_search(at, "SERIAL")` — drive the search box
- `_open_report_view(at)` — switch to the report-stolen view
- `_input_by_key(at, "rep_serial")` — locate widgets by `key=`
- `_button_by_label(at, "Submit report")` — locate by visible text
- `_has_text(at, "...")` — search rendered markdown

When you add UI, add tests in the same style. Don't unit-test
functions when an AppTest assertion can prove the same thing through the
real surface.

## Conventions

- **No badge PNGs / image generation.** If you find yourself reaching for
  Pillow, ask: would plain text work?
- **Serial normalisation is canonical via `db.normalize_serial`.** Always
  upper-case + strip non-alphanum before comparing or signing tokens.
- **Email match is case-insensitive** everywhere (recover flow, rate limit).
- **Rate limit reports at 3/email/24h.** Anything stricter triggers false
  positives; anything looser invites flooding.
- **The verification step is the trust gate** — only `status='verified'`
  rows show in search. Don't surface pending rows anywhere user-facing.
- **CSS lives in the `<style>` block at the top of `streamlit_app.py`.**
  Don't sprinkle `st.markdown(..., unsafe_allow_html=True)` style blocks
  throughout — keep all overrides in one place so they're greppable.
- **Streamlit's `emotion-cache-xxxx` class names rotate per release.**
  Don't pin to them. Target `data-testid` attributes and structural
  selectors (`[data-testid="stCode"] > div`).

## Coding style (project-specific)

- Default to **no comments**. Add one only when the *why* is non-obvious —
  a hidden constraint, a subtle invariant, a workaround.
- Never write what the code already says ("this function returns X").
- Never reference the PR / ticket / task in comments — that rots fast.
- Prefer editing existing files. Don't create new modules for small
  helpers; inline them.
- No backwards-compat shims. Cut directly. The project is pre-launch.

## Environment

- `CHECK_TOKEN_SECRET` — HMAC secret for share links. Override in prod.
- `BASE_URL` — public URL for verification email links. Defaults to the
  live request host via `_current_base_url()` (Streamlit `st.context`).
- `RESEND_API_KEY` *or* `SMTP_HOST` — email transport. Unset → dev mode
  prints the verification link inline.

## Recovery flow (recently hardened — read before touching)

Two-step, mirrors the report-verification flow:

1. `request_recovery(serial, email)` stamps a single-use token onto
   the matching verified row's `verification_token` column. Returns the
   token if a match exists, `None` otherwise — no info leak between
   "wrong email" and "no such serial."
2. Clicking `?recover=TOKEN` calls `complete_recovery(token)`, which
   sets status='recovered' and clears the token.

The dialog's "no match" branch shows the **same** success message as the
match branch ("if a verified report matches, check your inbox") so
probing emails doesn't expose which (serial, email) pairs exist. Both
branches go through the same UI path; only the actual email is gated.

We re-use the existing `verification_token` column because it's NULL
after the original report verification — so we can stamp a new token
on it for recovery without a schema change.

## Open lines of work (where to focus next)

Roughly ordered by leverage on the mission:

1. **Mobile testing beyond the share card.** Share card verified at
   390×844 (iPhone 13). The report form, the folium map widget, and the
   recover dialog haven't been mobile-checked. Real sellers will be on
   phones.
2. **Disposable-email defense.** Rate limit caps spam-per-email but not
   spam-by-rotating-emails. Block `mailinator.com`, `10minutewail.com`,
   etc. at submit. Maintain the blocklist as a constant; don't pull from
   a third-party service.
3. **Distribution.** Code is the easy part. The norm only takes hold if
   Danish cycling communities, DBA, Cyklistforbundet know about it.
4. **Production deployment.** Streamlit Community Cloud or Fly.io; point
   `bikecheck.dk` at it; set the secrets. Currently the share URLs use
   whichever host the request came in on, so production "just works"
   once the domain is live.

## Don'ts

- Don't add features the user didn't ask for. The Apple-style restraint
  in the UI is deliberate — bloat erodes trust.
- Don't add `try/except` or input validation at internal boundaries.
  Trust the code; validate at user-input edges only.
- Don't switch from SQLite to Postgres "for scale." The dataset is
  tiny and will stay tiny for the foreseeable future.
- Don't introduce a frontend framework. Streamlit + targeted CSS is the
  whole UI stack.
- Don't write CLAUDE.md updates as essays. Keep this file tight.
