#!/usr/bin/env python3
"""SourceLens experiment analysis (standard library only).

Inputs (never commit these; they contain emails and live in experiment/data/, which is git-ignored):
  --goatcounter  GoatCounter CSV export (page views and events)
  --forms        Formspree CSV export

Example:
  python3 experiment/analyze.py --goatcounter experiment/data/goatcounter.csv \
      --forms experiment/data/formspree.csv --contacted 20 --positive <count>   # omit --positive until outreach is counted

Outputs: a funnel table by channel (markdown) with 95% Wilson intervals, experiment/funnel.svg,
and PASS/FAIL for each pre-set threshold. Rates are computed at full precision and only
formatted for display.

Channel attribution: the page fires a `landing-<utm_source>` event once per page view when the link has
utm_source. Other events are attributed to the channel of the same GoatCounter session. Form rows carry
utm_source in a hidden field. Anything without a channel is reported as "(unattributed)".
"""
import argparse
import csv
import math
import os
import sys
from collections import defaultdict

Z95 = 1.959963984540054
FUNNEL_PLANS = ["citizen", "premium", "newsroom", "api"]


def wilson(k, n, z=Z95):
    """95% Wilson score interval for k successes in n trials. Returns (low, high) or (None, None) if n == 0."""
    if n <= 0:
        return None, None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def rate_str(k, n):
    if n == 0:
        return "n/a (0)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {pct(k / n)} [{pct(lo)}, {pct(hi)}]"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))
    # normalise header names: lower case, strip leading numbers/spaces (GoatCounter prefixes "2 Path")
    out = []
    for r in rows:
        nr = {}
        for k, v in r.items():
            if k is None:
                continue
            key = k.strip().lower().lstrip("0123456789 ").replace(" ", "_")
            nr[key] = (v or "").strip()
        out.append(nr)
    return out


def first(row, *names):
    for n in names:
        if n in row and row[n] != "":
            return row[n]
    return ""


def truthy(v):
    return v.strip().lower() in ("1", "true", "t", "yes", "y")


def load_excludes(path):
    items = []
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.split("#", 1)[0].strip().lower()
            if line:
                items.append(line)
    return items


def excluded(email, utm_source, excludes):
    e = email.lower()
    if "test" in e or utm_source.lower() == "test":
        return True
    return any(x in e for x in excludes)


def analyse(gc_rows, form_rows, excludes):
    # ---- GoatCounter ----
    session_channel = {}
    sessions_all = set()
    ev_sessions = defaultdict(set)  # event path -> sessions
    for r in gc_rows:
        if first(r, "bot") not in ("", "0"):  # GoatCounter: 0 = not a bot, any non-zero isbot code = bot
            continue
        sess = first(r, "session", "session_id")
        path = first(r, "path", "event_name")
        is_event = truthy(first(r, "event"))
        if not sess:
            continue
        if not is_event:
            sessions_all.add(sess)
        else:
            name = path.lstrip("/")
            ev_sessions[name].add(sess)
            if name.startswith("landing-"):
                session_channel[sess] = name[len("landing-"):]
    chan = lambda s: session_channel.get(s, "(unattributed)")

    channels = defaultdict(lambda: defaultdict(set))
    for s in sessions_all:
        channels[chan(s)]["visitors"].add(s)
    for name, sess in ev_sessions.items():
        for s in sess:
            if name == "demo-check" or name.startswith("demo-chip-"):
                channels[chan(s)]["demo"].add(s)
            if name.startswith("plan-click-"):
                channels[chan(s)]["plan_click"].add(s)
                tier = name[len("plan-click-"):]
                channels[chan(s)]["plan_" + tier].add(s)
    # ---- Forms ----
    seen = set()
    forms = defaultdict(lambda: defaultdict(int))
    dropped = 0
    for r in form_rows:
        email = first(r, "email")
        src = first(r, "utm_source") or "(unattributed)"
        if excluded(email, src, excludes):
            dropped += 1
            continue
        name = first(r, "form_name") or "waitlist"
        key = (email.lower(), name)
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        forms[src][name] += 1
    return channels, forms, dropped, sessions_all, ev_sessions


