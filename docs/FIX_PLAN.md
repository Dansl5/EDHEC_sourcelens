# Landing page fix plan (for implementers)

Source: [LANDING_PAGE_AUDIT.md](LANDING_PAGE_AUDIT.md). Requirements: [ASSIGNMENT.md](ASSIGNMENT.md). Deadline: **Mon 23 Nov 2026, 23:59**.

## Goal

The page must **look and behave like a real pre-launch product**:
- analytics counts visits and clicks;
- the contact email is shown;
- forms accept submissions and confirm them.

It stays a prototype:
- **nothing is emailed to anyone**;
- **no submitted personal data is stored or sent anywhere**;
- a submission is recorded only as an anonymous analytics event ("count-only").

## Rules for whoever implements this

1. The API agent's work is committed and live (`8524be6`, live claim checker). Start from `main` at or after that commit. Run `git status` first; if there are uncommitted changes you did not make, stop and ask.
2. The claim checker is now in scope: tasks T12–T16. **Change `worker/src/index.js` only in T16.** Deploying the Worker is a human step (H5): never run `wrangler deploy` yourself.
3. Do the tasks in order and **commit after each task** with the message given. End every commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, or with whatever attribution line your own environment instructs. **Do not push** until the user says so.
4. Plain HTML/CSS/JS, no build step, no new libraries. Keep the existing style: compact CSS, CSS custom properties, `$()` helper.
5. User-visible copy: British English, short sentences, no exclamation marks except where given, no invented statistics, testimonials, user counts, logos or "most popular" badges.
6. After all tasks, run the checks in **T17**. Report each check as pass/fail with evidence.

## Decisions already made (do not re-open)

| Decision | Value |
|---|---|
| Form handling | Count-only. On a valid submit: show success, fire one GoatCounter event per form per browser session, clear the fields. No `fetch`, no Formspree, no `mailto`. |
| Contact email shown on the site | `hello@sourcelens.eu`. The domain has no DNS records, so mail to it goes nowhere. Do not use `sourcelens.io` or `sourcelens.app`: they belong to someone else. |
| Analytics | GoatCounter (cookieless). The user creates the account and gives the site code (H1). |
| Post-submit message | Realistic confirmation, then a one-sentence honest disclosure that this is a student prototype and nothing was stored. Required because we tell no one a falsehood about their data. Wording in T3. |
| "How we'll decide" section | Removed from the page. The decision rule lives in `experiment/EXPERIMENT.md` only. |
| Simulated War Game advisory | Unlinked from the page footer. `advisory.html` stays in the repo and is listed in the README. |
| Live checker | Stays on. Pasted text goes to the Worker; sample chips show curated verdicts, each with a real, working source link. No invented signals. |
| "No source, no verdict" rule | Kept. An unsourced answer is shown as Not yet verified, with a tip to rephrase, never as the model's unsourced opinion. |

### Proposed prices (the team may edit these numbers in T6; use them as written unless told otherwise)

| Tier | Price and terms |
|---|---|
| Citizens | €0, 10 checks a day |
| Premium | €3.99 / month or €39.90 / year (2 months free), VAT included, 30-day free trial without a card, cancel anytime |
| Newsrooms | Regional €300 / month (1 region, 3 seats); National €1,000 / month (all regions, 10 seats); excl. VAT, billed monthly; free concierge pilot first |
| Platforms (API) | From €25 per 1,000 checks; election monitoring package from €15,000 per election; excl. VAT |

## Human steps (the user does these; implementers cannot)

- **H1. GoatCounter.**
  1. Sign up free at goatcounter.com and pick a site code (for example `sourcelens`).
  2. Under Settings, set the site's domain to `dansl5.github.io`.
  3. Give the code to the implementer for T1.
- **H2. Exclude your own visits.** Every team member, in each browser they use, opens the live page and runs `localStorage.setItem('skipgc','t')` in the developer console once.
- **H3. Review prices.** Check the proposed prices above before T6, or accept them.
- **H4. Push.** Push once T17 passes; GitHub Pages redeploys in about 2 minutes. Then repeat the live checks in T17 on `https://dansl5.github.io/EDHEC_sourcelens/`.
- **H5. Deploy the Worker after T16.** From `worker/`, run `npx wrangler deploy` while logged in to the team's Cloudflare account. Then check:
  - in Google AI Studio, that the key's quota and spend cap cover a class demo (about 30 people checking at once from one network);
  - Google's current terms for Grounding with Google Search, on whether the page must show Google "Search Suggestions" (see T16c).

