#!/usr/bin/env python3
"""Validate a Power Apps Canvas .pa.yaml before it is pasted into Studio.

Two classes of rule, and the difference matters (see docs/EVIDENCE-TIERS.md):

  PLATFORM  a fact about Power Apps. Violating it produces a failure the platform itself
            generates. Hard-coded here, reported as ERROR, never overridable.
  HOUSE     a convention this organisation adopted. Reported as WARN, and every number
            lives in assets/house-style.yaml so a project with a different design system
            edits one file instead of this script.

Exit codes:  0 = no PLATFORM errors   1 = at least one ERROR   2 = usage or parse failure

Usage:
    python3 scripts/validate_pa_yaml.py Screen.pa.yaml [more.pa.yaml ...]
    python3 scripts/validate_pa_yaml.py --style path/to/house-style.yaml Screen.pa.yaml
    python3 scripts/validate_pa_yaml.py --platform-only Screen.pa.yaml
"""
import re
import sys
import pathlib

import yaml

# ============================ PLATFORM ============================
# Power Apps facts. Not configurable.

CATALOG = {
    "Label@2.5.1", "GroupContainer@1.5.0", "Classic/Button@2.2.0",
    "Classic/CheckBox@2.1.0", "Classic/Icon@2.5.0", "Classic/TextInput@2.3.2",
    "Gallery@2.15.0", "Classic/Radio@2.3.0", "Classic/DropDown@2.3.1",
}
BARE_TYPES = {"Label", "Gallery", "GroupContainer"}
ITEMS_PAIR = {"Classic/DropDown@2.3.1", "Classic/Radio@2.3.0"}
NONEXISTENT = {"DropShadow.Light": "DropShadow.Light does not exist — use DropShadow.None, "
                                   "or omit DropShadow entirely on elevated white cards"}

DEFAULT_STYLE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "house-style.yaml"
NUM_RE = re.compile(r"^=(\d+)$")
# Enum.Member as it appears in a formula. Excludes Parent./Self./ThisItem./App. property
# access, which is the same shape but is not an enum.
ENUM_RE = re.compile(r"\b(?<!\.)([A-Z][A-Za-z]+)\.([A-Z][A-Za-z]+)\b")

errors, warns = [], []
STYLE = {}
PLATFORM_ONLY = False


def err(loc, msg):
    errors.append(f"ERROR  [PLATFORM] {loc}: {msg}")


def warn(loc, msg, section=None):
    """HOUSE warning. Suppressed when the relevant style section is disabled."""
    if PLATFORM_ONLY:
        return
    if section and not STYLE.get(section, {}).get("enforce", True):
        return
    warns.append(f"WARN   [HOUSE]    {loc}: {msg}")


def sect(name, key, default=None):
    return STYLE.get(name, {}).get(key, default)


def items(node):
    return [(k.value, v) for k, v in node.value]


def block_needed(text):
    """PLATFORM: YAML itself requires a block scalar for these."""
    return ("\n" in text.strip()) or (": " in text) or (" #" in text)


# ============================ checks ============================