def build_table(channels, forms):
    names = sorted(set(channels) | set(forms), key=lambda c: (c.startswith("("), c))
    lines = ["| Channel | Unique visitors | Used demo | Clicked a plan | Premium click | Waitlist sign-ups | Premium priority list | Newsroom pilot requests |",
             "|---|---|---|---|---|---|---|---|"]
    tot = defaultdict(int)
    for c in names:
        v = len(channels[c]["visitors"]) if c in channels else 0
        d = len(channels[c]["demo"]) if c in channels else 0
        pc = len(channels[c]["plan_click"]) if c in channels else 0
        pr = len(channels[c]["plan_premium"]) if c in channels else 0
        wl = forms[c]["waitlist"] if c in forms else 0
        pp = forms[c]["premium"] if c in forms else 0
        pil = forms[c]["newsroom-pilot"] if c in forms else 0
        for k, x in (("v", v), ("d", d), ("pc", pc), ("pr", pr), ("wl", wl), ("pp", pp), ("pil", pil)):
            tot[k] += x
        lines.append(f"| {c} | {v} | {rate_str(d, v)} | {rate_str(pc, v)} | {rate_str(pr, v)} | {rate_str(wl, v)} | {rate_str(pp, v)} | {pil} |")
    lines.append(f"| **All channels** | {tot['v']} | {rate_str(tot['d'], tot['v'])} | {rate_str(tot['pc'], tot['v'])} | "
                 f"{rate_str(tot['pr'], tot['v'])} | {rate_str(tot['wl'], tot['v'])} | {rate_str(tot['pp'], tot['v'])} | {tot['pil']} |")
    return "\n".join(lines), tot


def funnel_svg(tot, path):
    stages = [("Unique visitors", tot["v"]), ("Used the demo", tot["d"]), ("Clicked a plan", tot["pc"]),
              ("Joined the waitlist", tot["wl"])]
    top = max(stages[0][1], 1)
    w, bar_h, gap, left, right = 760, 38, 16, 190, 150
    h = 30 + len(stages) * (bar_h + gap)
    maxw = w - left - right
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="Source Sans 3, Segoe UI, Arial, sans-serif" font-size="15">',
             f'<rect width="{w}" height="{h}" fill="#ffffff"/>']
    y = 20
    for i, (label, n) in enumerate(stages):
        bw = max(2, maxw * n / top) if n else 2
        pct_top = "" if i == 0 or tot["v"] == 0 else f"  ({n / tot['v'] * 100:.1f}% of visitors)"
        fill = ["#24324f", "#3d4f78", "#c4693f", "#6f8a5c"][i]
        parts.append(f'<text x="{left - 10}" y="{y + bar_h / 2 + 5}" text-anchor="end" fill="#1c2438">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="4" fill="{fill}"/>')
        parts.append(f'<text x="{left + bw + 8:.1f}" y="{y + bar_h / 2 + 5}" fill="#1c2438" font-weight="700">{n}<tspan font-weight="400" font-size="12" fill="#5d6579">{pct_top}</tspan></text>')
        y += bar_h + gap
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--goatcounter", required=True)
    ap.add_argument("--forms", required=True)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--exclude", default=os.path.join(here, "exclude.txt"), help="one email or substring per line (git-ignored)")
    ap.add_argument("--svg", default=os.path.join(here, "funnel.svg"))
    ap.add_argument("--t1", type=float, default=0.10, help="waitlist threshold, share of unique visitors (proposed 10%%)")
    ap.add_argument("--t2", type=float, default=0.03, help="Premium click threshold, share of unique visitors (proposed 3%%)")
    ap.add_argument("--t3", type=int, default=3, help="positive replies needed from contacted organisations (proposed 3)")
    ap.add_argument("--contacted", type=int, default=20, help="N, organisations contacted")
    ap.add_argument("--positive", type=int, default=None, help="organisations that replied positively or booked a call (manual count)")
    a = ap.parse_args(argv)

    if not os.path.exists(a.exclude):
        print(f"WARNING: exclude file not found ({a.exclude}); team emails are NOT removed beyond the 'test' rule.", file=sys.stderr)
    channels, forms, dropped, sessions_all, ev = analyse(read_csv(a.goatcounter), read_csv(a.forms), load_excludes(a.exclude))
    table, tot = build_table(channels, forms)
    print(table)
    print(f"\nForm rows removed (test, excluded, duplicate): {dropped}")
    print("Intervals are 95% Wilson [low, high]. Visitors are unique GoatCounter sessions (bots excluded).")
    funnel_svg(tot, a.svg)
    print(f"Funnel chart written to {a.svg}")

    v = tot["v"]
    print("\nPre-set thresholds (pass if observed rate >= threshold; lower bound shown for uncertainty)")
    for label, k, thr in (("T1 waitlist sign-up rate", tot["wl"], a.t1), ("T2 Premium click rate", tot["pr"], a.t2)):
        if v == 0:
            print(f"  {label}: no visitors, cannot evaluate")
            continue
        lo, _ = wilson(k, v)
        verdict = "PASS" if k / v >= thr else "FAIL"
        note = "" if verdict == "FAIL" or lo >= thr else " (lower bound below threshold: weak pass)"
        print(f"  {label}: {rate_str(k, v)} vs threshold {thr * 100:.1f}% -> {verdict}{note}")
    if a.positive is None:
        print("  T3 newsroom replies: not measured (pass --positive with the manual outreach count; {{TODO}} until then)")
    else:
        verdict = "PASS" if a.positive >= a.t3 else "FAIL"
        print(f"  T3 newsroom replies: {a.positive} of {a.contacted} contacted vs threshold {a.t3} -> {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