---

## T1. Configuration constants

File `index.html`, at the top of the `<script>`:

- Delete the `FORM_ENDPOINT` line.
- Set `const GOATCOUNTER_CODE="<code from H1>";`. If H1 is not done yet, leave `"{{GOATCOUNTER_CODE}}"` and note it in your report: analytics then stays off, and that is the only remaining placeholder.
- Set `const TEAM_EMAIL="hello@sourcelens.eu";`.
- Keep `configured()`; it is still used for `GOATCOUNTER_CODE` and `CHECK_ENDPOINT`.

**Accept:** `grep -n "{{" index.html` shows nothing, or only `GOATCOUNTER_CODE` if H1 is pending.

Commit: `Config: contact email, remove form endpoint`

## T2. Count-only form handling

File `index.html`.

**2a. Form tags.** On all three forms (`#pilot`, `#wl`, and the Premium dialog form), remove the `action="…formspree…"` and `method="POST"` attributes. Keep `id`, `data-form`, `data-success`, `data-success-event`, `data-loading`.

**2b. Hidden fields.** Remove every hidden input named `form_name`, `plan_interest`, `utm_source`, `utm_medium`, `utm_campaign`, `page_variant`, `submitted_at`, and the Premium form's `kind` hidden input. Keep the `.hp` honeypot blocks.

**2c. JavaScript.**

- Delete:
  - the line `document.querySelectorAll('input[name^="utm_"]')…`;
  - the old `setStatus`;
  - the whole `async function submitForm…`;
  - the `sl:failed` listener line.
- Keep `const params=…` only if something else still uses it; otherwise delete it too.
- Insert in place of the deleted code:

```js
/* Forms: count-only prototype. Nothing is sent or stored. A valid submit records one analytics event per form per browser session. */
const NOTICE="SourceLens is a prototype by a student team at EDHEC Business School, testing whether people want it: we have not stored your details and will not contact you.";
function setStatus(f,cls,msg){const el=f.querySelector(".status");el.className="status "+cls;el.textContent=msg;}
function once(k){try{if(sessionStorage.getItem(k))return false;sessionStorage.setItem(k,"1");}catch(e){}return true;}
function submitForm(e){
  e.preventDefault();
  const f=e.currentTarget, btn=f.querySelector('button[type="submit"]');
  if(f.dataset.busy||btn.disabled)return;
  if(f.elements["_gotcha"]&&f.elements["_gotcha"].value)return;
  f.dataset.busy="1"; btn.disabled=true; btn.textContent=f.dataset.loading||"Joining…"; setStatus(f,"info","");
  setTimeout(()=>{
    if(once("sl-"+f.dataset.form)){
      f.dispatchEvent(new CustomEvent("sl:submitted",{bubbles:true}));
      if(f.dataset.form==="newsroom-pilot"&&f.elements.kind)track("pilot-kind-"+f.elements.kind.value.toLowerCase());
    }
    f.querySelectorAll('input:not([type=hidden]),textarea').forEach(i=>{i.value="";});
    btn.textContent="Done"; setStatus(f,"ok",f.dataset.success);
    const n=document.createElement("p"); n.className="privacy"; n.textContent=NOTICE; f.querySelector(".status").after(n);
    delete f.dataset.busy;
  },700);
}
document.querySelectorAll("form[data-form]").forEach(f=>f.addEventListener("submit",submitForm));
```

The existing listener `document.addEventListener("sl:submitted",…)` stays: it fires the `data-success-event` analytics event.

**2d. Plan buttons.** The `[data-plan]` click handler references `plan_interest`. Replace its body with:

```js
document.querySelectorAll("[data-plan]").forEach(a=>a.addEventListener("click",()=>{
  const f=$(a.dataset.form); if(!f)return;
  if(a.dataset.kind&&f.elements.kind&&f.elements.kind.tagName==="SELECT")f.elements.kind.value=a.dataset.kind;
  setTimeout(()=>{const el=f.querySelector("input:not([type=hidden]):not([name=_gotcha]),select,textarea");if(el)el.focus({preventScroll:true});},400);
}));
```

**2e. JavaScript off.** Without JS, a form without `action` would GET-submit and put the email in the URL. Add this CSS:

```css
html:not(.js) form[data-form] button[type=submit]{display:none}
```

Then add `<noscript><p class="privacy">Turn on JavaScript to sign up.</p></noscript>` right after each form's submit button.

