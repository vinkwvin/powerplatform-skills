#!/usr/bin/env python3
"""Validate a generated .docx manual before it is sent to anyone.

A .docx is a zip of XML. python-docx will happily read a file that other readers reject, so
this checks the package itself — required parts, well-formed XML, relationship integrity —
as well as the content rules the manual has to satisfy.

PLATFORM errors are OOXML or python-docx facts. HOUSE warnings are conventions from
assets/house-style.yaml.

Exit codes:  0 = no PLATFORM errors   1 = at least one ERROR   2 = usage failure

Usage:
    python3 validate_manual.py manual.docx
    python3 validate_manual.py manual.docx --spec solution-spec.yaml
"""
import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import yaml

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REQUIRED_PARTS = ["[Content_Types].xml", "_rels/.rels", "word/document.xml"]
DEFAULT_STYLE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "house-style.yaml"

errors, warns = [], []


def err(loc, msg):
    errors.append(f"ERROR  [PLATFORM] {loc}: {msg}")


def warn(loc, msg):
    warns.append(f"WARN   [HOUSE]    {loc}: {msg}")


def validate_package(path):
    """The file has to be a well-formed OOXML package, not just readable by one library."""
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        err(path.name, "not a zip — a .docx is a zip archive of XML parts")
        return None
    names = set(z.namelist())
    for part in REQUIRED_PARTS:
        if part not in names:
            err(path.name, f"missing required package part {part!r}")
    bad = z.testzip()
    if bad:
        err(path.name, f"corrupt entry in the archive: {bad}")

    for name in sorted(n for n in names if n.endswith(".xml") or n.endswith(".rels")):
        try:
            ET.fromstring(z.read(name))
        except ET.ParseError as e:
            err(f"{path.name}!{name}", f"XML does not parse: {e}")

    # every r:id referenced by the document must exist in its rels part
    if "word/document.xml" in names and "word/_rels/document.xml.rels" in names:
        doc = z.read("word/document.xml").decode("utf-8", "replace")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
        have = set(re.findall(r'Id="([^"]+)"', rels))
        used = set(re.findall(r'r:(?:id|embed)="([^"]+)"', doc))
        for missing in sorted(used - have):
            err(f"{path.name}!word/document.xml",
                f"references relationship {missing!r}, which is not in document.xml.rels")
    return z


def validate_content(path, z, spec, style):
    try:
        import docx
    except ImportError:
        warn(path.name, "python-docx not installed — content checks skipped")
        return
    d = docx.Document(str(path))

    heads = [(p.style.name, p.text.strip()) for p in d.paragraphs
             if p.style.name.startswith(("Heading", "Title")) and p.text.strip()]
    if not heads:
        err(path.name, "no built-in Heading styles used. A table of contents built from custom "
                       "styles comes out empty")
    if not any(s == "Title" or s == "Heading 1" for s, _ in heads):
        err(path.name, "no Title or Heading 1 — the document has no top level")

    # PLATFORM: a table needs a width on the table AND on every cell, or Word and Google Docs
    # lay it out differently.
    for i, t in enumerate(d.tables):
        for r, row in enumerate(t.rows):
            for c, cell in enumerate(row.cells):
                if cell.width is None:
                    warn(f"{path.name} table[{i}]",
                         f"cell r{r}c{c} has no width — set a width on the table and on every "
                         f"cell, or layout differs between Word and Google Docs")
                    break
            else:
                continue
            break

    for p in d.paragraphs:
        if "\n" in p.text:
            err(f"{path.name}", "a paragraph contains a literal newline — use separate "
                                "paragraphs, not \\n")
            break

    text = "\n".join(p.text for p in d.paragraphs)
    frames = re.findall(r"Figure (\d+) — paste screenshot here",
                        "\n".join(c.text for t in d.tables for row in t.rows for c in row.cells))
    if frames:
        nums = [int(n) for n in frames]
        if sorted(nums) != list(range(1, len(nums) + 1)):
            warn(path.name, f"screenshot frames are not numbered 1..n: {sorted(nums)}")

    # ---- HOUSE ----
    order = (style.get("headings") or {}).get("order", "local_first")
    if spec:
        meta = spec.get("meta") or {}
        status = str(meta.get("status", "")).lower()
        low = text.lower()
        if status == "draft":
            if "troubleshooting" in low:
                warn(path.name, "draft mode but a troubleshooting section is present — nothing "
                                "has failed yet, so entries would have to be invented")
            if "setting the system up" in low or "first-time setup" in low:
                warn(path.name, "draft mode but a setup section is present — it cannot be "
                                "written before the system exists")
            if "draft" not in low:
                warn(path.name, "draft mode but the document does not say so. A reader who "
                                "thinks it is final will not correct it")
        if not (spec.get("glossary") or []):
            warn(path.name, "the spec has no glossary — the manual's glossary section will be "
                            "empty, and the glossary is what stops two readers disagreeing")

        # automation-written columns must not be presented as user input
        auto = {f.get("name") for l in (spec.get("lists") or [])
                for f in (l.get("fields") or []) if f.get("populated_by") == "automation"}
        marker = "what you fill in"
        if marker in low:
            seg = low.split(marker, 1)[1][:1500]
            # Word-boundary match, and skip names that also occur as role or screen labels —
            # a column called "Team" matches inside "Middle Team" otherwise.
            elsewhere = " ".join(
                [str(r.get("label", "")) for r in (spec.get("roles") or [])]
                + [str(s.get("name", "")) for s in (spec.get("screens") or [])]).lower()
            for name in sorted(auto):
                if not name or len(name) < 4:
                    continue
                if re.search(rf"\b{re.escape(name.lower())}\b", elsewhere):
                    continue
                if re.search(rf"\b{re.escape(name.lower())}\b", seg):
                    warn(path.name, f"{name!r} is populated_by automation but appears under "
                                    f"'what you fill in' — a user typing into a column a flow "
                                    f"overwrites is a support ticket")
        if meta.get("name_th") and order == "local_first":
            bilingual = [h for _, h in heads if " / " in h]
            if bilingual:
                first = bilingual[0].split(" / ")[0]
                if first.isascii():
                    warn(path.name, f"house style is local_first but the first bilingual heading "
                                    f"leads with ASCII: {bilingual[0]!r}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", nargs="+")
    ap.add_argument("--spec")
    ap.add_argument("--style", default=str(DEFAULT_STYLE))
    args = ap.parse_args()

    spec = None
    if args.spec:
        spec = yaml.safe_load(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    try:
        style = yaml.safe_load(pathlib.Path(args.style).read_text(encoding="utf-8")) or {}
    except OSError:
        style = {}

    for f in args.docx:
        p = pathlib.Path(f)
        if not p.is_file():
            print(f"No such file: {p}", file=sys.stderr)
            return 2
        before = len(errors)
        z = validate_package(p)
        if z is None or len(errors) > before:
            # The package itself is broken. Content checks would crash on it, and their
            # results would be meaningless anyway — fix the package first.
            print(f"  {p.name}: package is invalid, content checks skipped", file=sys.stderr)
            continue
        validate_content(p, z, spec, style)

    for line in errors + warns:
        print(line)
    print(f"\n{len(errors)} error(s) [PLATFORM], {len(warns)} warning(s) [HOUSE].")
    if errors:
        print("Do not send this. Every ERROR is a document-format rule.")
        return 1
    if warns:
        print("No format errors. Review the HOUSE warnings.")
    else:
        print("Clean. Safe to send.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
