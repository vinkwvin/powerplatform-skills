#!/usr/bin/env python3
"""Generate an admin manual and a user manual from one solution-spec.yaml.

ONE SOURCE, TWO RENDERINGS. The user manual is a projection of the admin manual — its two body
sections are the admin manual's user-facing sections, compressed. Architecture, setup,
troubleshooting and appendices are dropped. Nothing is authored twice.

meta.status decides the mode:
    draft   before the build — no setup, no troubleshooting, no screenshots yet.
            A requirements test: the user reads it and says "that's not how we do it".
    final   after the build — full, with screenshot frames a human fills and
            troubleshooting entries a human supplies.

Screenshots cannot be generated. Numbered placeholder frames are emitted instead, each naming
the screen, the state, and what to highlight.

Usage:
    python3 generate_manual.py spec.yaml -o out/
    python3 generate_manual.py spec.yaml -o out/ --style ../assets/house-style.yaml
"""
import argparse
import pathlib
import sys

import yaml

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor, Cm
except ImportError:
    print("python-docx is required:  pip install python-docx", file=sys.stderr)
    raise

DEFAULT_STYLE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "house-style.yaml"


# ---------------------------------------------------------------- helpers --
def heading_text(en, local, order):
    """Bilingual heading in the configured order. Localised text is a sibling, never a name."""
    if not local:
        return en
    return f"{local} / {en}" if order == "local_first" else f"{en} / {local}"


def add_table(doc, headers, rows, widths=None):
    """PLATFORM: a table needs a width on the table AND on every cell, or Word and Google Docs
    disagree about the layout."""
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    widths = widths or [Cm(16 / len(headers))] * len(headers)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(str(h))
        run.bold = True
        run.font.size = Pt(9)
        c.width = widths[i]
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].width = widths[i]
            cells[i].text = ""
            for j, line in enumerate(str(val).split("\n")):
                p = cells[i].paragraphs[0] if j == 0 else cells[i].add_paragraph()
                p.add_run(line).font.size = Pt(9)
    doc.add_paragraph()
    return t


def add_frame(doc, n, screen, state, highlight):
    """A screenshot placeholder someone can actually act on."""
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.rows[0].cells[0]
    cell.width = Cm(16)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"[ Figure {n} — paste screenshot here ]")
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x78, 0x76, 0x86)
    for label, val in (("Screen", screen), ("State", state), ("Highlight", highlight)):
        q = cell.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = q.add_run(f"{label}: {val}")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x78, 0x76, 0x86)
    doc.add_paragraph()
    return n + 1


def cover(doc, spec, kind, style):
    meta = spec.get("meta") or {}
    order = style.get("headings", {}).get("order", "local_first")
    title = meta.get("name", "System")
    local = meta.get("name_th")
    doc.add_heading(heading_text(title, local, order), 0)
    sub = "Administrator manual" if kind == "admin" else "User guide"
    p = doc.add_paragraph()
    p.add_run(sub).bold = True
    status = str(meta.get("status", "")).lower()
    add_table(doc, ["", ""], [
        ["Version", f"{meta.get('version','—')} ({'DRAFT' if status == 'draft' else 'final'})"],
        ["System", title],
        ["Audience", "System administrators and support" if kind == "admin"
                     else "Everyday users"],
        ["Generated from", "solution-spec.yaml — do not edit this document by hand"],
    ], widths=[Cm(4), Cm(12)])
    if status == "draft":
        p = doc.add_paragraph()
        r = p.add_run("This is a draft, written before the system was built. Please read it as a "
                      "question: anything here that does not match how you actually work is "
                      "cheapest to fix now.")
        r.italic = True
    doc.add_page_break()


# ------------------------------------------------------------------ parts --
def part_intro(doc, spec, style, kind):
    order = style.get("headings", {}).get("order", "local_first")
    meta = spec.get("meta") or {}
    roles = spec.get("roles") or []
    process = spec.get("process") or []
    doc.add_heading(heading_text("Introduction", "บทนำ" if meta.get("name_th") else None,
                                 order), 1)
    doc.add_heading("About this guide", 2)
    who = "administer" if kind == "admin" else "use"
    doc.add_paragraph(f"This guide explains how to {who} {meta.get('name','the system')}. "
                      f"It is generated from the solution specification, so it stays consistent "
                      f"with what was actually built.")
    doc.add_heading("What this system is", 2)
    doc.add_paragraph(f"{meta.get('name','The system')} is used by {len(roles)} role"
                      f"{'s' if len(roles) != 1 else ''} across {len(process)} stage"
                      f"{'s' if len(process) != 1 else ''}.")
    if process:
        doc.add_paragraph(f"It starts when {process[0].get('entry','—')} and finishes when "
                          f"{process[-1].get('exit','—')}.")
    doc.add_heading("Who should read what", 2)
    rows = [[r.get("label", ""), ", ".join(r.get("manual_sections") or []) or "—",
             "\n".join(f"· {x}" for x in (r.get("responsibilities") or [])) or "—"]
            for r in roles]
    add_table(doc, ["Role", "Reads", "Responsible for"], rows,
              widths=[Cm(4), Cm(3), Cm(9)])
    if kind == "admin":
        doc.add_heading("Access levels", 2)
        add_table(doc, ["Role", "Can see"],
                  [[r.get("label", ""), r.get("visibility_scope", "—")] for r in roles],
                  widths=[Cm(6), Cm(10)])