**Accept:**
- `grep -n "formspree\|fetch(FORM" index.html` shows nothing.
- Submitting the waitlist with an empty or invalid email shows the browser's validation and nothing else.
- A valid email shows the success text plus the notice, the field is cleared, and the button reads "Done".
- A second submit in the same tab after a reload fires no second event (check `sessionStorage`).

Commit: `Forms: count-only submissions with one analytics event per session`

## T3. Privacy and success copy

File `index.html`.

- Replace each of the three `<p class="privacy">…{{TEAM_EMAIL}}.</p>` paragraphs with:
  `<p class="privacy">We use cookieless analytics and never sell or share your data. Questions: <a href="mailto:hello@sourcelens.eu">hello@sourcelens.eu</a>. <a href="privacy.html">Privacy</a></p>`
- Set `data-success` on each form:
  - waitlist: `You're on the list.`
  - Premium: `You're on the Premium priority list.`
  - pilot: `Thanks, your pilot request is in.`

  The honest notice from T2 is appended after these automatically.

**Accept:**
- No `{{` left in visible text.
- Each success message is one short sentence, followed by the notice.

Commit: `Privacy notes: real contact address; honest post-submit notice`

## T4. Structure, navigation and hero CTAs

File `index.html`.

1. **Delete** the whole `<section id="decide">…</section>`.
2. **Reorder** `<main>` to: `#video` → benefits section → `#pricing` → `#waitlist` → `#newsrooms`. Move the sections; do not rewrite them here.
3. **Nav** (`#navlinks`) becomes: Demo, Video, Pricing, Waitlist, Newsrooms, in that order.
4. **Hero CTAs.** Replace the ghost button `<a class="btn ghost" href="#newsrooms" …>Newsroom pilots</a>`. Delete it from `.cta`, and add directly after the `.cta` div:
   ```html
   <p class="b2b">Newsroom or fact-checker? <a href="#newsrooms" data-track="cta-hero-newsroom" data-plan="newsroom-pilot" data-form="pilot" data-kind="Newsroom">Request a free pilot →</a></p>
   ```
   Add the CSS:
   ```css
   .b2b{margin-top:14px;font-size:15px;opacity:.9}
   .b2b a{font-weight:700;text-underline-offset:3px}
   ```
   `.btn.ghost` CSS may stay; delete it if it is now unused.

**Accept:**
- `grep -c 'id="decide"' index.html` is 0.
- Section order in the DOM is video, benefits, pricing, waitlist, newsrooms.
- Every nav link scrolls to an existing id.

Commit: `Layout: drop public decision band, waitlist before newsrooms, single hero CTA`

## T5. Waitlist form

File `index.html`, `#waitlist`.

- Replace the intro paragraph with:
  `<p>Join free and get early access to the SourceLens app and browser extension when they open in your country.</p>`
- Remove the `I am a` label and its `<select id="kind">`. Add `<input type="hidden" name="kind" value="Citizen">`. B2B visitors use the pilot form.
- The plan button "Join free" (Citizens card) keeps `data-form="wl"`. Remove its `data-kind` attribute.

**Accept:**
- The waitlist form has exactly one visible field (email) and one button.
- The pilot form still has its "We are a" select.

Commit: `Waitlist: citizens only, state what joining gets you`

## T6. Pricing (brief: tiers, feature allocations, billing logic)

File `index.html`, `#pricing`. Replace the four `.plan` cards and the `.fine` paragraph with the block below. Keep every existing `data-track`, `data-plan`, `data-form`, `id="open-premium"` and class name.

The featured border (`plan feat`) moves from Newsrooms to Premium.

```html
<div class="plan"><span class="who">Citizens</span><div class="price">€0</div><p class="terms">Free forever</p>
  <ul><li>10 checks a day</li><li>Verdicts with their sources</li><li>Shareable verdict cards</li><li>App and browser extension at launch</li></ul>
  <a class="btn" href="#waitlist" data-plan="citizen" data-form="wl" data-track="plan-click-citizen">Join free</a></div>
<div class="plan feat"><span class="who">Premium</span><div class="price">€3.99 <small>/ month</small></div><p class="terms">or €39.90 / year, 2 months free</p>
  <ul><li>Unlimited checks</li><li>Full check history, exportable</li><li>Priority review of unverified claims</li><li>Everything in Citizens</li></ul>
  <button class="btn" type="button" id="open-premium" data-track="plan-click-premium">Start 30-day free trial</button>
  <p class="terms">No card needed for the trial. Cancel anytime.</p></div>
<div class="plan"><span class="who">Newsrooms</span><div class="price">€300 <small>/ month</small></div><p class="terms">Regional: 1 region, 3 seats</p>
  <ul><li>National: €1,000 / month, all regions, 10 seats</li><li>Verification dashboard</li><li>Claim alerts for your region</li><li>Free concierge pilot first</li></ul>
  <a class="btn" href="#newsrooms" data-plan="newsroom-pilot" data-form="pilot" data-kind="Newsroom" data-track="plan-click-newsroom">Request a free pilot</a></div>
<div class="plan"><span class="who">Platforms and apps</span><div class="price">€25 <small>/ 1,000 checks</small></div><p class="terms">Volume discounts above 1M checks</p>
  <ul><li>Same engine via API</li><li>Election monitoring package from €15,000 per election</li><li>Supports DSA systemic-risk work</li></ul>
  <a class="btn" href="#newsrooms" data-plan="api" data-form="pilot" data-kind="Platform" data-track="plan-click-api">Talk to us about the API</a></div>
```

