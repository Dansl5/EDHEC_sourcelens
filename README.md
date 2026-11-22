# SourceLens

A "Shazam for political claims": paste a post, link or screenshot and get a sourced verdict (True, False, Misleading, Not yet verified). Nothing is deleted. This repository is the landing page and market-experiment kit for Team 11 B, EDHEC Foresight & Strategic Design (Homework 2). It is a student prototype; the demo verdicts are illustrative, not live fact-checks.

**Live page:** https://dansl5.github.io/EDHEC_sourcelens/

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole landing page (plain HTML, CSS and JS; no build step) |
| `advisory.html` | War Game security advisory, a simulated crisis. Linked from the footer only |
| `worker/` | Cloudflare Worker that holds the Gemini API key and powers the live claim checker (see `worker/README.md`) |
| `assets/` | Promo video, poster, favicon, link-preview card |
| `experiment/` | Market experiment one-pager, tracking links, analysis script, hallway-test script |

GitHub Pages serves the `main` branch from the repository root. Keep `.nojekyll`.

## How to edit

Edit the files and push to `main`; Pages redeploys in a minute or two. To test locally, run `python3 -m http.server` in this folder and open http://localhost:8000.

### Configuration (top of the `<script>` in `index.html`)

| Constant | Placeholder | Meaning |
|---|---|---|
| `FORM_ENDPOINT` | `https://formspree.io/f/{{FORM_ID}}` | Formspree form URL. Also set it in each `<form action>` (3 forms) |
| `GOATCOUNTER_CODE` | `{{GOATCOUNTER_CODE}}` | GoatCounter site code |
| `CHECK_ENDPOINT` | `https://{{WORKER_URL}}/check` | URL of the deployed claim-check Worker. While it contains `{{`, the demo uses the four canned verdicts only |
| `TEAM_EMAIL` | `{{TEAM_EMAIL}}` | Contact email, shown in the error message. The privacy notes contain the same token in the HTML |

While `FORM_ENDPOINT` still contains `{{`, forms are in **test mode**: nothing is sent and they show "Test mode: sign-ups are not being saved yet." While `GOATCOUNTER_CODE` still contains `{{`, analytics is not loaded and no events are counted. `TEAM_EMAIL` gates nothing; it only appears in the error message and privacy notes. Replace the placeholders (search the repo for `{{`) before collecting data.

## Where data lives

- **Form submissions:** Formspree (waitlist, Premium fake door, newsroom pilot). Fields: `email`, `kind`, `plan_interest`, `utm_source`, `utm_medium`, `utm_campaign`, `page_variant`, `submitted_at`, `form_name`, plus the pilot form's `organisation`, `role`, `country`, `biggest_pain`. A hidden `_gotcha` field is a bot trap.
- **Visitors and events:** GoatCounter (cookieless, no banner needed).
- Credentials are never stored in this repository. Raw exports contain emails and must not be committed: `experiment/data/` is git-ignored.

- **Claim-checker text:** pasted claims go to the Worker and on to Google's Gemini API (with Google Search). The Worker does not log or store them. The API key is a Worker secret, never in this repo.

## Tracked events (GoatCounter)

`cta-hero-waitlist`, `cta-hero-newsroom`, `demo-check`, `demo-check-live` (a pasted claim sent to the live checker), `demo-chip-1` to `demo-chip-4`, `plan-click-citizen`, `plan-click-premium`, `plan-click-newsroom`, `plan-click-api`, `waitlist-submit-success`, `premium-submit-success`, `newsroom-pilot-submit`, `waitlist-submit-error`, `premium-submit-error`, `newsroom-pilot-submit-error` (a failed submission, named after the form), `video-play` (once per page view), `landing-<utm_source>` (once per page view when the link carries `utm_source`, e.g. `landing-linkedin`).

## Experiment kit

See `experiment/EXPERIMENT.md` (source of the one-pager), `experiment/links.md` (one tracking link per channel), `experiment/analyze.py` (funnel and Wilson intervals from the exports), `experiment/hallway-script.md`.
