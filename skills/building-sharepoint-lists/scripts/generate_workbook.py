#!/usr/bin/env python3
"""Generate a SharePoint provisioning workbook (and optionally a PnP column script) from the
lists[] section of a solution-spec.yaml.

The workbook is **transposed**: fields run across the columns, one sheet per list, with fixed
metadata rows down the left. A wide list is then read left-to-right in the same direction the
form is filled, and a person entering sample data types down a column rather than across a row.

Layout per list sheet — row numbers are fixed so a human can rely on them:

    row 1  Section              grouping label, only on the first field of each section
    row 2  FIELD NAME (EN)      the SharePoint internal/display name — ASCII
    row 3  Data type            the SharePoint column type
    row 4  Label                localised display label (house style: sibling, never in the name)
    row 5  Description          what the column is for
    row 6  Choices / Notes      enumerated choices, or provisioning notes
    row 7  Populated by         user | automation
    row 8  marker row           "enter data below"
    row 9+ blank                sample or seed rows

Usage:
    python3 generate_workbook.py spec.yaml -o Provisioning.xlsx
    python3 generate_workbook.py spec.yaml --script columns.ps1
    python3 generate_workbook.py spec.yaml -o out.xlsx --label-row-header "ชื่อไทย (TH)"
"""
import argparse
import pathlib
import sys

import yaml

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    print("openpyxl is required:  pip install openpyxl", file=sys.stderr)
    raise

# spec type -> (SharePoint column type, PnP field type)
TYPE_MAP = {
    "text":      ("Single line of text",    "Text"),
    "multiline": ("Multiple lines of text", "Note"),
    "choice":    ("Choice",                 "Choice"),
    "bool":      ("Yes/No (Boolean)",       "Boolean"),
    "number":    ("Number",                 "Number"),
    "currency":  ("Currency",               "Currency"),
    "datetime":  ("Date and Time",          "DateTime"),
    "person":    ("Person or Group",        "User"),
    "file":      ("File",                   None),      # library, not a column
}

ROW_SECTION, ROW_NAME, ROW_TYPE, ROW_LABEL = 1, 2, 3, 4
ROW_DESC, ROW_CHOICES, ROW_POPULATED, ROW_MARKER = 5, 6, 7, 8
FIRST_DATA_ROW = 9

HDR_FILL = PatternFill("solid", fgColor="EAE6F2")
AUTO_FILL = PatternFill("solid", fgColor="FFF3E0")   # automation-populated columns
KEY_FILL = PatternFill("solid", fgColor="E4E1EC")


def sheet_title(index, name):
    """Excel caps sheet names at 31 chars and forbids : \\ / ? * [ ]."""
    base = f"{index}. {name}"
    for ch in ':\\/?*[]':
        base = base.replace(ch, "-")
    return base[:31]