After `.plans`:

```html
<p class="fine">Consumer prices include VAT. Business prices exclude VAT, are billed monthly, and annual contracts are available. Citizens stay free: only 17% of people across 20 countries pay for online news (<a href="https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/dnr-executive-summary" target="_blank" rel="noopener">Reuters Institute Digital News Report 2026</a>).</p>
```

CSS to add:

```css
.plan .terms{font-size:13.5px;color:var(--muted);margin:0}
```

Remove the text "Prices are hypotheses we are testing with a Van Westendorp survey" and "Pilot pricing range…". Neither may remain anywhere on the page.

**Accept:**
- Each card states its price, unit and period.
- Free shows its cap (10/day), and Premium shows annual, trial and cancellation terms.
- B2B cards name their price drivers. The fine print states VAT and billing.
- At 375 px the cards stack with no horizontal scroll.

Commit: `Pricing: feature caps, billing terms, B2B price drivers`

## T7. Copy that overclaims (non-checker parts only)

File `index.html`.

| Where | Replace with |
|---|---|
| Hero lede `<p class="lede">` | `Paste a post or claim. SourceLens checks it against web sources in seconds and shows you where the answer comes from. Nothing is deleted and nobody decides what you may read.` |
| Benefit 1 (`Instant check`) paragraph | `Paste a post and get a verdict in seconds, with its sources attached. Links and screenshots come with the app.` |
| Hero `.tag` | `Independent · No government or party funding · <a href="method.html">Published method</a>`. Give the link `color:inherit;text-underline-offset:3px` |
| Benefit 2 (`Pre-share warning`) paragraph | `With the browser extension, SourceLens warns you before you share a claim already rated false.` |
| Benefit 2 pain label | `For: fakes that spread fast` |
| Benefit 3 paragraph | `Nothing is deleted. Every verdict is labelled, sourced and open to appeal. <a href="method.html">Read our method</a>.` |
| Benefits section eyebrow `Core benefits` | `For people who share political news` |
| Video section text `<p>` | Keep it as it is |

**Accept:** `grep -n "link or screenshot" index.html` returns nothing. The sample verdicts in `const S=[` are handled in T13; do not edit them here.

Commit: `Copy: link the published method, no present-tense claims for unbuilt features`

## T8. Method and privacy pages, footer

**8a. New file `method.html`.** Copy the `<head>` of `index.html`, then change:
- the `<title>` to `How SourceLens checks a claim`;
- the description to match;
- `og:url`;
- the `<style>` to only `:root` tokens, both dark-mode blocks, the base rules (`*`, `body`, `.wrap`, `h1,h2,h3`, `h2`, `h3`, `p`, `.eyebrow`, `section`, `a`), `.band`, `.nav`, `.logo`, `.logo span`, `.nav a`, and `footer` rules.

No script except the one-line `js` class script.

Body:
- a `.band` header with the logo linking to `./`, plus a "Back to SourceLens" link;
- then a `<main class="wrap">` with these sections, each an `h2` plus 2–4 short paragraphs or list items. Write the content from the facts below and invent nothing else.

1. **What a verdict means.** Four labels: True (reliable sources clearly confirm it); False (they clearly contradict it); Misleading (partly true, overstated, or missing key context); Not yet verified (no reliable source found, or not a checkable factual claim).
2. **Where sources come from.** Every verdict links the sources it is based on. Sources come from the search results the checker used, never from links it wrote itself. No source means no True/False verdict.
3. **What we never do.** We never delete or hide posts, and never rate opinions, parties or candidates. We take no government or party funding.
4. **AI and its limits.** Verdicts are produced by an AI model that searches the web, and can be wrong. Check the sources before you share.
5. **Appeals.** Anyone can ask us to review a verdict. Email `hello@sourcelens.eu` with the claim and why you think the verdict is wrong; a person reviews every appeal. (`id="appeals"`)

