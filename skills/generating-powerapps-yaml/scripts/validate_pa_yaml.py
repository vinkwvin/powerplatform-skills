#!/usr/bin/env python3
"""Validate a Power Apps Canvas .pa.yaml against conventions measured from 17 screens
that compiled in Studio.

Every rule here is backed by a count over those screens, recorded in
ledger/01-observed-conventions.md. Rules with no measurement behind them are not enforced.

ERROR   will break the paste, or contradicts all 17 working screens
WARN    departs from the working set; usually wrong, occasionally deliberate

Exit codes:  0 = no errors   1 = at least one ERROR   2 = usage or parse failure

Usage:  python3 scripts/validate_pa_yaml.py Screen.pa.yaml [more.pa.yaml ...]
"""
import re
import sys
import pathlib

import yaml

# ---- the confirmed catalog: 9 types, exact versions, 2,830 controls, no others ----
CATALOG = {
    "Label@2.5.1", "GroupContainer@1.5.0", "Classic/Button@2.2.0",
    "Classic/CheckBox@2.1.0", "Classic/Icon@2.5.0", "Classic/TextInput@2.3.2",
    "Gallery@2.15.0", "Classic/Radio@2.3.0", "Classic/DropDown@2.3.1",
}
BARE_ONLY = {"Label", "Gallery", "GroupContainer"}   # never take a Classic/ prefix
SCREEN_PROPS = {"Fill", "LoadingSpinnerColor", "OnVisible"}          # 17/17 screens
LABEL_REQUIRED = {"Color", "FillPortions", "Height", "Size", "Text", "VerticalAlign"}
BUTTON_REQUIRED = {"Align", "Color", "Fill", "FocusedBorderThickness", "FontWeight",
                   "Height", "HoverColor", "HoverFill", "OnSelect", "PressedColor",
                   "PressedFill", "Size", "Text", "Width"}
SIZE_SET = {8, 9, 10, 11, 12, 13, 15, 16, 20, 22, 26}               # 1,829 uses
ITEMS_PAIR = {"Classic/DropDown@2.3.1", "Classic/Radio@2.3.0"}
ICON_ENUM = {"Icon.Document", "Icon.View", "Icon.Person",
             "Icon.Clock", "Icon.Publish", "Icon.Trash"}
NUM_RE = re.compile(r"^=(\d+)$")

errors, warns = [], []


def err(loc, msg):
    errors.append(f"ERROR  {loc}: {msg}")


def warn(loc, msg):
    warns.append(f"WARN   {loc}: {msg}")


def items(node):
    """(key, value_node) pairs of a MappingNode, in document order."""
    return [(k.value, v) for k, v in node.value]


def block_needed(text):
    """Does this scalar value require a | block scalar? 119/119 real ones did."""
    return ("\n" in text.strip()) or (": " in text) or (" #" in text)


def check_properties(loc, ctrl, node, is_screen=False):
    keys, seen = [], set()
    props = {}
    for key, vnode in items(node):
        if key in seen:
            err(f"{loc}.Properties", f"duplicate key {key!r}")
        seen.add(key)
        keys.append(key)
        props[key] = vnode

        if isinstance(vnode, yaml.MappingNode):
            err(f"{loc}.Properties.{key}",
                "flow-style mapping — commas inside RGBA(...) break flow style; "
                "use block style")
            continue
        if not isinstance(vnode, yaml.ScalarNode):
            continue
        val = vnode.value

        if val and not val.lstrip().startswith("="):
            warn(f"{loc}.Properties.{key}", f"value does not start with '=' ({val[:30]!r})")
        if vnode.style == "|":
            if not block_needed(val):
                warn(f"{loc}.Properties.{key}",
                     "block scalar with no ': ', newline or ' #' — 0 of 119 real block "
                     "scalars were decorative")
        elif block_needed(val):
            why = "': '" if ": " in val else ("' #'" if " #" in val else "a newline")
            err(f"{loc}.Properties.{key}",
                f"value contains {why} but is not a | block scalar — YAML will mis-parse "
                f"this and the paste breaks")
        if "DropShadow.Light" in val:
            err(f"{loc}.Properties.{key}",
                "DropShadow.Light does not exist — use DropShadow.None or omit DropShadow")
        if key == "Size":
            m = NUM_RE.match(val.strip())
            if m and int(m.group(1)) not in SIZE_SET:
                warn(f"{loc}.Properties.Size",
                     f"{val} is outside the measured set {sorted(SIZE_SET)} "
                     f"(floor 8, ceiling 26)")
        if key == "FocusedBorderThickness" and val.strip() == "=0":
            warn(f"{loc}.Properties.FocusedBorderThickness",
                 "never 0 in 289 real interactive controls — always 1, occasionally 2")
        if key == "Icon" and val.strip().lstrip("=").strip() not in ICON_ENUM:
            warn(f"{loc}.Properties.Icon",
                 f"{val} is not one of the six confirmed members {sorted(ICON_ENUM)} — "
                 f"mark UNVERIFIED and ask before shipping")

    lowered = [k.lower() for k in keys]
    if lowered != sorted(lowered):
        bad = next((f"{keys[i]!r} before {keys[i+1]!r}"
                    for i in range(len(lowered) - 1) if lowered[i] > lowered[i + 1]), "?")
        err(f"{loc}.Properties",
            f"properties not alphabetised ({bad}) — 2,847/2,847 real blocks are sorted")

    if is_screen:
        missing = SCREEN_PROPS - set(keys)
        for m in sorted(missing):
            err(f"{loc}.Properties", f"screen is missing {m} — present on 17/17 screens")
        for extra in sorted(set(keys) - SCREEN_PROPS):
            warn(f"{loc}.Properties", f"{extra} — no real screen carries a fourth property")
    return props