def write_list_sheet(ws, lst, index, label_header, join_fields):
    fields = lst.get("fields") or []
    kind = lst.get("kind", "list")

    for row, text in ((ROW_SECTION, "Section"), (ROW_NAME, "FIELD NAME (EN)"),
                      (ROW_TYPE, "Data type"), (ROW_LABEL, label_header),
                      (ROW_DESC, "Description"), (ROW_CHOICES, "Choices / Notes"),
                      (ROW_POPULATED, "Populated by"),
                      (ROW_MARKER, "enter data below")):
        c = ws.cell(row=row, column=1, value=text)
        c.font = Font(bold=True, size=9)
        c.fill = HDR_FILL
        c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.column_dimensions["A"].width = 18

    last_section = None
    for i, f in enumerate(fields):
        col = i + 2
        name = f.get("name", "")
        ftype = f.get("type", "text")
        sp_type, _ = TYPE_MAP.get(ftype, (f"UNKNOWN ({ftype})", None))

        section = f.get("section")
        if section and section != last_section:
            ws.cell(row=ROW_SECTION, column=col, value=section).font = Font(bold=True, size=9)
            last_section = section

        ws.cell(row=ROW_NAME, column=col, value=name).font = Font(bold=True, size=10)
        ws.cell(row=ROW_TYPE, column=col, value=sp_type)
        ws.cell(row=ROW_LABEL, column=col, value=f.get("label_th") or f.get("label") or "")
        ws.cell(row=ROW_DESC, column=col, value=f.get("description") or "")

        notes = []
        if f.get("choices"):
            notes.append("; ".join(str(c) for c in f["choices"]))
        if f.get("other_field"):
            notes.append(f"free text -> {f['other_field']}")
        if f.get("required"):
            notes.append("required")
        if name in join_fields:
            notes.append("JOIN KEY — text, not Lookup (delegation)")
        if lst.get("title_holds") and name == "Title":
            notes.append(f"rename display label to '{lst['title_holds']}'; indexed by default")
        if ftype == "file":
            notes.append("document library: create as a library, then add the columns right of this")
        ws.cell(row=ROW_CHOICES, column=col, value=" · ".join(notes))

        pop = f.get("populated_by", "")
        pc = ws.cell(row=ROW_POPULATED, column=col, value=pop)
        if pop == "automation":
            for r in (ROW_NAME, ROW_TYPE, ROW_POPULATED):
                ws.cell(row=r, column=col).fill = AUTO_FILL
            pc.value = "automation — do NOT put on a user form"
        if name in join_fields or (lst.get("title_holds") and name == "Title"):
            ws.cell(row=ROW_NAME, column=col).fill = KEY_FILL

        ws.column_dimensions[get_column_letter(col)].width = max(14, min(len(name) + 4, 30))

    for r in range(1, ROW_MARKER + 1):
        for c in range(1, len(fields) + 2):
            ws.cell(row=r, column=c).alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = ws.cell(row=FIRST_DATA_ROW, column=2)

    note = f"{kind.upper()} · {len(fields)} columns"
    if kind == "library":
        note += " · create as a DOCUMENT LIBRARY, not a list"
    ws.cell(row=FIRST_DATA_ROW + 20, column=1, value=note).font = Font(italic=True, size=9)


def write_guide(ws, spec, lists, label_header):
    meta = spec.get("meta") or {}
    rows = [
        ("How to use this workbook", ""),
        ("", ""),
        ("Solution", meta.get("name", "")),
        ("Spec version", f"{meta.get('version','')} ({meta.get('status','')})"),
        ("Site", meta.get("sharepoint_site", "— ask, then fill in —")),
        ("", ""),
        ("Steps", ""),
        ("1", "Create each list or library below, in the order of the sheets. Sheet order "
              "matters: a list referenced by another is created first."),
        ("2", "For each sheet, create the columns left to right. Row 3 gives the SharePoint "
              "column type to pick."),
        ("3", "Row 2 is the column NAME — keep it exactly as written, ASCII only. Row 4 is the "
              "display LABEL, which you set after creating the column."),
        ("4", "Columns shaded orange are written by a flow. Create them, then remove them from "
              "the default form so nobody types into them."),
        ("5", "Columns shaded purple are keys. They are plain text on purpose — see the note in "
              "row 6. Do not convert them to Lookup."),
        ("6", "A sheet marked LIBRARY must be created as a document library, not a list."),
        ("", ""),
        ("Why the join columns are text and not Lookup", ""),
        ("", "A Lookup column cannot be filtered on the server. A gallery filtered on one "
             "silently truncates at the delegation limit and shows an incomplete list with no "
             "error message. A text key keeps Filter() and StartsWith() delegable."),
        ("", ""),
        ("Lists in this workbook", ""),
    ]
    for i, lst in enumerate(lists, 1):
        rows.append((f"{i}. {lst.get('name','')}",
                     f"{lst.get('kind','list')} · {len(lst.get('fields') or [])} columns · "
                     f"{lst.get('purpose','')}"))
    for r, (a, b) in enumerate(rows, 1):
        ca = ws.cell(row=r, column=1, value=a)
        cb = ws.cell(row=r, column=2, value=b)
        if r == 1:
            ca.font = Font(bold=True, size=14)
        elif a and not b:
            ca.font = Font(bold=True)
        cb.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 96