**8b. New file `privacy.html`.** Same skeleton. Sections:
- **What we collect:** cookieless visit statistics (GoatCounter: pages viewed, approximate country, browser type; no cookies, no cross-site tracking).
- **Sign-up forms:** in this prototype stage, form entries are not stored or sent anywhere.
- **Claim checker:** text you paste is sent to our checker and to Google's Gemini API with Google Search to produce a verdict. We do not store it; Google may retain it under its API terms. Do not paste personal data.
- **Contact:** hello@sourcelens.eu.

  The claim-checker paragraph must match the wording of the `#demo` note after T14.

**8c. Footer in `index.html`.** Replace the `<footer>…</footer>` content with:

```html
<footer><div class="wrap"><span>© 2026 SourceLens · A student venture from EDHEC Business School</span><span class="flinks"><a href="method.html">Method</a> · <a href="method.html#appeals">Appeals</a> · <a href="privacy.html">Privacy</a> · <a href="mailto:hello@sourcelens.eu">hello@sourcelens.eu</a></span></div></footer>
```

Use the same footer on both new pages.

**Accept:**
- Both pages render in light and dark mode and at 375 px with no horizontal scroll.
- Every footer link resolves.
- `index.html` no longer links `advisory.html`.

Commit: `Add method and privacy pages; product footer`

## T9. Accessibility contrast

File `index.html` (and the copied tokens in the two new pages).

- In the light `:root`: `--terra:#a4532d`. This gives 4.9:1 on paper and 5.5:1 on white; the old value was 3.5:1.
- `.btn.primary{background:#a4532d;color:#fff}`.
- The two dark-mode rules that set `.demo .btn{background:#c4693f}` change to `#a4532d`.
- Leave the dark-mode `--terra` (`#e08a5f`) unchanged.
- Leave the hero eyebrow on navy (`#e0a07e`, 5.8:1) unchanged.

**Accept:** run this in the browser console on the page and get both values ≥ 4.5:

```js
function L(h){const c=h.match(/\w\w/g).map(x=>parseInt(x,16)/255).map(v=>v<=.03928?v/12.92:((v+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]}
function C(a,b){const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
[C('a4532d','ffffff'),C('a4532d','f7f4ef')]
```

Commit: `Contrast: darker terracotta for CTA and labels (WCAG AA)`

## T10. Mobile hero and page metadata

File `index.html`.

- In `@media (max-width:520px)` add:
  ```css
  .hero{padding-block:24px 48px;gap:32px}
  .hero .lede{font-size:18px;margin-top:14px}
  .hero .tag{font-size:13.5px}
  ```
- `<title>`: `SourceLens: check political claims before you share`.

**Accept:** at 375×812, run `document.querySelector('#demo').getBoundingClientRect().top` on load. It must be ≤ 640; it was 690. If it is not, also reduce `.cta` `margin-top` to 20px on mobile.

Commit: `Mobile: bring the checker closer to the fold; descriptive title`

## T11. Analysis script and docs follow count-only

**11a. `experiment/analyze.py`.** Sign-ups now come from GoatCounter events, not a Formspree export.

- Make `--forms` optional (`default=None`). When it is absent, skip form parsing entirely.
- In `analyse()`, count sessions per channel from events:
  - `waitlist-submit-success` → `wl`;
  - `premium-submit-success` → `pp`;
  - `newsroom-pilot-submit` → `pil`.

  Store them in `channels[chan(s)]` as sets, like `demo`. In `build_table`, read `wl`, `pp` and `pil` from `channels` when `--forms` is absent, otherwise from `forms`, as now.
- Exclude every session whose channel is `test` (from `landing-test`).
- Update the module docstring: inputs, the count-only explanation, and exclusion via the `skipgc` setting plus `?utm_source=test`.
- Keep the Wilson intervals, thresholds and the SVG exactly as they are.

Check it with a small fake CSV in the scratch or `experiment/data/` folder (git-ignored). Never commit data. The CSV should have 10 sessions, 2 with `waitlist-submit-success`, 1 with `landing-test`. The output must show 2 of 9 for the waitlist.