def part_architecture(doc, spec, style):
    doc.add_heading("System architecture", 1)
    doc.add_paragraph("How the parts fit together. This section is for administrators; "
                      "everyday users do not need it.")
    lists = spec.get("lists") or []
    flows = spec.get("flows") or []
    screens = spec.get("screens") or []
    doc.add_heading(f"SharePoint — {len(lists)} lists", 2)
    add_table(doc, ["List", "Holds", "Columns"],
              [[l.get("name", ""), l.get("purpose", "—"), str(len(l.get("fields") or []))]
               for l in lists], widths=[Cm(5), Cm(9), Cm(2)])
    doc.add_heading("Which columns are filled in by hand", 2)
    doc.add_paragraph("Columns marked automated are written by a flow. Do not type into them.")
    rows = []
    for l in lists:
        user = [f.get("name") for f in (l.get("fields") or [])
                if f.get("populated_by") == "user"]
        auto = [f.get("name") for f in (l.get("fields") or [])
                if f.get("populated_by") == "automation"]
        rows.append([l.get("name", ""), ", ".join(user) or "—", ", ".join(auto) or "—"])
    add_table(doc, ["List", "Entered by a person", "Written by automation"], rows,
              widths=[Cm(4), Cm(6), Cm(6)])
    if flows:
        doc.add_heading(f"Power Automate — {len(flows)} flows", 2)
        add_table(doc, ["Flow", "Type", "Does"],
                  [[f.get("name", ""), (f.get("trigger") or {}).get("kind", "—"),
                    f.get("purpose", "—")] for f in flows],
                  widths=[Cm(5), Cm(3), Cm(8)])
    if screens:
        doc.add_heading(f"Power Apps — {len(screens)} screens", 2)
        role_label = {r.get("id"): r.get("label", r.get("id")) for r in (spec.get("roles") or [])}
        add_table(doc, ["Screen", "Does", "Who can open it"],
                  [[s.get("name", ""), s.get("purpose", "—"),
                    ", ".join(role_label.get(r, r) for r in (s.get("roles") or [])) or "—"]
                   for s in screens], widths=[Cm(5), Cm(7), Cm(4)])


def part_screens(doc, spec, style, fig, roles_filter=None, compress=False):
    """Per screen: heading -> screenshot frame -> steps. The shape of the user manual."""
    order = style.get("headings", {}).get("order", "local_first")
    screens = spec.get("screens") or []
    bindings = spec.get("bindings") or []
    lists = {l.get("name"): l for l in (spec.get("lists") or [])}
    n = 0
    for s in screens:
        if roles_filter and not (set(s.get("roles") or []) & set(roles_filter)):
            continue
        n += 1
        doc.add_heading(f"{n}. {heading_text(s.get('name',''), s.get('name_th'), order)}", 2)
        if s.get("purpose"):
            doc.add_paragraph(s["purpose"])
        fig = add_frame(doc, fig, s.get("name", ""),
                        "opened, with a typical record loaded",
                        "the main action button")
        inputs = [b for b in bindings
                  if b.get("screen") == s.get("id") and b.get("direction") == "input"]
        shows = [b for b in bindings
                 if b.get("screen") == s.get("id") and b.get("direction") == "display"]
        if inputs:
            doc.add_paragraph("What you fill in:", style="Intense Quote")
            for b in inputs:
                lst = lists.get(b.get("list")) or {}
                fld = next((f for f in (lst.get("fields") or [])
                            if f.get("name") == b.get("field")), {})
                label = b.get("shows") or fld.get("label_th") or b.get("field") or "—"
                bullet = doc.add_paragraph(style="List Bullet")
                bullet.add_run(str(label))
                if fld.get("choices"):
                    bullet.add_run(f"  — choose one of: {', '.join(map(str, fld['choices']))}"
                                   ).italic = True
                if fld.get("required"):
                    bullet.add_run("  (required)").bold = True
        if shows and not compress:
            doc.add_paragraph("What the screen shows you:", style="Intense Quote")
            for b in shows:
                doc.add_paragraph(str(b.get("shows") or b.get("field") or "—"),
                                  style="List Bullet")
        if s.get("fires_flows"):
            doc.add_paragraph("When you submit, the system notifies the next team "
                              "automatically.", style="List Bullet")
    return fig


