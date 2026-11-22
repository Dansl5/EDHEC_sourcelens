# Assignment brief: Homework 2, Market validation (codified)

Source: Blackboard brief `27_M2_LI_BM_SOC_S1_B` (EDHEC M2, Foresight & Strategic Design, Cohort B). This file restates it so the team can check work against it without reopening the PDF.

## Deadline and submission

- **Due: Monday 23 November 2026, 23:59**, on Blackboard, submitted by **one** team member.
- The submission must contain:
  1. **Live artifact links**: a working URL to the published landing page, and a direct link or file for the promo video.
  2. **Experiment specification (1 page)**: business hypothesis, method, target audience tested, and the One Metric That Matters (OMTM).
  3. **Empirical results and takeaways**: the data collected (charts, conversion numbers, or verbatim user quotes) and the team's decision: **Persevere or Pivot**.
- The findings are presented in the **December block**, where the teaching team and peers challenge them and add new foresight vectors. That presentation is part of the assessment.

## Context

After the October pitch sessions and the Foresight War Gaming simulation, the team validates its riskiest Lean Canvas assumption with real users before December. The brief bridges the Lean Canvas and empirical market evidence.

## Part 1: Refine the digital artifacts

### 1. Landing page (the scope of `index.html`)

| Requirement | What the brief asks |
|---|---|
| **Core value** | Polish the low-code / no-code page so the **Unique Value Proposition is crystal clear above the fold**. |
| **User experience** | CTA buttons, intuitive navigation and core copy that **build credibility** and **address the target persona's primary pains**. |
| **Monetization clarity** | A clearly defined pricing strategy: **transparent tiers/plans, feature allocations, and billing logic**. |

### 2. Promo video / demo

- **Under 2 minutes**, tightly structured.
- Conveys **problem, solution, and how it works in practice**.
- Shows **functional prototype interactions, interface walkthroughs, or high-fidelity product visuals**, not abstract stock footage.

## Part 2: Market validation experiment

Pick the **single highest-risk assumption** on the Lean Canvas (for example Problem Resonance, Solution Desirability, Willingness-to-Pay) and test it:

- **a. Experiment architecture**: a testable hypothesis and a fitting method (Fake Door CTA on the landing page, A/B messaging test, Concierge MVP, or customer-discovery interviews using the video).
- **b. OMTM**: one unambiguous success metric, **defined before the test runs** (CTR, sign-up conversion, pre-orders, % of interviewees confirming a pain).
- **c. Run and collect**: authentic interactions, quantitative metrics, or direct qualitative feedback from the target audience.
- **d. Strategic synthesis**: an objective reading. Validated or invalidated? **Persevere or pivot?**

## Grading (10 points)

| Pillar | Sub-criterion | Graded on | Points |
|---|---|---|---|
| I. Analytical & Design Quality (5) | 1. Digital prototyping & touchpoints | Landing page and video: clarity, usability, value messaging | 2.5 |
| | 2. Data rigor & empirical evidence | Authenticity, depth and reliability of data from real users | 2.5 |
| II. Methodological Mastery (5) | 3. Experiment architecture & metric precision | Hypothesis quality, experiment shape, defined OMTM | 2.5 |
| | 4. Strategic synthesis & decision-making | Objective evaluation, critical reflection, persevere vs pivot | 2.5 |

**How the landing page feeds the grade:** criterion 1 grades it directly. Because the page is also the experiment instrument (fake door, waitlist, pilot form, analytics), it decides whether criteria 2 to 4 have any real data behind them.

## Landing page acceptance checklist

Derived from the brief and rubric. A page that fails a **blocking** item cannot support the submission.

| # | Check | Blocking |
|---|---|---|
| L1 | UVP (who, what, outcome) readable without scrolling on desktop **and** a 375 px phone | yes |
| L2 | Primary CTA above the fold, one clear primary action per audience | yes |
| L3 | Every claim on the page is true of the prototype today, or plainly labelled as planned | yes |
| L4 | No template placeholders (`{{...}}`) visible or in config on the live page | yes |
| L5 | Forms save real submissions; analytics records visits and CTA clicks | yes |
| L6 | Pricing shows tiers, what each tier includes and excludes, and billing terms (period, trial, cancellation, tax) | yes |
| L7 | Persona pains named in the copy match the persona in the experiment spec | no |
| L8 | Credibility signals are backed: links for "published method", appeals, who is behind it, a working contact | no |
| L9 | WCAG AA contrast on CTAs and body text; keyboard and screen-reader usable | no |
| L10 | Page copy, `EXPERIMENT.md` and the one-pager state the same hypothesis, OMTM and thresholds | no |
| L11 | Live page matches the committed `main` branch | no |