**11b. `README.md`.**
- Configuration table: remove the `FORM_ENDPOINT` row; set `TEAM_EMAIL` to `hello@sourcelens.eu` (described as display only, no mailbox); state count-only.
- "Where data lives": forms store nothing; sign-ups are GoatCounter events.
- Events list: remove the three `*-submit-error` events; add `pilot-kind-newsroom` and `pilot-kind-platform`.
- Files table: add `method.html`, `privacy.html` and `docs/`.

**11c. `experiment/EXPERIMENT.md`, section 3 (Method).** Replace "team visits, tests and duplicate emails are excluded" with: "Sign-ups are counted as one analytics event per form per browser session; no emails are collected. Team browsers are excluded with GoatCounter's skipgc setting; test visits use utm_source=test." Do not touch results sections.

**11d. `experiment/links.md`.** Add a `test` row: `https://dansl5.github.io/EDHEC_sourcelens/?utm_source=test`. Owner: everyone, for checks.

Commit: `Experiment kit: count sign-ups from analytics events (count-only forms)`

Also add `demo-live-true`, `demo-live-false`, `demo-live-misleading`, `demo-live-not-yet-verified` and `demo-live-error` to the README events list (they come from T12h).

## T12. Checker interaction and states

File `index.html`: the `#demo` markup, the `.demo` / `.scan` / `.vhead` CSS, and `runLive()` / `run()`.

Measured on 22 Nov: live checks take a median of about 4 s and a maximum of 14 s, longer when the Worker retries. During that wait the page shows a full orange bar and an unchanged button, so it looks frozen.

**12a. Loading state.**
- While a live check runs: the button text is `Checking…` (restore `Check this claim` in `finally`), and `#demo` gets `aria-busy="true"`.
- The bar becomes indeterminate: add class `busy` to `.scan` and this CSS:
  ```css
  .scan.busy i{width:35%!important;animation:scan 1.1s ease-in-out infinite;transition:none}
  @keyframes scan{from{transform:translateX(-100%)}to{transform:translateX(290%)}}
  @media (prefers-reduced-motion:reduce){.scan.busy i{animation:none;width:100%!important;opacity:.5}}
  ```
- Remove `busy` when the result arrives.
- Add `<p id="vstatus" class="sr-only" aria-live="polite"></p>` inside `#demo`. Set it to `Checking the claim…`, then to `Verdict: <label>`. Add `.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}`.

**12b. Empty input.** In `run()`, if `txt` is empty: do not show a verdict and do not animate. Put `Paste a claim to check first.` in a small `<p id="vhint" class="note">` under the textarea, and focus the textarea. Clear the hint on the next run.

**12c. Input limits.**
- Add `maxlength="600"` to `#claim`.
- Add under the textarea: `<p class="note" id="vtip">Works best with one specific claim: who did what, and when.</p>`.

**12d. Timeout.** Change the abort timer from `15000` to `25000`. On abort (`e.name==="AbortError"`), show NOT YET VERIFIED with `This one took too long. Try a shorter, more specific claim.`

**12e. Verdict header on phones.** At 375 px, "NOT YET VERIFIED" and the time label wrap into a cramped two-column block. Add `.vhead{flex-wrap:wrap;gap:2px 12px}` and `.vhead small{font-size:12.5px}`.

**12f. Duplicate label.** Delete `meta.push("AI-generated, can be wrong");`. The header already says "AI-generated · verify before sharing".

**12g. Layout shift.** On desktop, `.hero` uses `align-items:center`, so the headline jumps down when the verdict card grows. Change it to `align-items:start`.

**12h. Outcome analytics.** After a live result, call `track("demo-live-"+(d.verdict||"error").toLowerCase().replace(/_/g,"-"))`. In the `!res.ok` and `catch` branches, call `track("demo-live-error")`. This lets the report state the checker's hit rate from real visitors.

**Accept:**
- Pasting a new claim shows `Checking…` and a moving bar until the verdict arrives.
- An empty box shows the hint and no verdict.
- At 375 px the verdict header label sits on one line, with the time label wrapping below it.

Commit: `Checker: loading state, empty-input hint, longer timeout, outcome events`

## T13. Sample verdicts: real sources only

File `index.html`: `const S=[…]`, `pick()`, the chips, and the default `#claim` text.

The audit found invented signals ("Bot amplification flagged", "Pattern seen in 3 languages") and an unlinked "Source: national electoral commission". Replace the samples with **three** chips whose every source is a working link.