def part_setup(doc, spec, style):
    doc.add_heading("Setting the system up", 1)
    doc.add_paragraph("First-time setup, for administrators.")
    doc.add_heading("Checklist", 2)
    lists = spec.get("lists") or []
    for i, step in enumerate([
        "Create the SharePoint site.",
        f"Create the {len(lists)} lists and libraries from the provisioning workbook, in order.",
        "Remove automation-written columns from the default forms.",
        "Import each flow package and map its connections when prompted.",
        "Paste the app screens into Power Apps Studio.",
        "Add the team to the role mapping list.",
        "Run one request end to end before opening it to users.",
    ], 1):
        doc.add_paragraph(f"{i}. {step}", style="List Number")
    doc.add_paragraph("Detailed steps are in the provisioning workbook produced by "
                      "building-sharepoint-lists.")


def part_troubleshooting(doc, spec, style, entries):
    doc.add_heading("Troubleshooting", 1)
    if not entries:
        doc.add_paragraph("No problems have been recorded yet. Entries are added here as real "
                          "failures occur — this section is deliberately empty rather than "
                          "filled with problems nobody has actually had.")
        return
    for i, e in enumerate(entries, 1):
        doc.add_heading(f"{i}. {e.get('symptom','')}", 2)
        doc.add_paragraph(f"Cause: {e.get('cause','—')}")
        doc.add_paragraph(f"Fix: {e.get('fix','—')}")


def part_glossary(doc, spec, style):
    order = style.get("headings", {}).get("order", "local_first")
    doc.add_heading(heading_text("Glossary", "อภิธานศัพท์"
                                 if (spec.get("meta") or {}).get("name_th") else None, order), 1)
    g = spec.get("glossary") or []
    if not g:
        doc.add_paragraph("No glossary in the specification. This is a gap: the glossary is what "
                          "stops two readers understanding this document differently.")
        return
    add_table(doc, ["Term", "Also called", "Means"],
              [[heading_text(x.get("term", ""), x.get("term_th"), order),
                ", ".join(x.get("aka") or []) or "—", x.get("definition", "")] for x in g],
              widths=[Cm(4), Cm(4), Cm(8)])


# ------------------------------------------------------------------ build --
def build_admin(spec, style, troubles):
    doc = Document()
    doc.styles["Normal"].font.size = Pt(10.5)
    cover(doc, spec, "admin", style)
    part_intro(doc, spec, style, "admin")
    part_architecture(doc, spec, style)
    fig = 1
    final = str((spec.get("meta") or {}).get("status", "")).lower() == "final"
    if final:
        part_setup(doc, spec, style)
    doc.add_heading("Using the system", 1)
    fig = part_screens(doc, spec, style, fig)
    if final:
        part_troubleshooting(doc, spec, style, troubles)
    part_glossary(doc, spec, style)
    return doc, fig - 1


def build_user(spec, style):
    """A projection of the admin manual: the user-facing sections, compressed."""
    doc = Document()
    doc.styles["Normal"].font.size = Pt(11)
    cover(doc, spec, "user", style)
    part_intro(doc, spec, style, "user")
    roles = spec.get("roles") or []
    everyone = [r.get("id") for r in roles
                if "user" in (r.get("manual_sections") or ["user"])]
    doc.add_heading("Using the app", 1)
    fig = part_screens(doc, spec, style, 1, roles_filter=everyone or None, compress=True)
    part_glossary(doc, spec, style)
    return doc, fig - 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", default=".")
    ap.add_argument("--style", default=str(DEFAULT_STYLE))
    ap.add_argument("--troubleshooting",
                    help="YAML file of observed failures: symptom, cause, fix. Never invented.")
    args = ap.parse_args()

    spec = yaml.safe_load(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    try:
        style = yaml.safe_load(pathlib.Path(args.style).read_text(encoding="utf-8")) or {}
    except OSError:
        style = {}
    troubles = []
    if args.troubleshooting:
        troubles = yaml.safe_load(pathlib.Path(args.troubleshooting).read_text("utf-8")) or []

    meta = spec.get("meta") or {}
    status = str(meta.get("status", "draft")).lower()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = str(meta.get("id", "system"))

    admin, n_admin = build_admin(spec, style, troubles)
    ap_ = out / f"{slug}-admin-manual.docx"
    admin.save(ap_)
    user, n_user = build_user(spec, style)
    up = out / f"{slug}-user-manual.docx"
    user.save(up)

    print(f"wrote {ap_}\nwrote {up}")
    print(f"  mode: {status}"
          + ("  — no setup, no troubleshooting, no screenshots yet" if status == "draft" else ""))
    print(f"  screenshot frames to fill: {n_admin} in the admin manual, {n_user} in the user "
          f"manual")
    if status == "final" and not troubles:
        print("  NOTE: final mode with no troubleshooting entries. Ask the team for real "
              "observed failures — do not invent them.")
    if not (spec.get("glossary") or []):
        print("  WARNING: the spec has no glossary. Both manuals will say so rather than "
              "inventing one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