def build_script(lists, site):
    out = [
        "# SharePoint column-creation script (PnP.PowerShell).",
        "# Generated from solution-spec.yaml. Review before running.",
        "# A document library is NOT created here — create libraries in the browser first,",
        "# then run this to add their metadata columns.",
        "",
        f'$site = "{site or "<SITE URL>"}"',
        "Connect-PnPOnline -Url $site -Interactive",
        "",
    ]
    for lst in lists:
        name, kind = lst.get("name", ""), lst.get("kind", "list")
        out.append(f"# ---------- {name} ({kind}) ----------")
        if kind == "library":
            out.append(f'# Create the library "{name}" in the browser, then continue.')
        else:
            out.append(f'New-PnPList -Title "{name}" -Template GenericList -OnQuickLaunch')
        for f in lst.get("fields") or []:
            fname, ftype = f.get("name"), f.get("type", "text")
            if fname == "Title" or ftype == "file":
                continue
            _, pnp = TYPE_MAP.get(ftype, (None, None))
            if pnp is None:
                out.append(f'# SKIPPED {fname}: unmapped type {ftype!r}')
                continue
            line = f'Add-PnPField -List "{name}" -DisplayName "{fname}" ' \
                   f'-InternalName "{fname}" -Type {pnp} -AddToDefaultView'
            if f.get("populated_by") == "automation":
                line = line.replace(" -AddToDefaultView", "")
                line += "   # automation-written: keep off the user form"
            if ftype == "choice" and f.get("choices"):
                choices = ",".join(f'"{c}"' for c in f["choices"])
                line = f'Add-PnPField -List "{name}" -DisplayName "{fname}" ' \
                       f'-InternalName "{fname}" -Type Choice -Choices {choices} ' \
                       f'-AddToDefaultView'
            out.append(line)
        if lst.get("indexed"):
            for idx in lst["indexed"]:
                out.append(f'# index: {idx} (Title is indexed by default)')
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", help="workbook path (.xlsx)")
    ap.add_argument("--script", help="also write a PnP column script here")
    ap.add_argument("--label-row-header", default="Label (localised)",
                    help="header for the display-label row, e.g. 'ชื่อไทย (TH)'")
    args = ap.parse_args()

    spec = yaml.safe_load(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    lists = spec.get("lists") or []
    if not lists:
        print("spec has no lists[] section — nothing to generate", file=sys.stderr)
        return 2

    join_fields = set()
    for rel in spec.get("relations") or []:
        if rel.get("kind") == "text_key" and rel.get("from_field"):
            join_fields.add(rel["from_field"])

    if args.out:
        wb = openpyxl.Workbook()
        write_guide(wb.active, spec, lists, args.label_row_header)
        wb.active.title = "How to use"
        for i, lst in enumerate(lists, 1):
            ws = wb.create_sheet(sheet_title(i, lst.get("name", f"List{i}")))
            write_list_sheet(ws, lst, i, args.label_row_header, join_fields)
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        wb.save(args.out)
        total = sum(len(l.get("fields") or []) for l in lists)
        libs = sum(1 for l in lists if l.get("kind") == "library")
        print(f"wrote {args.out}")
        print(f"  {len(lists)} sheets ({len(lists)-libs} lists, {libs} librar"
              f"{'y' if libs == 1 else 'ies'}), {total} columns")
        for l in lists:
            auto = sum(1 for f in (l.get('fields') or [])
                       if f.get('populated_by') == 'automation')
            print(f"  {l.get('name'):26} {len(l.get('fields') or []):3} columns "
                  f"({auto} automation-written)")

    if args.script:
        pathlib.Path(args.script).write_text(
            build_script(lists, (spec.get("meta") or {}).get("sharepoint_site")),
            encoding="utf-8")
        print(f"wrote {args.script}")
    if not args.out and not args.script:
        print("nothing to do: pass -o and/or --script", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
