#!/usr/bin/env python3
"""Read every field report in feedback/ and produce a ranked action list.

Turns a pile of reports into an ordered agenda, so an intake round starts from evidence
rather than from whichever report was read last. See docs/IMPROVING-SKILLS.md.

Ranking, highest first:
    1  caught_by: studio            reached a real paste — the validator failed
    2  same element, 2+ reporters   independent corroboration beats one loud report
    3  present-and-ignored          the rule exists and did not land; fixable without adding length
    4  times >= 3                   meets the project's existing bar for an inline rule
    5  present-but-wrong            actively misleading
    6  absent, single report         real, and the easiest kind to over-act on

Usage:
    python3 scripts/triage_feedback.py
    python3 scripts/triage_feedback.py --skill generating-powerapps-yaml
    python3 scripts/triage_feedback.py --metrics
"""
import argparse
import pathlib
import re
import sys
from collections import Counter, defaultdict

import yaml

FEEDBACK = pathlib.Path(__file__).resolve().parent.parent / "feedback"
YAML_BLOCK = re.compile(r"```ya?ml\s*\n(.*?)```", re.S)

# A field report is YAML written by hand, and its most useful values are code snippets that
# contain colons — `wrong: Control: Image@2.2.0`. That is a YAML parse error. Rather than
# discard the report, quote the value and carry on: a lost report is a teammate's two minutes
# thrown away, and they stop filing.
SCALAR_WITH_COLON = re.compile(
    r"^(?P<indent>\s*(?:-\s+)?)(?P<key>[A-Za-z_][\w.]*):[ \t]+(?P<val>(?![\[{|>&*!'\"])"
    r"[^\n]*?:\s[^\n]*?)\s*$")


def repair_colons(block):
    """Quote any scalar value that contains a colon-space, so the record parses."""
    out = []
    for line in block.splitlines():
        m = SCALAR_WITH_COLON.match(line)
        if m and '"' not in m.group("val") and "#" not in m.group("val"):
            out.append(f'{m.group("indent")}{m.group("key")}: "{m.group("val").strip()}"')
        else:
            out.append(line)
    return "\n".join(out)


