#!/usr/bin/env python3
"""Package each skill as an upload-ready .zip in dist/, then verify by unzipping to temp.

A claude.ai skill zip has SKILL.md at the folder root, inside a single top-level folder named
for the skill. Every zip is verified after writing — a package nobody checked is a package that
fails on upload, in front of the teammate you were trying to help.

Usage:
    python3 scripts/package_skills.py
    python3 scripts/package_skills.py --out dist --skills-dir skills
"""
import argparse
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile

import yaml

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".git"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".DS_Store"}
RESERVED = {"anthropic", "claude", "skill", "skills", "system", "assistant"}


def keep(p):
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return False
    return p.suffix not in EXCLUDE_SUFFIX and p.name != ".DS_Store"


def verify(zpath, name):
    """Unzip to temp and confirm the thing actually works as a skill package."""
    problems = []
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        try:
            with zipfile.ZipFile(zpath) as z:
                bad = z.testzip()
                if bad:
                    return [f"corrupt entry: {bad}"]
                z.extractall(tmp)
        except zipfile.BadZipFile as e:
            return [f"not a valid zip: {e}"]

        roots = [d for d in tmp.iterdir() if d.is_dir()]
        if len(roots) != 1:
            problems.append(f"expected one top-level folder, found {[d.name for d in roots]}")
            return problems
        root = roots[0]
        if root.name != name:
            problems.append(f"top-level folder is {root.name!r}, expected {name!r}")

        sk = root / "SKILL.md"
        if not sk.is_file():
            problems.append("SKILL.md is not at the folder root")
            return problems

        text = sk.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            problems.append("frontmatter missing or malformed")
            return problems
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            problems.append(f"frontmatter does not parse: {e}")
            return problems

        n, desc = fm.get("name", ""), fm.get("description", "")
        if n != name:
            problems.append(f"frontmatter name {n!r} != folder {name!r}")
        if len(n) > 64:
            problems.append(f"name is {len(n)} chars, max 64")
        if not re.fullmatch(r"[a-z0-9-]+", n or ""):
            problems.append(f"name {n!r} is not lowercase/numbers/hyphens")
        for w in RESERVED:
            if w in (n or "").split("-"):
                problems.append(f"name contains reserved word {w!r}")
        if not (desc or "").strip():
            problems.append("description is empty")
        if len(desc) > 1024:
            problems.append(f"description is {len(desc)} chars, max 1024 — upload will fail")

        for py in (root / "scripts").glob("*.py") if (root / "scripts").is_dir() else []:
            try:
                compile(py.read_text(encoding="utf-8"), str(py), "exec")
            except SyntaxError as e:
                problems.append(f"scripts/{py.name} does not compile: line {e.lineno}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    src = pathlib.Path(args.skills_dir)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dirs = sorted(d for d in src.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    if not dirs:
        print(f"no skills in {src}", file=sys.stderr)
        return 2

    print("=" * 78)
    print(f"PACKAGE — {len(dirs)} skill(s) → {out}/")
    print("=" * 78)
    failed = 0
    for d in dirs:
        name = d.name
        zpath = out / f"{name}.zip"
        files = sorted(p for p in d.rglob("*") if p.is_file() and keep(p))
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                z.write(p, (pathlib.Path(name) / p.relative_to(d)).as_posix())

        problems = verify(zpath, name)
        size = zpath.stat().st_size
        status = "OK" if not problems else "FAILED"
        print(f"\n{name}")
        print(f"  {zpath}  ({size:,} bytes, {len(files)} files)  [{status}]")
        parts = {}
        for p in files:
            top = p.relative_to(d).parts[0] if len(p.relative_to(d).parts) > 1 else "(root)"
            parts[top] = parts.get(top, 0) + 1
        print("  " + "  ".join(f"{k}:{v}" for k, v in sorted(parts.items())))
        for prob in problems:
            failed += 1
            print(f"  FAIL  {prob}")

    print("\n" + "=" * 78)
    if failed:
        print(f"{failed} problem(s). Do not distribute these.")
        return 1
    print(f"All {len(dirs)} packages verified: SKILL.md at the folder root, frontmatter parses, "
          f"name and description within limits, every script compiles.")
    print("Upload at claude.ai → Settings → Capabilities → Skills → Upload skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
