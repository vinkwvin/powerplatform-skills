#!/usr/bin/env python3
"""Render a solution-spec.yaml as a print-ready system-overview document.

Emits ONE self-contained HTML file — no external assets, no fonts to fetch, no JavaScript.
The user opens it and presses Ctrl/Cmd+P -> Save as PDF. Page breaks, margins and running
headers are already set by @page CSS.

Why HTML and not a PDF binary: the environment this is used in has no CLI and no local
execution, so a PDF library is not available where the document is actually produced. Every
browser prints to PDF. If a headless Chromium happens to be present, --pdf will use it, but
nothing depends on that.

Section order is fixed by assets/pdf-outline.md. The document is a rendering of the spec —
never hand-edit the output; change the spec and re-render.

Usage:
    python3 render_overview.py spec.yaml -o overview.html
    python3 render_overview.py spec.yaml -o overview.html --pdf
"""
import argparse
import html
import pathlib
import re
import shutil
import subprocess
import sys

import yaml

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
:root{--ink:#1b1b23;--dim:#46454f;--faint:#787686;--line:#c7c4d7;--tint:#f5f2fe;
      --accent:#3b39c2;--warn:#ba1a1a;--bg:#fff;}
*{box-sizing:border-box}
body{font:11pt/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans Thai",
     "Sarabun",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);
     margin:0 auto;max-width:190mm;padding:10mm 6mm;}
h1{font-size:22pt;margin:0 0 2mm;letter-spacing:-.01em}
h2{font-size:14pt;margin:10mm 0 3mm;padding-bottom:1.5mm;border-bottom:2px solid var(--accent);
   page-break-after:avoid;break-after:avoid}
h3{font-size:11.5pt;margin:6mm 0 2mm;color:var(--dim);page-break-after:avoid;break-after:avoid}
p{margin:0 0 3mm}
.sub{color:var(--faint);font-size:10pt;margin:0 0 6mm}
.badge{display:inline-block;padding:.6mm 2.4mm;border-radius:3mm;font-size:8.5pt;
       background:var(--tint);color:var(--accent);border:1px solid var(--line);
       vertical-align:middle}