def load_reports(root, only_skill=None):
    reports, skipped, auto_fixed = [], [], []
    for path in sorted(root.rglob("*.md")):
        if path.name.upper().startswith(("README", "UPLOAD-HERE")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        blocks = YAML_BLOCK.findall(text)
        if not blocks:
            # a record may be plain YAML with no fence
            blocks = [text]
        parsed, why_failed, repaired = None, [], False
        for b in blocks:
            for candidate, is_repair in ((b, False), (repair_colons(b), True)):
                try:
                    d = yaml.safe_load(candidate)
                except yaml.YAMLError as e:
                    if not is_repair:
                        why_failed.append(str(e).splitlines()[0])
                    continue
                if isinstance(d, dict) and ("fixes" in d or "meta" in d):
                    parsed, repaired = d, is_repair
                    break
            if parsed is not None:
                break
        if parsed is None:
            # Never skip a report silently: a teammate who files and sees nothing happen
            # stops filing, and that input is lost permanently.
            skipped.append((path, why_failed))
            continue
        skill = (parsed.get("meta") or {}).get("skill") or path.parent.name
        if only_skill and skill != only_skill:
            continue
        artifact = next((p for p in path.parent.iterdir()
                         if p.stem == path.stem and p.suffix != ".md"), None)
        # An artifact good enough to promote straight to a regression fixture lives in evals/,
        # not here — and copying it back would just create two files that drift. A record may
        # name where it went instead, so doing the better thing is not scored as filing nothing.
        if artifact is None and parsed.get("artifact_at"):
            named = (root.parent / str(parsed["artifact_at"])).resolve()
            artifact = named if named.exists() else None
        parsed["_path"] = path
        parsed["_skill"] = skill
        parsed["_artifact"] = artifact
        parsed["_reporter"] = path.stem
        parsed["_repaired"] = repaired
        reports.append(parsed)
        if repaired:
            auto_fixed.append(path)

    if auto_fixed:
        print(f"note: auto-quoted colon-space values in {len(auto_fixed)} report(s) so they "
              f"would parse: " + ", ".join(p.name for p in auto_fixed))
        print("      (the record is YAML too — quote values like \"Control: Image@2.2.0\")\n")
    if skipped:
        print("=" * 78)
        print(f"UNREADABLE — {len(skipped)} report(s) could not be parsed")
        print("=" * 78)
        for path, whys in skipped:
            print(f"\n  {path.name}")
            for w in whys or ["no YAML block found in the file"]:
                print(f"    {w}")
            print("    Most likely cause: a value containing ': ' was not quoted. In YAML a")
            print("    colon-space starts a nested mapping, so `wrong: Control: Image@2.2.0`")
            print("    is a parse error. Quote it: `wrong: \"Control: Image@2.2.0\"`")
        print("\n  Fix these and re-run. Do NOT leave them unread — an unreadable report is")
        print("  a teammate's two minutes thrown away, and they will notice.\n")
    return reports


def rule_status(fix):
    """`present_and_ignored` and `present-and-ignored` are the same verdict.

    Underscores are what field reports actually come back with, and an unrecognised status
    ranks last — so the highest-value finding in the first real report, a `present_and_ignored`,
    sorted below every routine gap. Normalise instead of asking people to spell it our way.
    """
    return str(fix.get("rule_status") or "").strip().lower().replace("_", "-")


def priority(fix, reporters_for_element):
    if fix.get("caught_by") == "studio":
        return 1, "reached a real paste — validator gap"
    if reporters_for_element > 1:
        return 2, f"reported independently by {reporters_for_element} sources"
    status = rule_status(fix)
    if status == "present-and-ignored":
        return 3, "rule exists and did not land — fix placement or wording, not length"
    try:
        if int(fix.get("times") or 0) >= 3:
            return 4, f"corrected {fix['times']}x in one session"
    except (TypeError, ValueError):
        pass
    if status == "present-but-wrong":
        return 5, "rule is actively misleading"
    if status == "absent":
        return 6, "gap, single report — resist adding length reflexively"
    return 7, "unclassified"


ACTION = {
    "absent": "ADD a rule",
    "present-but-wrong": "CORRECT the rule (and audit the reference it came from)",
    "present-and-ignored": "MOVE or REWRITE the rule — do not add a second one",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill")
    ap.add_argument("--metrics", action="store_true", help="print metrics only")
    ap.add_argument("--root", default=str(FEEDBACK))
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    if not root.is_dir():
        print(f"No feedback directory at {root}", file=sys.stderr)
        return 2
    reports = load_reports(root, args.skill)
    if not reports:
        print("No field reports filed yet.\n")
        print("Ask the team to paste prompts/feedback-session.md at the end of their next")
        print("working chat. Two minutes each, and it is the only thing that keeps these")
        print("skills from going stale. See docs/IMPROVING-SKILLS.md.")
        return 0

    # ---- metrics ----
    by_skill = defaultdict(list)
    for r in reports:
        by_skill[r["_skill"]].append(r)

    print("=" * 78)
    print("METRICS")
    print("=" * 78)
    for skill, rs in sorted(by_skill.items()):
        rounds = [int(r["meta"]["rounds"]) for r in rs
                  if str((r.get("meta") or {}).get("rounds", "")).isdigit()]
        caught = Counter(f.get("caught_by") for r in rs for f in (r.get("fixes") or []))
        total = sum(caught.values())
        by_val = caught.get("validator", 0) + caught.get("you-self-corrected", 0)
        first_ok = sum(1 for r in rs
                       if (r.get("meta") or {}).get("first_attempt_validated") is True)
        print(f"\n{skill}   {len(rs)} report(s)")
        if rounds:
            rounds.sort()
            med = rounds[len(rounds) // 2]
            print(f"  rounds-to-clean:      median {med}  (range {rounds[0]}-{rounds[-1]})"
                  f"   ← want this falling")
        if total:
            print(f"  caught in sandbox:    {by_val}/{total} = {100*by_val//total}%"
                  f"   ← want this rising")
            if caught.get("studio"):
                print(f"  reached Studio broken: {caught['studio']}"
                      f"   ← each one is a validator gap")
        print(f"  first attempt clean:  {first_ok}/{len(rs)}")
        no_artifact = [r["_path"].name for r in rs if not r["_artifact"]]
        if no_artifact:
            print(f"  no artifact filed:    {len(no_artifact)} "
                  f"(cannot promote a rule on its own): {', '.join(no_artifact[:3])}")
    if args.metrics:
        return 0

    # ---- verbatim platform errors ----
    # Ranked first because each one is a candidate static check, and a check outranks a rule:
    # a rule tells a model what to do, a check stops the artifact regardless of what it read.
    # Both errors in the first field report became checks; nothing else in that report did.
    errs = [(r["_skill"], e) for r in reports for e in (r.get("studio_errors_verbatim") or [])]
    if errs:
        print("\n" + "=" * 78)
        print(f"VERBATIM PLATFORM ERRORS — {len(errs)}, each a candidate validator check")
        print("=" * 78)
        for skill, e in errs:
            print(f"\n  [{skill}] {e}")
        print("\n  Can a static check catch this before the paste? If yes, write it before")
        print("  touching any rule text.")

    # ---- corroboration across reports ----
    element_reporters = defaultdict(set)
    for r in reports:
        for f in r.get("fixes") or []:
            key = (r["_skill"], str(f.get("element", "")).strip().lower())
            element_reporters[key].add(r["_reporter"])

    rows = []
    for r in reports:
        for f in r.get("fixes") or []:
            key = (r["_skill"], str(f.get("element", "")).strip().lower())
            n_rep = len(element_reporters[key])
            p, why = priority(f, n_rep)
            if n_rep > 1 and p == 1:
                why += f" · ALSO reported by {n_rep} independent sources"
            rows.append((p, why, r, f))
    rows.sort(key=lambda t: (t[0], -(int(t[3].get("times") or 0)
                                     if str(t[3].get("times") or "").isdigit() else 0)))

    print("\n" + "=" * 78)
    print(f"RANKED ACTIONS — {len(rows)} finding(s)")
    print("=" * 78)
    tiers = Counter(str(f.get("tier", "unclear")) for _, _, _, f in rows)
    print(f"tiers: " + "  ".join(f"{k}={v}" for k, v in tiers.most_common()))
    if tiers.get("unclear"):
        print(f"  {tiers['unclear']} finding(s) with an unclear tier — assign one before "
              f"changing anything (docs/EVIDENCE-TIERS.md)")

    last_p = None
    for p, why, r, f in rows:
        if p != last_p:
            print(f"\n--- priority {p} ---")
            last_p = p
        status = rule_status(f) or "?"
        print(f"\n[{r['_skill']}] {f.get('element', '?')}")
        print(f"   why here: {why}")
        print(f"   tier: {f.get('tier','unclear')}   status: {status}   "
              f"caught_by: {f.get('caught_by','?')}   times: {f.get('times','?')}")
        print(f"   wrong: {str(f.get('wrong',''))[:110]}")
        print(f"   right: {str(f.get('right',''))[:110]}")
        if f.get("rule_quote"):
            print(f"   quoted rule: {str(f['rule_quote'])[:110]}")
        print(f"   ACTION: {ACTION.get(status, 'classify rule_status first')}")
        if f.get("caught_by") == "studio":
            print(f"   ALSO: add a validator check — this one got past the gate")
        print(f"   source: {r['_path'].name}"
              + (f"  artifact: {r['_artifact'].name}" if r["_artifact"] else "  (NO ARTIFACT)"))

    conf = [x for r in reports for x in (r.get("unverified_confirmed") or [])]
    if conf:
        print("\n" + "=" * 78)
        print("CATALOG GROWTH — previously UNVERIFIED, now accepted by the platform")
        print("=" * 78)
        for c in conf:
            print(f"  + {c}")
        print("  Add these to the relevant catalog or house-style.yaml. This is how the")
        print("  confirmed set grows without anyone guessing.")

    # ---- the free-text answer ----
    # Read this even when the ranked list above is empty. The first field report filed
    # `repeated_corrections: []` and every fix held first time, so every structured metric here
    # scored it clean — while the actual defect was the validator's success message claiming a
    # clean run meant a correct screen. One blind spot presenting three times, not one mistake
    # repeated. No structured field would have surfaced it; this one did.
    misses = [(r["_skill"], r["_path"].name, str(r[k]).strip())
              for r in reports for k in ("biggest_miss", "biggest_single_miss")
              if r.get(k)]
    if misses:
        print("\n" + "=" * 78)
        print("BIGGEST MISS — free text. Read every one, including on a quiet round.")
        print("=" * 78)
        for skill, src, text in misses:
            print(f"\n  [{skill}] {src}")
            for line in text.splitlines():
                print(f"    {line}")

    print("\n" + "=" * 78)
    print("Reminders: validator gaps before rule edits · every confirmed fix gets an eval ·")
    print("report what you did NOT act on and why · bump the version, write the CHANGELOG,")
    print("and tell the team to re-install (skills do not sync).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