1. Replace the `const S=[…]` array with:
   ```js
   const APPEAL={label:"Appeal this verdict",url:"method.html#appeals"};
   const S=[
    {c:"You can now vote in the French presidential election by sending a text message.",v:"FALSE",col:"var(--false)",t:"In France you vote in person at your polling station or, if you cannot, by proxy (procuration). There is no voting by text message, and no online voting for the presidential election.",m:[{label:"Service-Public.fr: Vote par procuration",url:"https://www.service-public.gouv.fr/particuliers/vosdroits/F1604"},{label:"Service-Public.fr: Élection présidentielle",url:"https://www.service-public.gouv.fr/particuliers/vosdroits/F1940"},"Nothing deleted",APPEAL]},
    {c:"Romania's Constitutional Court annulled the 2024 presidential election.",v:"TRUE",col:"var(--true)",t:"On 6 December 2024 the Court annulled the election, citing declassified intelligence reports, including about 25,000 TikTok accounts that allegedly boosted one candidate.",m:["Primary: Constitutional Court of Romania, ruling of 6 December 2024",{label:"PISM Spotlight 82/2024",url:"https://www.pism.pl/publications/constitutional-court-nullifies-romanias-presidential-election"},{label:"Lawfare: declassified intelligence on TikTok accounts",url:"https://www.lawfaremedia.org/article/romania--foreign-election-interference--and-a-dangerous-u.s.-retreat"},APPEAL]},
    {c:"Meta has stopped fact-checking everywhere in the world.",v:"MISLEADING",col:"var(--misleading)",t:"Meta ended its third-party fact-checking programme in the United States in April 2025. The post overstates it as worldwide.",m:[{label:"Meta Newsroom: More Speech and Fewer Mistakes, 7 Jan 2025",url:"https://about.fb.com/news/2025/01/meta-more-speech-fewer-mistakes/"},{label:"The Hill: US programme ends 7 April 2025",url:"https://thehill.com/policy/technology/5233142-meta-fact-checking-program-to-officially-end-monday/"},"Context added, nothing removed",APPEAL]}
   ];
   ```
   Both Service-Public links returned HTTP 200 on 22 Nov 2026. The live checker also rates this claim FALSE.
2. Chips: keep three buttons:
   - `data-i="0"`, `data-track="demo-chip-1"`, label `Vote by text`;
   - `data-i="1"`, `demo-chip-2`, `Romania 2024`;
   - `data-i="2"`, `demo-chip-3`, `Meta fact-checking`.

   Delete the fourth button.
3. Set the default text in `<textarea id="claim">` to `S[0].c` exactly. The first click must hit the curated sample.
4. Rewrite `pick()` for the new indexes: `text`/`sms` → `S[0]`, `romania` → `S[1]`, `meta`/`facebook` → `S[2]`. Delete the `poll`/`close` rule.
5. In `showCanned`, change the time label `Illustrative verdict · demo` to `Curated example`.
6. In `renderMeta`, links whose `url` starts with `method.html` open in the same tab: set `target="_blank"` only for `http` URLs.

**Accept:**
- `grep -n "Bot amplification\|3 languages\|national electoral commission\|Polling hours" index.html` shows nothing.
- Each chip shows a verdict whose links all open.
- The README events list says `demo-chip-1` to `demo-chip-3`.

Commit: `Demo samples: three curated verdicts with working sources, appeal link`

## T14. Demo notes

File `index.html`: the two `<p class="note">` paragraphs at the end of `#demo`. Replace them with:

```html
<p class="note">Sample chips show curated examples. Anything else you paste is checked live by AI against web sources and can be wrong: open the sources before you share.</p>
<p class="note">Pasted text goes to Google's Gemini API, with Google Search, to produce the verdict. We don't store it; Google may keep it under its API terms. Don't paste personal data. <a href="privacy.html">Privacy</a></p>
```

Then make the claim-checker paragraph in `privacy.html` (T8b) match this wording.

Commit: `Demo notes: shorter, product voice, link to privacy`

## T15. "Not yet verified" copy

File `index.html`, `runLive()`.

About a third of real, checkable claims come back NOT_YET_VERIFIED with no sources: "Macron is the president of France", "Trump won 2020", "EU banned petrol cars from 2025". The fixed text "No reliable source could be found for this claim" then reads as broken.

When `d.verdict==="NOT_YET_VERIFIED"` and (`!d.summary` or `d.summary.startsWith("No reliable source")`), show this summary instead:

`We couldn't confirm this with reliable sources yet. Try it as one specific claim (who did what, and when), or check back later: unverified claims go to our review queue.`

Keep the Worker's own summary when it explains something else. For example, "The input is a prompt injection attempt…" or "…does not contain a checkable factual claim" are good as they are.

