#!/usr/bin/env python3
"""Lint every skill against the packaging rules, and check the five descriptions do not collide.

Run before packaging. Everything here is a claude.ai constraint or a project rule from
PROJECT-BRIEF.md — none of it is stylistic preference.

Usage:
    python3 scripts/lint_skills.py
    python3 scripts/lint_skills.py --skills-dir skills
"""
import argparse
import pathlib
import re
import sys
from collections import Counter

import yaml

RESERVED = {"anthropic", "claude", "skill", "skills", "system", "assistant"}
MAX_NAME = 64
MAX_DESC = 1024
MAX_BODY = 500
TARGET_BODY = 200
MAX_REF = 100          # references longer than this need a TOC
TIME_WORDS = re.compile(
    r"\b(currently|at present|as of (?:today|now|20\d\d)|recently|nowadays|"
    r"(?<!as )soon|shortly|in the (?:coming|next) (?:weeks?|months?)|last (?:week|month|year)|"
    r"this (?:week|month|quarter|year))\b", re.I)
# One term per concept — mixing these makes a skill read as two documents stitched together.
TERM_SETS = [
    ({"column", "field"}, "column/field"),
    ({"screen", "page"}, "screen/page"),
    ({"flow", "workflow"}, "flow/workflow"),
]

problems, notes = [], []


def bad(skill, msg):
    problems.append(f"FAIL  {skill}: {msg}")


def note(skill, msg):
    notes.append(f"note  {skill}: {msg}")


def lint_skill(d):
    name = d.name
    sk = d / "SKILL.md"
    if not sk.is_file():
        bad(name, "no SKILL.md")
        return None
    text = sk.read_text(encoding="utf-8")

    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        bad(name, "no YAML frontmatter")
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        bad(name, f"frontmatter does not parse: {e}")
        return None

    n, desc = fm.get("name", ""), fm.get("description", "")
    if n != name:
        bad(name, f"frontmatter name {n!r} does not match the folder")
    if len(n) > MAX_NAME:
        bad(name, f"name is {len(n)} chars, max {MAX_NAME}")
    if not re.fullmatch(r"[a-z0-9-]+", n or ""):
        bad(name, f"name {n!r} must be lowercase letters, numbers and hyphens only")
    for w in RESERVED:
        if w in (n or "").split("-"):
            bad(name, f"name contains the reserved word {w!r}")
    if not (desc or "").strip():
        bad(name, "description is empty")
    if len(desc) > MAX_DESC:
        bad(name, f"description is {len(desc)} chars, max {MAX_DESC} — claude.ai rejects it")

    lines = text.splitlines()
    if len(lines) > MAX_BODY:
        bad(name, f"SKILL.md is {len(lines)} lines, max {MAX_BODY}")
    elif len(lines) > TARGET_BODY:
        note(name, f"SKILL.md is {len(lines)} lines, target under {TARGET_BODY}")

    if not re.search(r"<!--\s*v\d+\.\d+\.\d+\s*-->", text):
        bad(name, "no <!-- vX.Y.Z --> version line")
    flat = re.sub(r"\s+", " ", text)
    if "If it fails, fix and re-run. Do not present output to the user until the validator " \
       "exits clean." not in flat:
        bad(name, "the D2 validation gate is missing or reworded")

    for label, body in (("SKILL.md", text),
                        *[(f"references/{p.name}", p.read_text(encoding="utf-8"))
                          for p in sorted((d / "references").glob("*.md"))]):
        for hit in set(TIME_WORDS.findall(body)):
            note(name, f"{label}: time-sensitive wording {hit!r}")

    if "\\" in text.replace("\\n", "").replace("\\t", ""):
        for ln in lines:
            if re.search(r"[A-Za-z0-9_]\\[A-Za-z0-9_]", ln) and "\\\\" not in ln:
                note(name, f"possible backslash path: {ln.strip()[:60]!r}")
                break

    refs = d / "references"
    if refs.is_dir():
        for sub in refs.iterdir():
            if sub.is_dir():
                bad(name, f"references/{sub.name}/ is nested — references must be one level deep")
        for p in sorted(refs.glob("*.md")):
            body = p.read_text(encoding="utf-8")
            if len(body.splitlines()) > MAX_REF and "## Contents" not in body:
                bad(name, f"references/{p.name} is {len(body.splitlines())} lines with no TOC")
            if f"references/{p.name}" not in text:
                note(name, f"references/{p.name} is never pointed to from SKILL.md")

    scripts = sorted((d / "scripts").glob("*.py")) if (d / "scripts").is_dir() else []
    if not scripts:
        bad(name, "no scripts/ — every generator skill ships a validator")
    elif not any("validate" in s.name for s in scripts):
        bad(name, "no validate_*.py in scripts/")

    words = Counter(re.findall(r"[a-z]+", text.lower()))
    for terms, label in TERM_SETS:
        used = {t for t in terms if words.get(t, 0) >= 3}
        if len(used) > 1:
            counts = ", ".join(f"{t}×{words[t]}" for t in sorted(used))
            note(name, f"mixes {label} ({counts}) — one term per concept")

    return {"name": n, "desc": desc, "lines": len(lines),
            "refs": len(list(refs.glob("*.md"))) if refs.is_dir() else 0,
            "scripts": len(scripts)}


def check_collisions(skills):
    """Every skill must name every sibling in a Do NOT clause."""
    names = {s["name"] for s in skills}
    print("\n" + "=" * 78)
    print("DESCRIPTION COLLISIONS")
    print("=" * 78)
    for s in skills:
        missing = sorted(n for n in names - {s["name"]} if n not in s["desc"])
        if missing:
            bad(s["name"], f"description does not route away from: {', '.join(missing)}")
        else:
            print(f"  {s['name']:34} routes away from all {len(names)-1} siblings")

    # shared trigger vocabulary is where two skills fight for the same request
    def trigger_phrases(d):
        return {p.strip().lower() for p in re.findall(r'"([^"]{4,60})"', d)}

    print("\n  shared trigger phrases:")
    clean = True
    for i, a in enumerate(skills):
        for b in skills[i + 1:]:
            shared = trigger_phrases(a["desc"]) & trigger_phrases(b["desc"])
            if shared:
                clean = False
                bad(a["name"], f"shares trigger phrase(s) {sorted(shared)} with {b['name']}")
    if clean:
        print("    none — no two skills quote the same trigger phrase")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills-dir", default="skills")
    args = ap.parse_args()
    root = pathlib.Path(args.skills_dir)
    dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    if not dirs:
        print(f"no skills found in {root}", file=sys.stderr)
        return 2

    print("=" * 78)
    print(f"LINT — {len(dirs)} skill(s)")
    print("=" * 78)
    print(f"{'skill':34} {'desc':>6} {'body':>6} {'refs':>5} {'scripts':>8}")
    skills = []
    for d in dirs:
        s = lint_skill(d)
        if s:
            skills.append(s)
            print(f"{s['name']:34} {len(s['desc']):>6} {s['lines']:>6} "
                  f"{s['refs']:>5} {s['scripts']:>8}")
    if skills:
        check_collisions(skills)

    print("\n" + "=" * 78)
    for line in problems:
        print(line)
    for line in notes:
        print(line)
    print(f"\n{len(problems)} failure(s), {len(notes)} note(s).")
    if problems:
        print("Fix every FAIL before packaging.")
        return 1
    print("All skills pass. Ready to package.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
