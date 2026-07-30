#!/usr/bin/env python3
"""
validate_pa_yaml.py — lint Power Apps Canvas source YAML (pa.yaml) against the
environment conventions encoded by the `powerapps-yaml` skill.

Stdlib only — no install, runs anywhere Python 3 does.

Usage:
    python3 validate_pa_yaml.py <file.pa.yaml> [more.pa.yaml ...]
    cat Screen.pa.yaml | python3 validate_pa_yaml.py -

Exit code: 0 if no ERRORs, 1 if any ERROR was found. WARNs never fail the run.

What it checks (see references/yaml-conventions.md for the why):
  ERROR  tabs used for indentation
  ERROR  wrong bare/Classic choice (Label/Gallery must be bare; Button/TextInput/
         DropDown/Icon/Radio/CheckBox must be Classic/)
  ERROR  DropDown/Radio has `Items:` but is missing the `Items.Value:` companion
  ERROR  a property value contains ': ' or ' #' but isn't a block scalar (|)
  WARN   a screen has no LoadingSpinnerColor
  WARN   properties inside a Properties: block aren't alphabetized
  WARN   DropShadow.Light used (omit DropShadow on elevated cards instead)
  WARN   Radio missing Layout / RadioSize
  WARN   a known control uses an off-book version string
"""

import re
import sys

# Verified control versions for this environment.
EXPECTED_VERSION = {
    "Label": "2.5.1",
    "Gallery": "2.15.0",
    "Classic/Button": "2.2.0",
    "Classic/TextInput": "2.3.2",
    "Classic/DropDown": "2.3.1",
    "Classic/Icon": "2.5.0",
    "Classic/Radio": "2.3.0",
    "GroupContainer": "1.5.0",
}
MUST_BE_BARE = {"Label", "Gallery"}          # base name must NOT carry Classic/
MUST_BE_CLASSIC = {"Button", "TextInput", "DropDown", "Icon", "Radio", "CheckBox"}

CONTROL_RE = re.compile(r"^\s*Control:\s*([A-Za-z0-9/_]+)@([0-9][0-9.]*)\s*(?:#.*)?$")
KEY_RE = re.compile(r"^(\s*)([A-Za-z0-9_.]+):(\s.*)?$")
SCALAR_INTRO_RE = re.compile(r"^\s*[A-Za-z0-9_.]+:\s*[|>][+-]?\s*(?:#.*)?$")
SCREEN_KEYWORDS = {"Properties", "Children", "Control", "Variant"}


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


class Finding:
    __slots__ = ("level", "line", "msg")

    def __init__(self, level, line, msg):
        self.level = level
        self.line = line
        self.msg = msg


def annotate_block_scalars(lines):
    """Return a list of flags per line: 'intro', 'content', or 'normal'."""
    flags = ["normal"] * len(lines)
    in_scalar = False
    scalar_indent = 0
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        stripped = line.strip()
        if in_scalar:
            if stripped == "":
                flags[i] = "content"
                continue
            if indent_of(line) > scalar_indent:
                flags[i] = "content"
                continue
            in_scalar = False  # dedented out; fall through to classify this line
        if SCALAR_INTRO_RE.match(line):
            flags[i] = "intro"
            in_scalar = True
            scalar_indent = indent_of(line)
    return flags


def check_tabs(lines, findings):
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        lead = line[: len(line) - len(line.lstrip(" \t"))]
        if "\t" in lead:
            findings.append(Finding("ERROR", i + 1, "tab in indentation — use spaces only"))


def check_controls(lines, flags, findings):
    """Validate each Control: line and the DropDown/Radio companion props."""
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        m = CONTROL_RE.match(line)
        if not m:
            continue
        full, version = m.group(1), m.group(2)
        base = full.split("/")[-1]
        is_classic = full.startswith("Classic/")

        if base in MUST_BE_BARE and is_classic:
            findings.append(Finding(
                "ERROR", i + 1,
                f"{base} must be bare ({base}@{EXPECTED_VERSION.get(base,'?')}), not Classic/{base}"))
        if base in MUST_BE_CLASSIC and not is_classic:
            findings.append(Finding(
                "ERROR", i + 1,
                f"{base} must be Classic/{base}@{EXPECTED_VERSION.get('Classic/'+base,'?')} "
                f"(bare {base} is the modern control and rejects Color/Fill/Size)"))

        key = full if is_classic else base
        expected = EXPECTED_VERSION.get(key)
        if expected and version != expected:
            findings.append(Finding(
                "WARN", i + 1,
                f"{full} is @{version}; verified version is @{expected}"))

        # DropDown/Radio companion-property checks, scoped to this control's block.
        if base in ("DropDown", "Radio"):
            ctrl_indent = indent_of(line)
            name_indent = ctrl_indent - 2  # the "- Name:" line sits 2 shallower
            has_items = has_items_value = has_layout = has_radiosize = False
            j = i + 1
            while j < len(lines):
                l2 = lines[j].rstrip("\n")
                if l2.strip() == "":
                    j += 1
                    continue
                if indent_of(l2) <= name_indent:  # dedented out of this control
                    break
                if flags[j] != "content":
                    s = l2.strip()
                    if s.startswith("Items.Value:"):
                        has_items_value = True
                    elif s.startswith("Items:"):
                        has_items = True
                    elif s.startswith("Layout:"):
                        has_layout = True
                    elif s.startswith("RadioSize:"):
                        has_radiosize = True
                j += 1
            if has_items and not has_items_value:
                findings.append(Finding(
                    "ERROR", i + 1,
                    f"{base} has Items: but is missing the required 'Items.Value: =Value' companion"))
            if base == "Radio":
                if not has_layout:
                    findings.append(Finding("WARN", i + 1, "Radio missing 'Layout: =Layout.Horizontal'"))
                if not has_radiosize:
                    findings.append(Finding("WARN", i + 1, "Radio missing 'RadioSize: =30'"))