def check_properties(loc, ctrl, node, is_screen=False):
    keys, seen, props = [], set(), {}
    for key, vnode in items(node):
        if key in seen:
            err(f"{loc}.Properties", f"duplicate key {key!r}")
        seen.add(key)
        keys.append(key)
        props[key] = vnode

        if isinstance(vnode, yaml.MappingNode):
            err(f"{loc}.Properties.{key}",
                "flow-style mapping — commas inside RGBA(...) break flow-style parsing. "
                "Use block style")
            continue
        if not isinstance(vnode, yaml.ScalarNode):
            continue
        val = vnode.value

        # -- PLATFORM --
        if vnode.style != "|" and block_needed(val):
            why = "': '" if ": " in val else ("' #'" if " #" in val else "a newline")
            err(f"{loc}.Properties.{key}",
                f"value contains {why} but is not a | block scalar. YAML will mis-parse it "
                f"and the paste breaks")
        for bad, msg in NONEXISTENT.items():
            if bad in val:
                err(f"{loc}.Properties.{key}", msg)
        if val and not val.lstrip().startswith("="):
            err(f"{loc}.Properties.{key}",
                f"property value must start with '=' (found {val[:30]!r})")

        # -- HOUSE --
        if vnode.style == "|" and not block_needed(val):
            warn(f"{loc}.Properties.{key}",
                 "block scalar with no ': ', newline or ' #' — reference set never used | "
                 "decoratively")
        if key == "Size":
            m = NUM_RE.match(val.strip())
            allowed = sect("font_sizes", "allowed", [])
            if m and allowed and int(m.group(1)) not in allowed:
                warn(f"{loc}.Properties.Size",
                     f"{val} outside the house set {allowed} "
                     f"(floor {sect('font_sizes','floor')}, ceiling {sect('font_sizes','ceiling')})",
                     "font_sizes")
        if key == "FocusedBorderThickness":
            m = NUM_RE.match(val.strip())
            ok = sect("interactive_state", "focused_border_thickness", [])
            if m and ok and int(m.group(1)) not in ok:
                warn(f"{loc}.Properties.FocusedBorderThickness",
                     f"{val} — house style uses {ok}; a focus ring is always present, just thin",
                     "interactive_state")
        if key == "Icon":
            confirmed = sect("icons", "confirmed", [])
            v = val.strip().lstrip("=").strip()
            if confirmed and v not in confirmed:
                warn(f"{loc}.Properties.Icon",
                     f"{v} is not in the confirmed member list {confirmed}. The Icon.* enum is "
                     f"larger than this — mark '# UNVERIFIED' and paste-test it alone, then add "
                     f"it to house-style.yaml once Studio accepts it",
                     "icons")

        # Same treatment for every other enum: an unlisted member may well be valid, but
        # nobody here has pasted it, and a member that does not exist fails only in Studio.
        known = sect("enum_members", "confirmed", {}) or {}
        for enum, member in ENUM_RE.findall(val):
            if enum in known and member not in known[enum]:
                warn(f"{loc}.Properties.{key}",
                     f"{enum}.{member} is not in the confirmed member list for {enum} "
                     f"{sorted(known[enum])}. It may be valid — this enum is larger than what "
                     f"shipped here. Mark '# UNVERIFIED', paste-test that one control alone, "
                     f"then add the member to house-style.yaml",
                     "enum_members")

    # -- HOUSE: ordering --
    if sect("property_order", "mode", "alphabetical_case_insensitive") == \
            "alphabetical_case_insensitive":
        lowered = [k.lower() for k in keys]
        if lowered != sorted(lowered):
            bad = next((f"{keys[i]!r} before {keys[i+1]!r}"
                        for i in range(len(lowered) - 1) if lowered[i] > lowered[i + 1]), "?")
            warn(f"{loc}.Properties", f"properties not alphabetised ({bad})", "property_order")

    if is_screen:
        req = sect("required_properties", "screen", [])
        for m in sorted(set(req) - set(keys)):
            warn(f"{loc}.Properties", f"screen missing {m}", "required_properties")
    return props


