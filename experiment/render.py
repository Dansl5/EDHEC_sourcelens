#!/usr/bin/env python3
"""Render experiment/EXPERIMENT.md to a one-page A4 PDF (standard library + headless Chrome).

Usage: python3 experiment/render.py
Writes experiment/one-pager.html and experiment/SourceLens_Market_Experiment.pdf, then checks the page count.
Supported markdown subset: headings, paragraphs, bullet and numbered lists, tables, bold, italic, code, links, images.
"""
import html
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "EXPERIMENT.md")
OUT_HTML = os.path.join(HERE, "one-pager.html")
OUT_PDF = os.path.join(HERE, "SourceLens_Market_Experiment.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page{size:A4;margin:8mm 10mm}
*{box-sizing:border-box}
body{font-family:"Source Sans 3","Segoe UI",Helvetica,Arial,sans-serif;font-size:11pt;line-height:1.2;color:#1c2438;margin:0}
h1{font-family:"Source Serif 4",Georgia,serif;font-size:19pt;margin:0 0 3px;color:#24324f}
h2{font-family:"Source Serif 4",Georgia,serif;font-size:12pt;margin:5px 0 1px;color:#24324f;border-bottom:1px solid #e3ddd3}
p{margin:2px 0}
ul,ol{margin:2px 0;padding-left:18px}
li{margin:0}
table{border-collapse:collapse;width:100%;margin:3px 0;font-size:11pt}
th,td{border:1px solid #d9d2c6;padding:0 5px;text-align:left;vertical-align:top}
th{background:#f1ece3}
code{font-family:Menlo,monospace;font-size:9.5pt}
img{display:block;max-width:100%;max-height:30mm;margin:3px auto}
.todo{background:#fff3b0;padding:0 2px;border-radius:2px}
.missing{border:1px dashed #b5452f;padding:6px;text-align:center;margin:3px 0;height:30mm;display:flex;align-items:center;justify-content:center}
a{color:#24324f}
"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(?<![\"'>=(])(https?://[^\s<)]+)", r'<a href="\1">\1</a>', t)
    t = re.sub(r"\{\{(.*?)\}\}", r'<span class="todo">{{\1}}</span>', t)
    return t


def image(line):
    m = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
    alt, src = m.group(1), m.group(2)
    if os.path.exists(os.path.join(HERE, src)):
        return f'<img alt="{html.escape(alt)}" src="{html.escape(src)}">'
    return f'<div class="missing"><span class="todo">{{{{TODO: {html.escape(alt)}; run analyze.py to create {html.escape(src)}}}}}</span></div>'


def render(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("#"):
            n = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{n}>{inline(ln[n:].strip())}</h{n}>")
            i += 1
        elif ln.startswith("!["):
            out.append(image(ln)); i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
            has_head = any(c for c in head)
            t = "<table>"
            if has_head:
                t += "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>"
            for r in body:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</table>")
        elif re.match(r"\s*([-*]|\d+\.)\s", ln):
            tag = "ol" if re.match(r"\s*\d+\.", ln) else "ul"
            items = []
            while i < len(lines) and re.match(r"\s*([-*]|\d+\.)\s", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            para = [ln]; i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||!\[|\s*([-*]|\d+\.)\s)", lines[i]):
                para.append(lines[i]); i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def page_count(pdf):
    data = open(pdf, "rb").read()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def main():
    body = render(open(SRC, encoding="utf-8").read())
    open(OUT_HTML, "w", encoding="utf-8").write(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SourceLens Market Experiment</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=Source+Sans+3:wght@400;600;700&display=swap">'
        f"<style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                    f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    n = page_count(OUT_PDF)
    print(f"{OUT_PDF}: {n} page(s)")
    if n != 1:
        print("Longer than one page: cut words in EXPERIMENT.md.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
