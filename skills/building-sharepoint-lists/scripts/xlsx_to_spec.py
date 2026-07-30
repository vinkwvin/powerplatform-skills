#!/usr/bin/env python3
"""Convert an existing SharePoint provisioning workbook into solution-spec.yaml lists[] form.

The reverse of generate_workbook.py. Two uses:

  1. Bootstrap a spec for a system that already exists and is documented in Excel, instead of
     retyping it.
  2. Round-trip test: xlsx -> spec -> xlsx should preserve every field.

Reads whichever metadata rows it can find by their left-column labels, so it tolerates
workbooks whose row order differs. Recognised labels (case-insensitive, substring match):

    FIELD NAME / COLUMN NAME   the column name        (required)
    DATA TYPE / TYPE           the SharePoint type    (required)
    SECTION                    grouping label
    TH / LABEL / ชื่อไทย        localised label
    DESCRIPTION                description
    CHOICES / NOTES            choices, notes
    POPULATED                  user | automation

Anything it cannot determine is emitted as a TODO comment rather than guessed.

Usage:
    python3 xlsx_to_spec.py Workbook.xlsx -o lists.yaml
    python3 xlsx_to_spec.py Workbook.xlsx --sheet "1. New_Request"
"""
import argparse
import pathlib
import re
import sys

import yaml

try:
    import openpyxl
except ImportError:
    print("openpyxl is required:  pip install openpyxl", file=sys.stderr)
    raise

SP_TO_SPEC = {
    "single line of text": "text",
    "multiple lines of text": "multiline",
    "choice": "choice",
    "yes/no": "bool",
    "boolean": "bool",
    "number": "number",
    "currency": "currency",
    "date and time": "datetime",
    "date": "datetime",
    "person or group": "person",
    "person": "person",
    "file": "file",
    "hyperlink": "text",
    "lookup": "LOOKUP-NOT-PERMITTED",
}
ROW_LABELS = {
    "name": ("field name", "column name"),
    "type": ("data type",),
    "section": ("section",),
    "label": ("ชื่อไทย", "(th)", "label"),
    "description": ("description",),
    "choices": ("choices", "notes"),
    "populated": ("populated",),
}


def map_type(raw):
    if not raw:
        return None, "type cell was empty"
    s = str(raw).strip().lower()
    for key, val in SP_TO_SPEC.items():
        if s.startswith(key) or key in s:
            if val == "LOOKUP-NOT-PERMITTED":
                return None, ("column is a Lookup. Lookup is not delegable — convert the join "
                              "to a text key before using this spec")
            return val, None
    return None, f"unrecognised SharePoint type {raw!r}"


def find_rows(ws, max_scan=14):
    """Map our field roles to the sheet's actual row numbers, by left-column label."""
    found = {}
    for r in range(1, min(ws.max_row, max_scan) + 1):
        label = str(ws.cell(row=r, column=1).value or "").strip().lower()
        if not label:
            continue
        for role, needles in ROW_LABELS.items():
            if role in found:
                continue
            if any(n in label for n in needles):
                found[role] = r
    return found


def parse_sheet(ws):
    rows = find_rows(ws)
    if "name" not in rows or "type" not in rows:
        return None, [f"sheet {ws.title!r}: could not find a FIELD NAME row and a DATA TYPE row "
                      f"in the first column — skipped"]

    notes, fields = [], []
    last_section = None
    for col in range(2, ws.max_column + 1):
        name = ws.cell(row=rows["name"], column=col).value
        if not name or not str(name).strip():
            continue
        name = str(name).strip()

        ftype, why = map_type(ws.cell(row=rows["type"], column=col).value)
        f = {"name": name}
        if ftype:
            f["type"] = ftype
        else:
            f["type"] = "text"
            notes.append(f"{ws.title} / {name}: {why}. Emitted as 'text' — CONFIRM before use")

        if "section" in rows:
            sec = ws.cell(row=rows["section"], column=col).value
            if sec and str(sec).strip():
                last_section = str(sec).strip()
            if last_section:
                f["section"] = last_section
        for role, key in (("label", "label_th"), ("description", "description")):
            if role in rows:
                v = ws.cell(row=rows[role], column=col).value
                if v and str(v).strip():
                    f[key] = str(v).strip()
        if "choices" in rows:
            v = ws.cell(row=rows["choices"], column=col).value
            if v and str(v).strip():
                txt = str(v).strip()
                if f["type"] == "choice":
                    parts = [p.strip().strip('"').strip("'")
                             for p in re.split(r"[;·|]|,(?=\s*[^\s])", txt) if p.strip()]
                    if parts:
                        f["choices"] = parts
                else:
                    f["notes"] = txt
        if "populated" in rows:
            v = str(ws.cell(row=rows["populated"], column=col).value or "").strip().lower()
            if "automation" in v:
                f["populated_by"] = "automation"
            elif "user" in v:
                f["populated_by"] = "user"
        if "populated_by" not in f:
            f["populated_by"] = "user"
            notes.append(f"{ws.title} / {name}: no 'Populated by' row — defaulted to 'user'. "
                         f"CONFIRM which columns a flow writes")
        fields.append(f)

    if not fields:
        return None, [f"sheet {ws.title!r}: no field-name cells found — skipped"]

    list_name = re.sub(r"^\s*[\d①-⑩]+[.)]\s*", "", ws.title).strip()
    kind = "library" if fields and fields[0]["type"] == "file" else "list"
    return {"name": list_name, "kind": kind,
             "purpose": "TODO — describe what one row represents",
             "fields": fields}, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx")
    ap.add_argument("-o", "--out")
    ap.add_argument("--sheet", action="append",
                    help="only this sheet; repeatable. Default: every sheet that parses")
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx, data_only=True)
    lists, all_notes = [], []
    for name in wb.sheetnames:
        if args.sheet and name not in args.sheet:
            continue
        parsed, notes = parse_sheet(wb[name])
        all_notes += notes
        if parsed:
            lists.append(parsed)

    doc = yaml.safe_dump({"lists": lists}, allow_unicode=True, sort_keys=False, width=100)
    header = ["# lists[] extracted from " + pathlib.Path(args.xlsx).name,
              "# Review every TODO before feeding this to a builder skill.",
              "# relations[] is NOT inferred — joins cannot be read off a workbook. Add them by",
              "# hand, and state the reason for each (validate_lists.py requires it).", ""]
    if all_notes:
        header += ["# ---- things that needed a guess ----"] + \
                  [f"#   {n}" for n in all_notes] + [""]
    out = "\n".join(header) + doc

    if args.out:
        pathlib.Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(out)
    total = sum(len(l["fields"]) for l in lists)
    print(f"\n{len(lists)} list(s), {total} field(s)", file=sys.stderr)
    for l in lists:
        print(f"  {l['name']:26} {len(l['fields']):3} fields  ({l['kind']})", file=sys.stderr)
    if all_notes:
        print(f"\n{len(all_notes)} item(s) needed a guess — see the header comments",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