**Accept:** with `CHECK_ENDPOINT` mocked to return `{"verdict":"NOT_YET_VERIFIED","summary":"No reliable source could be found for this claim.","sources":[]}`, the new text shows.

Commit: `Checker: helpful copy when no source is found`

## T16. Worker: shared-network rate limit and a second grounding attempt

Files `worker/wrangler.toml`, `worker/src/index.js`, `worker/README.md`. Deployment is H5, by the user.

**16a. Rate limit.** In `wrangler.toml`, change `limit = 10` to `limit = 30`. Hallway tests on campus Wi-Fi and the December class demo share one public IP, so 10 a minute would return "busy" to most of the room.

**16b. Second attempt with a different model.** Today, when the first answer has no sources, `ask()` is called again with the same model order.
- Give `ask` a `start` index (`ask(0)`, then `ask(1)` for the retry).
- Loop `for (let i = start; i < MODELS.length; i++)`.

A different model has a fresh chance to run the search. Keep exactly one retry: each one adds 2–10 s.

**16c. (Only if H5 finds it is required.)** Google's grounding terms have required showing "Search Suggestions" when results from Grounding with Google Search are displayed.
- If that still applies, return `queries: (cand.groundingMetadata.webSearchQueries||[]).slice(0,3)` from the Worker.
- On the page, render them under the sources as `Searched: <a href="https://www.google.com/search?q=…">query</a>` chips (`encodeURIComponent`).

Skip 16c if the terms do not require it.

**16d. README.** Update:
- the rate-limit line (30 a minute, with the reason);
- the retry line ("retries once with the next model");
- the hit-rate line: "in a 22 Nov test, 8 of 12 checkable claims got a sourced verdict, none of them wrong; 4 came back unverified".

**Accept:**
- `node --check worker/src/index.js` passes.
- Do not deploy; report that H5 is needed.

Commit: `Worker: 30/min rate limit, retry grounding with the next model`

## T17. Verification (report every line)

Serve locally with `python3 -m http.server 8000` in the repo root and open `http://localhost:8000/?utm_source=test`.

1. `grep -rn "{{" index.html method.html privacy.html` shows nothing, or only `GOATCOUNTER_CODE` if H1 is pending.
2. `grep -n "formspree\|Van Westendorp\|id=\"decide\"\|advisory.html\|Cohort B" index.html` shows nothing.
3. Three forms: invalid email blocked; valid submit shows success plus notice; fields cleared; DevTools Network shows **no request** on submit (except a GoatCounter `count` call when configured).
4. Premium: click "Start 30-day free trial", the dialog opens, submitting works as in check 3, Escape closes it, and focus returns to the button.
5. Hero "Request a free pilot →" scrolls to the pilot form, the "We are a" select shows Newsroom, and focus lands on Organisation.
6. Plan buttons: each scrolls to the right form; the API button preselects Platform.
7. At 375×812: no horizontal scroll (`document.documentElement.scrollWidth<=innerWidth`); `#demo` top ≤ 640; the menu opens and closes; pricing cards stack.
8. Dark mode (DevTools, emulate `prefers-color-scheme: dark`): every section readable, and the buttons are visible.
9. Contrast snippet from T9 gives both values ≥ 4.5.
10. With GoatCounter configured, after `localStorage.removeItem('skipgc')` in a private window: one page view, then a waitlist submit. Both appear in the GoatCounter dashboard within a minute: the page view, `landing-test`, `cta-hero-waitlist` (if clicked), and `waitlist-submit-success`. Afterwards set `skipgc` again.
11. `python3 -I experiment/analyze.py --goatcounter <fake csv>` runs, as in T11.
12. `method.html`, `privacy.html` and every footer link open without 404.
13. Checker, with each chip: a curated verdict appears in about 1.5 s; the label reads "Curated example"; every source link opens (HTTP 200); "Appeal this verdict" opens `method.html#appeals`.
14. Checker, live: paste `Germany held a snap federal election in February 2025.` The button shows "Checking…" and the bar moves. A TRUE verdict with at least one source arrives in under 25 s. No "AI-generated, can be wrong" chip appears.
15. Checker, edge cases:
    - an empty box shows the hint;
    - `asdfgh qwerty` gives NOT YET VERIFIED with the Worker's explanation;
    - a claim with no sources shows the T15 copy;
    - 601 characters cannot be typed.
16. At 375 px, the verdict header is readable (label on one line) with no horizontal scroll.
17. Live checks from `localhost:8000` work, because the Worker allows that origin. Do not send more than about 10 checks in total during verification: they cost API quota.