def check_block_scalar_needed(lines, flags, findings):
    for i, raw in enumerate(lines):
        if flags[i] != "normal":
            continue
        line = raw.rstrip("\n")
        m = KEY_RE.match(line)
        if not m:
            continue
        rest = m.group(3) or ""
        val = rest.strip()
        if not val or val in ("|", ">") or val.startswith("|") or val.startswith(">"):
            continue
        # A fully YAML-quoted scalar is safe; Power Fx values start with '=' (plain scalar) and aren't.
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            continue
        if ": " in val:
            findings.append(Finding(
                "ERROR", i + 1,
                "value contains ': ' (colon-space) — wrap it in a block scalar (Key: |)"))
        elif " #" in val:
            findings.append(Finding(
                "ERROR", i + 1,
                "value contains ' #' (YAML reads it as a comment) — wrap it in a block scalar (Key: |)"))


def check_dropshadow_light(lines, flags, findings):
    for i, raw in enumerate(lines):
        if flags[i] == "content":
            continue
        if "DropShadow.Light" in raw:
            findings.append(Finding(
                "WARN", i + 1,
                "DropShadow.Light — omit DropShadow entirely on elevated white cards (default is correct)"))


def check_screens_have_spinner(lines, findings):
    screens_indent = None
    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip() == "Screens:" or re.match(r"^\s*Screens:\s*$", line):
            screens_indent = indent_of(line)
            break
    if screens_indent is None:
        return  # not a full Screens: file; nothing to check
    name_indent = screens_indent + 2
    screen_starts = []  # (line_index, name)
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        if indent_of(line) != name_indent:
            continue
        stripped = line.strip()
        if not stripped.endswith(":"):
            continue
        name = stripped[:-1].strip()
        if name in SCREEN_KEYWORDS or name.startswith("- "):
            continue
        screen_starts.append((i, name))
    for idx, (start, name) in enumerate(screen_starts):
        end = screen_starts[idx + 1][0] if idx + 1 < len(screen_starts) else len(lines)
        block = "".join(lines[start:end])
        if "LoadingSpinnerColor" not in block:
            findings.append(Finding(
                "WARN", start + 1,
                f"screen '{name}' has no LoadingSpinnerColor (add =RGBA(56, 96, 178, 1))"))


def check_alpha_sort(lines, flags, findings):
    """Within each Properties: block, the immediate child keys should be alphabetized."""
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip("\n")
        if line.strip() == "Properties:" or re.match(r"^\s*Properties:\s*$", line):
            prop_indent = indent_of(line)
            child_indent = prop_indent + 2
            prev_key = None
            reported = False
            j = i + 1
            while j < n:
                l2 = lines[j].rstrip("\n")
                if l2.strip() == "":
                    j += 1
                    continue
                if indent_of(l2) <= prop_indent:
                    break  # end of this Properties block
                if flags[j] == "content":
                    j += 1
                    continue
                if indent_of(l2) == child_indent:
                    km = KEY_RE.match(l2)
                    if km:
                        key = km.group(2)
                        if prev_key is not None and key.lower() < prev_key.lower() and not reported:
                            findings.append(Finding(
                                "WARN", j + 1,
                                f"properties not alphabetized: '{key}' should come before '{prev_key}'"))
                            reported = True
                        prev_key = key
                j += 1
            i = j
            continue
        i += 1


def validate(lines):
    flags = annotate_block_scalars(lines)
    findings = []
    check_tabs(lines, findings)
    check_controls(lines, flags, findings)
    check_block_scalar_needed(lines, flags, findings)
    check_dropshadow_light(lines, flags, findings)
    check_screens_have_spinner(lines, findings)
    check_alpha_sort(lines, flags, findings)
    findings.sort(key=lambda f: (f.line, 0 if f.level == "ERROR" else 1))
    return findings


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: validate_pa_yaml.py <file.pa.yaml> [...]  (or - for stdin)", file=sys.stderr)
        return 2

    total_errors = 0
    for path in paths:
        if path == "-":
            lines = sys.stdin.readlines()
            label = "<stdin>"
        else:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    lines = fh.readlines()
            except OSError as exc:
                print(f"{path}: cannot read ({exc})", file=sys.stderr)
                total_errors += 1
                continue
            label = path

        findings = validate(lines)
        errors = sum(1 for f in findings if f.level == "ERROR")
        warns = sum(1 for f in findings if f.level == "WARN")
        total_errors += errors

        print(f"\n=== {label} ===")
        if not findings:
            print("  OK — no issues found.")
        else:
            for f in findings:
                print(f"  {f.level:<5} line {f.line}: {f.msg}")
        print(f"  {errors} error(s), {warns} warning(s)")

    print(f"\nDone. {total_errors} error(s) total.")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
