# SourceLens claim-check Worker

Cloudflare Worker that holds the Gemini API key and answers `POST /check {"claim": "..."}` with `{verdict, summary, sources}`. The landing page calls it so the key is never in the public HTML.

It calls Google's fast "flash-lite" Gemini models (`MODELS` in `src/index.js`, tried in order) with Google Search grounding. An alternative using Claude with web search is kept in `alt/anthropic.js` (untested against the live API; it needs an `ANTHROPIC_API_KEY` secret and replaces `src/index.js`).

## Deploy

```bash
npx wrangler secret put GEMINI_API_KEY   # key from aistudio.google.com
npx wrangler deploy
```

`CHECK_ENDPOINT` in `../index.html` points at the deployed URL. Set a spend limit for the key in Google AI Studio or Cloud billing.

## Local test

```bash
echo "GEMINI_API_KEY=your-key" > .dev.vars   # git-ignored
npx wrangler dev
curl -X POST http://localhost:8787 -H "Origin: http://localhost:8000" -H "Content-Type: application/json" -d '{"claim":"The Eiffel Tower is in Berlin."}'
```

## Behaviour

- Only the origins listed in `ALLOWED_ORIGINS` (`src/index.js`) are served.
- Claims over 600 characters are rejected. The claim text is never logged or stored by the Worker.
- The prompt requires a search every time. If the model skips it, the Worker retries once with the next model.
- Sources come from search grounding, not from links the model wrote. No sources means `NOT_YET_VERIFIED`, so some claims come back unverified with the lite models: in a 22 Nov test, 8 of 12 checkable claims got a sourced verdict, none of them wrong; 4 came back unverified.
- If a model is overloaded (500/503), the next model in `MODELS` is tried.
- Rate limit: 30 requests per minute per IP via the `RL` binding in `wrangler.toml`. Campus Wi-Fi and the class demo share one public IP, so 10 would block most of the room.
- Open item: check whether Google's Grounding with Google Search terms require displaying Search Suggestions; if so, return webSearchQueries and render them (see docs/FIX_PLAN.md T16c).
- Google may retain inputs under its API terms; the page says so.