def check_control(loc, name, body, depth):
    fields = dict(items(body))
    if "Control" not in fields:
        err(f"{loc}", "control has no Control: key")
        return
    ctrl = fields["Control"].value.strip()

    if ctrl not in CATALOG:
        base = ctrl.split("@")[0]
        if base in BARE_ONLY or f"Classic/{base}" in {c.split('@')[0] for c in CATALOG}:
            err(f"{loc}({name})",
                f"{ctrl} is not in the confirmed catalog. Bare Label/Gallery/GroupContainer, "
                f"Classic/ on everything interactive, exact versions: {sorted(CATALOG)}")
        else:
            err(f"{loc}({name})",
                f"{ctrl} is not a confirmed control type. Mark it '# UNVERIFIED' and ask "
                f"before shipping — an invented control type is the top cause of paste failure")

    if ctrl == "GroupContainer@1.5.0":
        variant = fields.get("Variant")
        if variant is None or variant.value.strip() != "AutoLayout":
            err(f"{loc}({name})",
                "GroupContainer needs 'Variant: AutoLayout' — 887/887 real containers have it")
    if ctrl == "Gallery@2.15.0":
        variant = fields.get("Variant")
        if variant is None or variant.value.strip() != "Vertical":
            warn(f"{loc}({name})", "Gallery Variant is 'Vertical' on 36/36 real galleries")

    props = {}
    if "Properties" in fields and isinstance(fields["Properties"], yaml.MappingNode):
        props = check_properties(f"{loc}({name})", ctrl, fields["Properties"])

    pk = set(props)
    if depth > 1:
        for coord in ("X", "Y"):
            if coord in pk:
                err(f"{loc}({name}).Properties.{coord}",
                    f"{coord} appears only on the depth-1 root container in the real screens "
                    f"(0 of 2,813 nested controls declare it). Position with AutoLayout")
    if ctrl in ITEMS_PAIR:
        for req in ("Items", "Items.Value"):
            if req not in pk:
                err(f"{loc}({name}).Properties",
                    f"{ctrl} needs both Items and Items.Value — missing {req}. "
                    f"Omitting Items.Value is a silent failure")
    if ctrl == "Label@2.5.1":
        for m in sorted(LABEL_REQUIRED - pk):
            warn(f"{loc}({name}).Properties", f"Label missing {m} — 1,370/1,370 carry it")
    if ctrl == "Classic/Button@2.2.0":
        for m in sorted(BUTTON_REQUIRED - pk):
            warn(f"{loc}({name}).Properties", f"Button missing {m} — 268/268 carry it")
    if ctrl == "GroupContainer@1.5.0":
        for m in ("Height", "LayoutMinHeight"):
            if m not in pk:
                warn(f"{loc}({name}).Properties",
                     f"container missing {m} — 887/887 carry both, or rows collapse")
    if ctrl == "Gallery@2.15.0":
        for m in ("Height", "Items", "LayoutMinHeight", "TemplateSize"):
            if m not in pk:
                warn(f"{loc}({name}).Properties", f"Gallery missing {m} — 36/36 carry it")

    if "Children" in fields and isinstance(fields["Children"], yaml.SequenceNode):
        walk_children(f"{loc}({name})", fields["Children"], depth + 1)


def walk_children(loc, seq, depth):
    for i, item in enumerate(seq.value):
        if not isinstance(item, yaml.MappingNode):
            err(f"{loc}.Children[{i}]", "each child must be a single-key mapping '- Name:'")
            continue
        for name, body in items(item):
            if isinstance(body, yaml.MappingNode):
                check_control(f"{loc}.Children[{i}]", name, body, depth)
            else:
                err(f"{loc}.Children[{i}]({name})", "control body must be a mapping")


def validate(path):
    raw = path.read_text(encoding="utf-8")

    for n, line in enumerate(raw.splitlines(), 1):
        indent = line[: len(line) - len(line.lstrip())]
        if "\t" in indent:
            err(f"{path.name}:{n}", "tab in leading whitespace — breaks the paste. Spaces only")

    try:
        yaml.safe_load(raw)
    except yaml.YAMLError as e:
        err(path.name, f"does not parse as YAML: {str(e).splitlines()[0]}")
        return
    root = yaml.compose(raw)
    if not isinstance(root, yaml.MappingNode):
        err(path.name, "top level must be a mapping")
        return
    top = dict(items(root))
    if "Screens" not in top:
        err(path.name, "no top-level 'Screens:' key — Studio needs the full schema, "
                       "not a bare control list")
        return
    for sname, screen in items(top["Screens"]):
        loc = f"{path.name}[{sname}]"
        sf = dict(items(screen))
        if "Properties" in sf and isinstance(sf["Properties"], yaml.MappingNode):
            check_properties(loc, None, sf["Properties"], is_screen=True)
        else:
            err(loc, "screen has no Properties block")
        if "Children" in sf and isinstance(sf["Children"], yaml.SequenceNode):
            walk_children(loc, sf["Children"], 1)
        else:
            err(loc, "screen has no Children block")


def main():
    paths = [pathlib.Path(a) for a in sys.argv[1:]]
    if not paths:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    for p in paths:
        if not p.is_file():
            print(f"No such file: {p}", file=sys.stderr)
            return 2
        validate(p)
    for line in errors + warns:
        print(line)
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s).")
    if errors:
        print("Do not paste this into Studio. Fix every ERROR and re-run.")
        return 1
    print("Clean. Safe to paste into Power Apps Studio.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
