# SourceLens

A "Shazam for political claims": paste a post or claim and get a sourced verdict (True, False, Misleading, Not yet verified). Nothing is deleted. This repository is the landing page and market-experiment kit for Team 11 B, EDHEC Foresight & Strategic Design (Homework 2). It is a student prototype; the sample chips show curated verdicts, and pasted text is checked live by AI and can be wrong.

**Live page:** https://dansl5.github.io/EDHEC_sourcelens/

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole landing page (plain HTML, CSS and JS; no build step) |
| `method.html` | How verdicts are made, what we never do, and how to appeal a verdict |
| `privacy.html` | Privacy notes: analytics, forms, claim checker |
| `advisory.html` | War Game security advisory, a simulated crisis. Not linked from the page |
| `worker/` | Cloudflare Worker that holds the Gemini API key and powers the live claim checker (see `worker/README.md`) |
| `assets/` | Promo video, poster, favicon, link-preview card |
| `docs/` | Assignment brief, landing page audit, fix plan |
| `experiment/` | Market experiment one-pager, tracking links, analysis script, hallway-test script |

GitHub Pages serves the `main` branch from the repository root. Keep `.nojekyll`.

## How to edit

Edit the files and push to `main`; Pages redeploys in a minute or two. To test locally, run `python3 -m http.server` in this folder and open http://localhost:8000.

### Configuration (top of the `<script>` in `index.html`)

| Constant | Placeholder | Meaning |
|---|---|---|
| `GOATCOUNTER_CODE` | `sourcelens` | GoatCounter site code (dashboard: https://sourcelens.goatcounter.com) |
| `CHECK_ENDPOINT` | `https://sourcelens-check.sourcelens-team11.workers.dev/check` | URL of the deployed claim-check Worker. If it contained `{{`, the demo would use the curated sample verdicts only |
| `TEAM_EMAIL` | `hello@sourcelens.eu` | Contact email, display only. There is no mailbox behind it (the domain has no mail records) |

The forms are **count-only**: they never send or store anything. A valid submit fires one GoatCounter event per form per browser session, clears the fields and shows an honest prototype notice. If `GOATCOUNTER_CODE` contained `{{`, analytics would not load and no events, including sign-ups, would be counted.

## Where data lives

- **Form submissions:** the forms store nothing and send nothing. Sign-ups are GoatCounter events (`waitlist-submit-success`, `premium-submit-success`, `newsroom-pilot-submit`); no emails are collected. A hidden `_gotcha` field is a bot trap.
- **Visitors and events:** GoatCounter (cookieless, no banner needed).
- Credentials are never stored in this repository. Raw analytics exports stay out of the repo: `experiment/data/` is git-ignored.

- **Claim-checker text:** pasted claims go to the Worker and on to Google's Gemini API (with Google Search). The Worker does not log or store them. The API key is a Worker secret, never in this repo.

## Tracked events (GoatCounter)

`cta-hero-waitlist`, `cta-hero-newsroom`, `demo-check`, `demo-check-live` (a pasted claim sent to the live checker), `demo-live-true`, `demo-live-false`, `demo-live-misleading`, `demo-live-not-yet-verified`, `demo-live-error` (the outcome of a pasted claim sent to the live checker), `demo-chip-1` to `demo-chip-3`, `plan-click-citizen`, `plan-click-premium`, `plan-click-newsroom`, `plan-click-api`, `pilot-kind-newsroom`, `pilot-kind-platform` (the "We are a" choice on a pilot request), `waitlist-submit-success`, `premium-submit-success`, `newsroom-pilot-submit`, `video-play` (once per page view), `landing-<utm_source>` (once per page view when the link carries `utm_source`, e.g. `landing-linkedin`; `landing-test` marks test visits).

## Experiment kit

See `experiment/EXPERIMENT.md` (source of the one-pager), `experiment/links.md` (one tracking link per channel), `experiment/analyze.py` (funnel and Wilson intervals from the GoatCounter export), `experiment/hallway-script.md`.
