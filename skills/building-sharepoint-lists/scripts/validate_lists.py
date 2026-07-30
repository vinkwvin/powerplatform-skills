#!/usr/bin/env python3
"""Validate the lists[] and relations[] sections of a solution-spec.yaml before provisioning.

PLATFORM errors are SharePoint or Power Apps facts and are not overridable.
HOUSE warnings are this organisation's conventions, held in assets/house-style.yaml.
See docs/EVIDENCE-TIERS.md.

Exit codes:  0 = no PLATFORM errors   1 = at least one ERROR   2 = usage or parse failure

Usage:
    python3 scripts/validate_lists.py spec.yaml
    python3 scripts/validate_lists.py --platform-only spec.yaml
    python3 scripts/validate_lists.py --style path/to/house-style.yaml spec.yaml
"""
import re
import sys
import pathlib

import yaml

VALID_TYPES = {"text", "multiline", "choice", "bool", "number",
               "currency", "datetime", "person", "file"}
POPULATED = {"user", "automation"}
VALID_REL_KINDS = {"text_key", "person", "none"}
DEFAULT_STYLE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "house-style.yaml"

errors, warns = [], []
STYLE, PLATFORM_ONLY = {}, False


def err(loc, msg):
    errors.append(f"ERROR  [PLATFORM] {loc}: {msg}")


def warn(loc, msg, section=None):
    if PLATFORM_ONLY:
        return
    if section and not STYLE.get(section, {}).get("enforce", True):
        return
    warns.append(f"WARN   [HOUSE]    {loc}: {msg}")


def sect(name, key, default=None):
    return STYLE.get(name, {}).get(key, default)


