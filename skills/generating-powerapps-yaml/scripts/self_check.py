#!/usr/bin/env python3
"""Prove a change to this skill did not break it. Run before and after every edit.

WHY THIS EXISTS
    Nobody maintains this skill centrally. Whoever edits it is the only person checking it,
    in a chat, without the project it came from. So the evidence has to travel inside the zip.

    The trap this catches: a new rule that looks obviously correct and fires on output that
    already shipped. That has happened here once already — a warning was added for buttons
    with no BorderThickness, and it fired on 20 reference buttons that compiled and worked.
    A validator that warns on known-good output teaches people to ignore warnings, and then
    it protects nobody.

WHAT IT CHECKS
    tests/reference/   17 screens that compiled in Power Apps Studio. 0 errors, 0 warnings.
                       These are ground truth. If your change makes one of them complain,
                       your change is wrong — not the screen.
    tests/field/       real output from a later project, with known warnings recorded.
    tests/probes/      purpose-built files, each declaring the counts it must produce.
                       A probe proves a rule still FIRES. Reference screens prove it does
                       not fire wrongly. Both directions are needed.

    Expected counts live in tests/expected.json. Changing a number there is allowed, but it
    is a decision — write down why in the same commit or message.

USAGE
    python3 scripts/self_check.py            # from the skill folder
    python3 scripts/self_check.py -v         # show every file

    Exit 0 = safe. Exit 1 = you broke something, or you changed behaviour without recording it.

DO NOT read the test files to understand them. There are 2.3 MB of them and they exist to be
checked mechanically. Reading them burns context you will want for the actual edit.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
VALIDATOR = HERE / "validate_pa_yaml.py"
COUNTS = re.compile(r"(\d+) error\(s\) \[PLATFORM\], (\d+) warning\(s\) \[HOUSE\]")

# In the repository the corpus lives in source-artifacts/; in the packaged zip it is copied
# to tests/. Look in both so the check runs in either place without being configured.
CANDIDATES = {
    "reference": [SKILL / "tests" / "reference", SKILL.parent.parent / "source-artifacts" / "yaml"],
    "field": [SKILL / "tests" / "field",
              SKILL.parent.parent / "evals" / "generating-powerapps-yaml" / "fixtures"],
    "probes": [SKILL / "tests" / "probes",
               SKILL.parent.parent / "evals" / "generating-powerapps-yaml" / "fixtures"],
}


def resolve(kind):
    for path in CANDIDATES[kind]:
        if path.is_dir() and any(path.glob("*.pa.yaml")):
            return path
    return None


def run_validator(paths):
    """Return (errors, warnings) for one file, or None if the validator itself failed."""
    proc = subprocess.run([sys.executable, str(VALIDATOR), *[str(p) for p in paths]],
                          capture_output=True, text=True)
    m = COUNTS.search(proc.stdout)
    if not m:
        return None, proc.stdout + proc.stderr
    return (int(m.group(1)), int(m.group(2))), proc.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    expected_path = SKILL / "tests" / "expected.json"
    if not expected_path.exists():
        print(f"FAIL  missing {expected_path.relative_to(SKILL)} — nothing to check against.")
        return 1
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    failures, notes = [], []

    # --- reference screens, checked as one batch: they must be collectively spotless -----
    ref_dir = resolve("reference")
    if ref_dir is None:
        failures.append("reference screens not found — cannot verify anything. "
                        "The zip is incomplete; get a complete copy before editing.")
    else:
        files = sorted(ref_dir.glob("*.pa.yaml"))
        want_n = expected["reference"]["files"]
        if len(files) != want_n:
            failures.append(f"reference: found {len(files)} screens, expected {want_n}. "
                            f"Do not proceed with a partial corpus.")
        counts, out = run_validator(files)
        if counts is None:
            failures.append(f"reference: validator did not run.\n{out[:400]}")
        else:
            got_e, got_w = counts
            want_e, want_w = expected["reference"]["errors"], expected["reference"]["warnings"]
            if (got_e, got_w) != (want_e, want_w):
                failures.append(
                    f"reference: {got_e} error(s), {got_w} warning(s) — expected "
                    f"{want_e}/{want_w}.\n"
                    f"      These {len(files)} screens compiled in Studio. If a rule you added "
                    f"fires on them,\n      the rule is wrong. Ground truth outranks a "
                    f"plausible inference, every time.")
            else:
                notes.append(f"reference   {len(files)} screens   {got_e} err, {got_w} warn   OK")

    # --- field output and probes, checked one file at a time ----------------------------
    for kind in ("field", "probes"):
        base = resolve(kind)
        for name, want in expected.get(kind, {}).items():
            path = (base / name) if base else None
            if path is None or not path.is_file():
                failures.append(f"{kind}: missing {name}")
                continue
            counts, out = run_validator([path])
            if counts is None:
                failures.append(f"{kind}/{name}: validator did not run.\n{out[:400]}")
                continue
            got_e, got_w = counts
            if (got_e, got_w) != (want["errors"], want["warnings"]):
                failures.append(
                    f"{kind}/{name}: {got_e} error(s), {got_w} warning(s) — expected "
                    f"{want['errors']}/{want['warnings']}.\n      {want.get('why', '')}")
            else:
                notes.append(f"{kind:<11} {name:<32} {got_e} err, {got_w} warn   OK")

    if args.verbose or not failures:
        for n in notes:
            print(f"  {n}")

    print()
    if failures:
        print("=" * 74)
        print(f"FAIL — {len(failures)} check(s) did not pass")
        print("=" * 74)
        for f in failures:
            print(f"\n  {f}")
        print("\n  Do not package this skill. Fix the change, or — if the new behaviour is")
        print("  deliberate — update tests/expected.json and say plainly what changed and why.")
        return 1

    print("PASS — the skill still behaves the way it did before your edit.")
    print("\nThis proves you did not break the known cases. It does not prove your new rule is")
    print("correct. For that, add a probe under tests/probes/ that fails without your change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