def check_control(loc, name, body, depth):
    fields = dict(items(body))
    if "Control" not in fields:
        err(loc, "control has no Control: key")
        return
    ctrl = fields["Control"].value.strip()
    base = ctrl.split("@")[0]

    # -- PLATFORM: catalog and bare-vs-Classic --
    if ctrl not in CATALOG:
        if base.startswith("Classic/") and base.split("/", 1)[1] in BARE_TYPES:
            err(f"{loc}({name})",
                f"{ctrl} — {base.split('/',1)[1]} is a bare control and must not carry the "
                f"Classic/ prefix")
        elif base in BARE_TYPES or f"Classic/{base}" in {c.split('@')[0] for c in CATALOG}:
            err(f"{loc}({name})",
                f"{ctrl} is not a confirmed type or version. Confirmed: {sorted(CATALOG)}")
        else:
            err(f"{loc}({name})",
                f"{ctrl} is not in the confirmed catalog. It may well exist — the Power Apps "
                f"control set is larger than this list — but it is unverified here. Mark it "
                f"'# UNVERIFIED', paste-test it alone, and add it to the catalog once Studio "
                f"accepts it. Never ship an unverified type inside a full screen unflagged")

    if ctrl in ITEMS_PAIR:
        pk = set()
        if isinstance(fields.get("Properties"), yaml.MappingNode):
            pk = {k for k, _ in items(fields["Properties"])}
        for req in ("Items", "Items.Value"):
            if req not in pk:
                err(f"{loc}({name}).Properties",
                    f"{base} requires both Items and Items.Value — missing {req}. Omitting "
                    f"Items.Value renders an empty control with no error message")

    # -- HOUSE: variant --
    want_variant = sect("positioning", "container_variant")
    if ctrl == "GroupContainer@1.5.0" and want_variant:
        v = fields.get("Variant")
        if v is None or v.value.strip() != want_variant:
            warn(f"{loc}({name})", f"GroupContainer without 'Variant: {want_variant}'",
                 "positioning")

    props = {}
    if isinstance(fields.get("Properties"), yaml.MappingNode):
        props = check_properties(f"{loc}({name})", ctrl, fields["Properties"])
    pk = set(props)

    # -- HOUSE: coordinates --
    max_depth = sect("positioning", "allow_coordinates_below_depth", 1)
    if max_depth is not None and depth > max_depth:
        for coord in ("X", "Y"):
            if coord in pk:
                warn(f"{loc}({name}).Properties.{coord}",
                     f"{coord} below depth {max_depth}. House style positions with AutoLayout; "
                     f"coordinates mixed into an AutoLayout tree fight their siblings. Use "
                     f"Padding*, LayoutGap, or {sect('positioning','inset_idiom')}",
                     "positioning")

    # -- HOUSE: required property sets --
    for m in sorted(set(sect("required_properties", ctrl, [])) - pk):
        warn(f"{loc}({name}).Properties", f"{base} missing {m}", "required_properties")

    # -- HOUSE: containment --
    if ctrl == "GroupContainer@1.5.0":
        for m in sect("containment", "container_requires", []):
            if m not in pk:
                warn(f"{loc}({name}).Properties",
                     f"container missing {m} — without both, a row can collapse to zero height",
                     "containment")
    if ctrl == "Gallery@2.15.0":
        for m in sect("containment", "gallery_requires", []):
            if m not in pk:
                warn(f"{loc}({name}).Properties", f"Gallery missing {m}", "containment")

    if isinstance(fields.get("Children"), yaml.SequenceNode):
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
        if "\t" in line[: len(line) - len(line.lstrip())]:
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
        err(path.name, "no top-level 'Screens:' key — Studio needs the full source schema, "
                       "not a bare control list")
        return
    scroll_want = sect("containment", "scroll_containers_per_screen")
    for sname, screen in items(top["Screens"]):
        loc = f"{path.name}[{sname}]"
        sf = dict(items(screen))
        if isinstance(sf.get("Properties"), yaml.MappingNode):
            check_properties(loc, None, sf["Properties"], is_screen=True)
        else:
            err(loc, "screen has no Properties block")
        if isinstance(sf.get("Children"), yaml.SequenceNode):
            walk_children(loc, sf["Children"], 1)
        else:
            err(loc, "screen has no Children block")
        if scroll_want:
            n = raw.count("LayoutOverflowY")
            if n != scroll_want:
                warn(loc, f"{n} LayoutOverflowY container(s); house style uses {scroll_want} "
                          f"per screen (content region plus the card inside it)", "containment")


def load_style(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as e:
        print(f"WARN   could not read house style {path}: {e}. "
              f"PLATFORM rules still apply.", file=sys.stderr)
        return {}


def main():
    global STYLE, PLATFORM_ONLY
    args = sys.argv[1:]
    style_path = DEFAULT_STYLE
    files = []
    i = 0
    while i < len(args):
        if args[i] == "--style":
            i += 1
            style_path = pathlib.Path(args[i])
        elif args[i] == "--platform-only":
            PLATFORM_ONLY = True
        else:
            files.append(pathlib.Path(args[i]))
        i += 1
    if not files:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    STYLE = {} if PLATFORM_ONLY else load_style(style_path)
    if STYLE.get("meta", {}).get("style_id"):
        print(f"house style: {STYLE['meta']['style_id']}\n")
    for p in files:
        if not p.is_file():
            print(f"No such file: {p}", file=sys.stderr)
            return 2
        validate(p)
    for line in errors + warns:
        print(line)
    print(f"\n{len(errors)} error(s) [PLATFORM], {len(warns)} warning(s) [HOUSE].")
    if errors:
        print("Do not paste this into Studio. Every ERROR is a platform rule — fix and re-run.")
        return 1
    if warns:
        print("No platform errors. Review the HOUSE warnings: fix them, or if this project has "
              "different conventions, change assets/house-style.yaml rather than ignoring them.")
    else:
        print("Clean. Safe to paste into Power Apps Studio.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