def validate(spec):
    lists = spec.get("lists")
    if not lists:
        err("lists", "spec has no lists[] section")
        return

    by_name = {}
    for i, lst in enumerate(lists):
        lst = lst or {}
        lp = f"lists[{i}]"
        name = lst.get("name")
        if not name:
            err(f"{lp}.name", "required")
            continue
        if name in by_name:
            err(f"{lp}.name", f"duplicate list name {name!r}")
        fields = lst.get("fields") or []
        by_name[name] = {(f or {}).get("name") for f in fields}
        lp = f"lists[{i}]({name})"

        kind = lst.get("kind", "list")
        if kind not in {"list", "library"}:
            err(f"{lp}.kind", f"{kind!r} must be 'list' or 'library'")

        # -- PLATFORM: library detection --
        first_type = (fields[0] or {}).get("type") if fields else None
        has_file = any((f or {}).get("type") == "file" for f in fields)
        if kind == "library" and first_type != "file":
            err(f"{lp}", "kind is 'library' but its first field is not type 'file'. A library's "
                         "first column is the file itself")
        if kind == "list" and has_file:
            err(f"{lp}", "a field of type 'file' appears in a list. A plain list cannot hold "
                         "file uploads — set kind: library")

        seen = set()
        for j, f in enumerate(fields):
            f = f or {}
            fname = f.get("name")
            fp = f"{lp}.fields[{j}]"
            if not fname:
                err(f"{fp}.name", "required")
                continue
            if fname in seen:
                err(f"{fp}.name", f"duplicate field name {fname!r} in list {name!r}")
            seen.add(fname)
            fp = f"{lp}.{fname}"

            # -- PLATFORM: types --
            ftype = f.get("type")
            if ftype not in VALID_TYPES:
                if ftype == "lookup":
                    err(f"{fp}.type",
                        "'lookup' is not permitted. A Lookup column cannot be filtered on the "
                        "server, so a gallery filtered on it truncates silently at the "
                        "delegation limit with no error. Use type 'text' for the key")
                else:
                    err(f"{fp}.type", f"{ftype!r} is not a valid type ({sorted(VALID_TYPES)})")
            pop = f.get("populated_by")
            if pop is None:
                err(f"{fp}.populated_by",
                    "required. It decides whether the column appears on a user form, and the "
                    "manual renders the same split")
            elif pop not in POPULATED:
                err(f"{fp}.populated_by", f"{pop!r} must be 'user' or 'automation'")

            # -- PLATFORM: choices --
            if ftype == "choice" and not f.get("choices"):
                err(f"{fp}.choices",
                    "a Choice column rejects any value not in its list, so the choices must be "
                    "enumerated before provisioning")
            other = f.get("other_field")
            if other and other not in seen | {(x or {}).get("name") for x in fields}:
                err(f"{fp}.other_field", f"{other!r} is not a field of list {name!r}")

            # -- PLATFORM: column naming --
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", fname):
                err(f"{fp}.name",
                    f"{fname!r} is not a safe SharePoint column name. Non-ASCII or punctuated "
                    f"names survive creation and then break formulas, URLs and exports. Keep "
                    f"the name ASCII and put the localised text in label_th")

            # -- HOUSE --
            if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", fname):
                warn(f"{fp}.name", f"{fname!r} is not PascalCase", "naming")
            if ftype == "bool":
                prefixes = sect("naming", "boolean_prefixes", [])
                # A past participle ("Checked", "Approved") reads as a statement just as well
                # as a prefix does, so accept either shape.
                participle = bool(re.search(r"(ed|able|ible)$", fname))
                if prefixes and not participle and \
                        not any(fname.startswith(p) for p in prefixes):
                    warn(f"{fp}.name",
                         f"boolean {fname!r} does not read as a statement or action. Use a "
                         f"house prefix {prefixes} or a past participle (Checked, Approved)",
                         "naming")
            if not f.get("label_th") and not f.get("label"):
                warn(f"{fp}", "no localised label — the manual and the provisioning workbook "
                              "both render one", "naming")

        # -- HOUSE: audit pair on child lists --
        if sect("audit_trail", "require_on_child_lists", False):
            # Only a text_key relation makes this a child list. A person relation
            # (e.g. an owner field) does not.
            joins = {rel.get("from_field") for rel in (spec.get("relations") or [])
                     if rel.get("from") == name and rel.get("kind") == "text_key"}
            if joins & seen:
                by, at = sect("audit_trail", "actor_suffix", "By"), \
                          sect("audit_trail", "time_suffix", "At")
                pairs = {n[:-len(by)] for n in seen if n.endswith(by)} & \
                        {n[:-len(at)] for n in seen if n.endswith(at)}
                if not pairs:
                    warn(f"{lp}", f"child list has no <Verb>{by}/<Verb>{at} audit pair. Cheap "
                                  f"now, painful to retrofit", "audit_trail")

    # -- relations --
    for i, rel in enumerate(spec.get("relations") or []):
        rel = rel or {}
        rp = f"relations[{i}]"
        kind = rel.get("kind")
        if kind == "lookup":
            err(f"{rp}.kind", "'lookup' is not permitted — see the delegation note in "
                              "references/delegation.md. Use 'text_key'")
        elif kind not in VALID_REL_KINDS:
            err(f"{rp}.kind", f"{kind!r} must be one of {sorted(VALID_REL_KINDS)}")
        src = rel.get("from")
        if src not in by_name:
            err(f"{rp}.from", f"{src!r} is not a declared list")
        elif rel.get("from_field") and rel["from_field"] not in by_name[src]:
            err(f"{rp}.from_field", f"{rel['from_field']!r} is not a field of {src!r}")
        dst = rel.get("to")
        if dst is not None:
            if dst not in by_name:
                err(f"{rp}.to", f"{dst!r} is not a declared list")
            elif rel.get("to_field") and rel["to_field"] not in by_name[dst]:
                err(f"{rp}.to_field", f"{rel['to_field']!r} is not a field of {dst!r}")
        if kind == "text_key" and rel.get("from_field"):
            for lst in spec["lists"]:
                if (lst or {}).get("name") != src:
                    continue
                for f in lst.get("fields") or []:
                    if (f or {}).get("name") == rel["from_field"] and f.get("type") != "text":
                        err(f"{rp}.from_field",
                            f"{rel['from_field']!r} is kind 'text_key' but its type is "
                            f"{f.get('type')!r}. A join key must be text to stay delegable")
        if not rel.get("reason"):
            warn(f"{rp}.reason", "no reason stated — an unexplained relation gets 'improved' by "
                                 "the next builder")


def main():
    global STYLE, PLATFORM_ONLY
    args, style_path, files = sys.argv[1:], DEFAULT_STYLE, []
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
    if len(files) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if not files[0].is_file():
        print(f"No such file: {files[0]}", file=sys.stderr)
        return 2
    if not PLATFORM_ONLY:
        try:
            STYLE = yaml.safe_load(style_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as e:
            print(f"WARN   could not read house style {style_path}: {e}", file=sys.stderr)
    try:
        spec = yaml.safe_load(files[0].read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR  <parse>: {e}", file=sys.stderr)
        return 2

    validate(spec)
    for line in errors + warns:
        print(line)
    print(f"\n{len(errors)} error(s) [PLATFORM], {len(warns)} warning(s) [HOUSE].")
    if errors:
        print("Do not provision from this spec. Fix every ERROR and re-run.")
        return 1
    if warns:
        print("No platform errors. Review the HOUSE warnings, or change "
              "assets/house-style.yaml if this project's conventions differ.")
    else:
        print("Clean. Safe to generate the provisioning workbook.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