.badge.warn{background:#fff0ee;color:var(--warn);border-color:#f4c7c2}
table{width:100%;border-collapse:collapse;margin:0 0 5mm;font-size:9.5pt;
      page-break-inside:auto}
th{text-align:left;background:var(--tint);border-bottom:1.5px solid var(--line);
   padding:1.8mm 2.2mm;font-weight:600;color:var(--dim);font-size:8.5pt;
   text-transform:uppercase;letter-spacing:.03em}
td{border-bottom:1px solid #e4e1ec;padding:1.8mm 2.2mm;vertical-align:top}
tr{page-break-inside:avoid;break-inside:avoid}
code{font-family:"SF Mono",Menlo,Consolas,monospace;font-size:9pt;
     background:var(--tint);padding:.3mm 1.2mm;border-radius:1mm}
.note{border-left:3px solid var(--accent);background:var(--tint);padding:2.5mm 3.5mm;
      margin:0 0 5mm;font-size:9.5pt;page-break-inside:avoid}
.note.warn{border-left-color:var(--warn);background:#fff8f7}
.q{border-left:3px solid var(--warn);padding:2mm 3.5mm;margin:0 0 3mm;
   page-break-inside:avoid;background:#fff8f7}
.q b{color:var(--warn)}
.meta{color:var(--faint);font-size:9pt}
.auto{color:var(--faint);font-style:italic}
section{page-break-before:auto}
section.brk{page-break-before:always;break-before:page}
@media print{body{padding:0;max-width:none}.noprint{display:none}}
.noprint{background:var(--tint);border:1px solid var(--line);border-radius:2mm;
         padding:3mm 4mm;margin:0 0 8mm;font-size:9.5pt}
"""


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def find_todos(node, path=""):
    """Every TODO / TBD / ??? anywhere in the spec, with the key path it sits at."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += find_todos(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += find_todos(v, f"{path}[{i}]")
    elif isinstance(node, str) and re.search(r"\b(TODO|TBD|\?\?\?)\b", node, re.I):
        out.append((path, node.strip()))
    return out


def table(headers, rows, empty=None):
    if not rows:
        return f'<p class="meta">{esc(empty or "None recorded.")}</p>'
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def render(spec):
    meta = spec.get("meta") or {}
    roles = spec.get("roles") or []
    process = spec.get("process") or []
    screens = spec.get("screens") or []
    lists = spec.get("lists") or []
    flows = spec.get("flows") or []
    glossary = spec.get("glossary") or []
    relations = spec.get("relations") or []
    role_label = {r.get("id"): r.get("label", r.get("id")) for r in roles}
    status = str(meta.get("status", "")).lower()

    P = []
    A = P.append

    # ---- title -----------------------------------------------------------
    title = meta.get("name") or "System overview"
    th = f' <span class="meta">/ {esc(meta.get("name_th"))}</span>' if meta.get("name_th") else ""
    A(f"<h1>{esc(title)}{th}</h1>")
    badge = f'<span class="badge{" warn" if status == "draft" else ""}">{esc(status or "—")}</span>'
    A(f'<p class="sub">System overview &nbsp;·&nbsp; spec v{esc(meta.get("version","—"))} '
      f'&nbsp;{badge}</p>')

    A('<div class="noprint"><b>To save as PDF:</b> press Ctrl/Cmd&nbsp;+&nbsp;P and choose '
      '“Save as PDF”. Margins and page breaks are already set. This box does not print.</div>')

    if status == "draft":
        A('<div class="note warn"><b>This is a draft.</b> It describes what we believe the '
          'system should do, before it is built. Read it as a question — anything here that is '
          'wrong is cheapest to fix now.</div>')

    # ---- 1 summary -------------------------------------------------------
    A("<section><h2>1. Summary</h2>")
    stages = len(process)
    A(f"<p>{esc(title)} is used by {len(roles)} role{'s' if len(roles) != 1 else ''} across "
      f"{stages} stage{'s' if stages != 1 else ''}. It is built on "
      f"{len(screens)} screen{'s' if len(screens) != 1 else ''}, "
      f"{len(lists)} list{'s' if len(lists) != 1 else ''}, and "
      f"{len(flows)} automated flow{'s' if len(flows) != 1 else ''}.</p>")
    if process:
        first, last = process[0], process[-1]
        A(f"<p>It starts when <b>{esc(first.get('entry','—'))}</b> and finishes when "
          f"<b>{esc(last.get('exit','—'))}</b>.</p>")
    if meta.get("sharepoint_site"):
        A(f'<p class="meta">Site: <code>{esc(meta["sharepoint_site"])}</code></p>')
    A("</section>")

    # ---- 2 glossary ------------------------------------------------------
    A("<section><h2>2. Glossary</h2>")
    A('<p class="meta">Read this first. It exists so two people reading this document '
      'understand it the same way.</p>')
    rows = []
    for g in glossary:
        term = f"<b>{esc(g.get('term'))}</b>"
        if g.get("term_th"):
            term += f'<br><span class="meta">{esc(g["term_th"])}</span>'
        if g.get("unresolved"):
            term += ' <span class="badge warn">unresolved</span>'
        aka = ", ".join(esc(a) for a in (g.get("aka") or [])) or '<span class="meta">—</span>'
        d = esc(g.get("definition", ""))
        if g.get("distinct_from"):
            df = g["distinct_from"]
            d += (f'<br><span class="meta">Not the same as '
                  f'<b>{esc(df.get("term"))}</b>: {esc(df.get("difference"))}</span>')
        rows.append([term, aka, d])
    A(table(["Term", "Also called", "Means"], rows, "No glossary recorded — this is a gap."))
    A("</section>")

    # ---- 3 who does what -------------------------------------------------
    A('<section class="brk"><h2>3. Who does what</h2>')
    rows = []
    for r in roles:
        rid = r.get("id")
        label = f"<b>{esc(r.get('label'))}</b>"
        if r.get("label_th"):
            label += f'<br><span class="meta">{esc(r["label_th"])}</span>'
        resp = "<br>".join(f"· {esc(x)}" for x in (r.get("responsibilities") or [])) or "—"
        seen = [s.get("name") for s in screens if rid in (s.get("roles") or [])]
        rows.append([label, resp, esc(r.get("visibility_scope", "—")),
                     ", ".join(esc(s) for s in seen) or '<span class="meta">—</span>'])
    A(table(["Role", "Responsible for", "Can see", "Screens"], rows))
    A("</section>")

    # ---- 4 process -------------------------------------------------------
    A("<section><h2>4. The process</h2>")
    rows = []
    for p in sorted(process, key=lambda x: x.get("index", 0)):
        stage = f"<b>{esc(p.get('stage'))}</b>"
        if p.get("stage_th"):
            stage += f'<br><span class="meta">{esc(p["stage_th"])}</span>'
        rows.append([esc(p.get("index", "")), stage,
                     esc(role_label.get(p.get("owner_role"), p.get("owner_role", "—"))),
                     esc(p.get("entry", "—")), esc(p.get("exit", "—"))])
    A(table(["#", "Stage", "Owner", "Starts when", "Moves on when"], rows))
    A("</section>")

    # ---- 5 screens -------------------------------------------------------
    if screens:
        A('<section class="brk"><h2>5. Screens</h2>')
        rows = []
        for s in screens:
            name = f"<b>{esc(s.get('name'))}</b>"
            if s.get("name_th"):
                name += f'<br><span class="meta">{esc(s["name_th"])}</span>'
            who = ", ".join(esc(role_label.get(r, r)) for r in (s.get("roles") or [])) or "—"
            rw = []
            if s.get("reads"):
                rw.append("reads " + ", ".join(esc(x) for x in s["reads"]))
            if s.get("writes"):
                rw.append("writes " + ", ".join(esc(x) for x in s["writes"]))
            rows.append([name, esc(s.get("purpose", "—")), who,
                         "<br>".join(rw) or "—",
                         ", ".join(esc(f) for f in (s.get("fires_flows") or [])) or "—"])
        A(table(["Screen", "What it is for", "Who sees it", "Data", "Flows"], rows))
        A("</section>")

    # ---- 6 data ----------------------------------------------------------
    if lists:
        A('<section class="brk"><h2>6. Data</h2>')
        if relations:
            A("<h3>How the lists connect</h3>")
            rows = [[f"{esc(r.get('from'))}.{esc(r.get('from_field'))}",
                     f"{esc(r.get('to'))}.{esc(r.get('to_field'))}" if r.get("to")
                     else '<span class="meta">—</span>',
                     f"<code>{esc(r.get('kind'))}</code>",
                     esc(r.get("reason", ""))] for r in relations]
            A(table(["From", "To", "Kind", "Why this way"], rows))
        for l in lists:
            fields = l.get("fields") or []
            kind = l.get("kind", "list")
            tag = ' <span class="badge">document library</span>' if kind == "library" else ""
            A(f"<h3>{esc(l.get('name'))}{tag}</h3>")
            purpose = esc(l.get("purpose", ""))
            if l.get("purpose_th"):
                purpose += f' <span class="meta">/ {esc(l["purpose_th"])}</span>'
            A(f"<p>{purpose} <span class=\"meta\">— {len(fields)} columns</span></p>")
            rows = []
            for f in fields:
                nm = f"<code>{esc(f.get('name'))}</code>"
                if f.get("label_th"):
                    nm += f'<br><span class="meta">{esc(f["label_th"])}</span>'
                pop = f.get("populated_by", "—")
                pop_c = f'<span class="auto">{esc(pop)}</span>' if pop == "automation" else esc(pop)
                notes = "; ".join(esc(c) for c in (f.get("choices") or []))
                rows.append([nm, esc(f.get("type")), pop_c, notes or esc(f.get("description", ""))])
            A(table(["Column", "Type", "Filled in by", "Values / notes"], rows))
        A("</section>")

    # ---- 7 automation ----------------------------------------------------
    if flows:
        A('<section class="brk"><h2>7. Automation</h2>')
        rows = []
        for f in flows:
            trig = (f.get("trigger") or {}).get("kind", "—")
            waits = "the app waits" if f.get("responds_to_app") else "runs in background"
            if f.get("type") == "child":
                waits = "called by other flows"
            rows.append([f"<b>{esc(f.get('name'))}</b>", esc(f.get("purpose", "—")),
                         f"<code>{esc(trig)}</code>", waits,
                         ", ".join(esc(x) for x in (f.get("lists") or [])) or "—"])
        A(table(["Flow", "What it does", "Triggered by", "Timing", "Touches"], rows))
        A("</section>")

    # ---- 8 open questions ------------------------------------------------
    todos = find_todos({k: v for k, v in spec.items()})
    A("<section><h2>8. Open questions</h2>")
    if todos:
        A('<p class="meta">Unresolved at the time of writing. Reply by number.</p>')
        for i, (path, text) in enumerate(todos, 1):
            A(f'<div class="q"><b>Q{i}.</b> {esc(text)}'
              f'<br><span class="meta">spec: <code>{esc(path)}</code></span></div>')
    else:
        A('<p class="meta">None outstanding.</p>')
    A("</section>")

    # ---- 9 colophon ------------------------------------------------------
    A("<section><h2>9. How this was produced</h2>")
    A(f'<p class="meta">Generated from <code>solution-spec.yaml</code> v'
      f'{esc(meta.get("version","—"))} ({esc(status or "—")}). '
      f'This document is a rendering of that file — do not edit it by hand. To change something, '
      f'change the spec and re-render, so the two cannot drift apart.</p>')
    A("</section>")

    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{esc(title)} — system overview</title>"
            f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")


def find_browser():
    """A headless browser, if this sandbox happens to have one. Nothing depends on it."""
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        exe = shutil.which(name)
        if exe:
            return exe
    for root in (pathlib.Path("/opt/pw-browsers"), pathlib.Path.home() / ".cache/ms-playwright"):
        if not root.is_dir():
            continue
        for pat in ("chromium*/chrome-linux/chrome", "chromium*/chrome-linux/headless_shell"):
            hits = sorted(root.glob(pat))
            if hits:
                return str(hits[-1])
    return None


def try_pdf(html_path, pdf_path):
    for cand in filter(None, [find_browser()]):
        exe = cand
        try:
            subprocess.run([exe, "--headless", "--disable-gpu", "--no-sandbox",
                            f"--print-to-pdf={pdf_path}", f"file://{html_path.resolve()}"],
                           check=True, capture_output=True, timeout=120)
            if pathlib.Path(pdf_path).is_file():
                return exe
        except (subprocess.SubprocessError, OSError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", default="system-overview.html")
    ap.add_argument("--pdf", action="store_true",
                    help="also try a headless browser, if one is present")
    args = ap.parse_args()

    spec = yaml.safe_load(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        print("spec did not parse as a mapping", file=sys.stderr)
        return 2

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(spec), encoding="utf-8")
    print(f"wrote {out}")

    todos = find_todos(spec)
    meta = spec.get("meta") or {}
    print(f"  status: {meta.get('status','—')}   spec v{meta.get('version','—')}")
    print(f"  {len(spec.get('glossary') or [])} glossary term(s), "
          f"{len(spec.get('roles') or [])} role(s), "
          f"{len(spec.get('screens') or [])} screen(s), "
          f"{len(spec.get('lists') or [])} list(s), "
          f"{len(spec.get('flows') or [])} flow(s)")
    if todos:
        print(f"  {len(todos)} open question(s) rendered in §8")
    if not (spec.get("glossary") or []):
        print("  WARNING: no glossary. §2 is the section that stops two readers disagreeing —"
              " build it before sending this out.")

    if args.pdf:
        pdf = out.with_suffix(".pdf")
        used = try_pdf(out, pdf)
        print(f"  wrote {pdf} (via {used})" if used else
              "  no headless browser found — open the HTML and press Ctrl/Cmd+P → Save as PDF")
    else:
        print("  open it and press Ctrl/Cmd+P → Save as PDF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
