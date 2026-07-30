#!/usr/bin/env python3
"""Validate a solution-spec.yaml against the contract in solution-spec.schema.yaml.

Checks structure and referential integrity: every cross-reference between sections
must resolve, nothing may be orphaned, and enum-valued fields must use a known value.

Exit codes:  0 = clean (warnings allowed)   1 = at least one ERROR   2 = usage/parse failure

Every message names the offending key path, e.g.
    ERROR  bindings[3].field: 'CustomerNam' not a field of list 'New_Request'

Usage:  python3 spec/validate_spec.py path/to/solution-spec.yaml
"""
import sys
import pathlib

import yaml

FIELD_TYPES = {"text", "choice", "bool", "person", "datetime",
               "multiline", "currency", "number", "file"}
POPULATED_BY = {"user", "automation"}
LIST_KINDS = {"list", "library"}
VAR_KINDS = {"global", "collection", "context"}
DIRECTIONS = {"input", "display", "ui"}
RELATION_KINDS = {"text_key", "person", "none"}
TRIGGER_KINDS = {"powerapps", "sharepoint_item", "recurrence", "child"}
FLOW_TYPES = {"request_response", "automated", "child"}
STATUSES = {"draft", "final"}
LANG_ORDERS = {"th_first", "en_first"}
REQUIRED_TOP = ["meta", "process", "roles", "glossary", "lists",
                "relations", "screens", "variables", "flows", "bindings"]
VAR_PREFIX = {"global": "gbl", "collection": "col", "context": "var"}

errors, warnings = [], []


def err(path, msg):
    errors.append(f"ERROR  {path}: {msg}")


def warn(path, msg):
    warnings.append(f"WARN   {path}: {msg}")


def enum(path, value, allowed, label):
    if value is not None and value not in allowed:
        err(path, f"{value!r} is not a valid {label} ({', '.join(sorted(allowed))})")


def validate(spec):
    if not isinstance(spec, dict):
        err("<root>", "top level must be a mapping")
        return

    for key in REQUIRED_TOP:
        if key not in spec:
            err(key, "required top-level key is missing")
    if errors:
        return

    # ---- meta -------------------------------------------------------------
    meta = spec["meta"] or {}
    for k in ("id", "name", "version", "status"):
        if not meta.get(k):
            err(f"meta.{k}", "required and must be non-empty")
    enum("meta.status", meta.get("status"), STATUSES, "status")
    enum("meta.heading_language_order", meta.get("heading_language_order"),
         LANG_ORDERS, "heading language order")
    if meta.get("id") and meta["id"] != meta["id"].lower().replace(" ", "_"):
        warn("meta.id", f"{meta['id']!r} should be lower_snake_case")

    # ---- collect ids ------------------------------------------------------
    role_ids = set()
    for i, r in enumerate(spec["roles"] or []):
        rid = (r or {}).get("id")
        if not rid:
            err(f"roles[{i}].id", "required")
            continue
        if rid in role_ids:
            err(f"roles[{i}].id", f"duplicate role id {rid!r}")
        role_ids.add(rid)
        if not r.get("label"):
            err(f"roles[{i}].label", "required")

    stage_ids = set()
    for i, p in enumerate(spec["process"] or []):
        sid = (p or {}).get("id")
        if not sid:
            err(f"process[{i}].id", "required")
            continue
        if sid in stage_ids:
            err(f"process[{i}].id", f"duplicate stage id {sid!r}")
        stage_ids.add(sid)
        owner = p.get("owner_role")
        if owner and owner not in role_ids:
            err(f"process[{i}].owner_role", f"{owner!r} is not a role id")

    # ---- lists ------------------------------------------------------------
    list_fields = {}
    for i, lst in enumerate(spec["lists"] or []):
        lst = lst or {}
        name = lst.get("name")
        if not name:
            err(f"lists[{i}].name", "required")
            continue
        if name in list_fields:
            err(f"lists[{i}].name", f"duplicate list name {name!r}")
        enum(f"lists[{i}].kind", lst.get("kind"), LIST_KINDS, "list kind")

        seen, fields = set(), {}
        for j, f in enumerate(lst.get("fields") or []):
            f = f or {}
            fp = f"lists[{i}]({name}).fields[{j}]"
            fname = f.get("name")
            if not fname:
                err(f"{fp}.name", "required")
                continue
            if fname in seen:
                err(f"{fp}.name", f"duplicate field name {fname!r} in list {name!r}")
            seen.add(fname)
            fields[fname] = f
            enum(f"{fp}.type", f.get("type"), FIELD_TYPES, "field type")
            enum(f"{fp}.populated_by", f.get("populated_by"), POPULATED_BY, "populated_by")
            if not f.get("populated_by"):
                err(f"{fp}.populated_by", "required -- the SharePoint builder and the "
                                          "manual both need the user/automation split")
            if f.get("type") == "choice" and not f.get("choices"):
                warn(f"{fp}.choices", f"choice field {fname!r} declares no choices")
            other = f.get("other_field")
            if other and other not in (x.get("name") for x in (lst.get("fields") or [])):
                err(f"{fp}.other_field", f"{other!r} is not a field of list {name!r}")
        list_fields[name] = fields

        if lst.get("kind") == "library":
            first = next(iter(fields.values()), {})
            if first.get("type") != "file":
                warn(f"lists[{i}]({name})", "kind is 'library' but its first field is not "
                                            "type 'file'")
        title = lst.get("title_holds")
        if title and "Title" not in fields:
            warn(f"lists[{i}]({name}).title_holds",
                 f"declares Title holds {title!r} but no Title field is defined")

    # ---- relations --------------------------------------------------------
    for i, rel in enumerate(spec["relations"] or []):
        rel = rel or {}
        rp = f"relations[{i}]"
        src = rel.get("from")
        if src not in list_fields:
            err(f"{rp}.from", f"{src!r} is not a declared list")
        elif rel.get("from_field") and rel["from_field"] not in list_fields[src]:
            err(f"{rp}.from_field", f"{rel['from_field']!r} not a field of list {src!r}")
        dst = rel.get("to")
        if dst is not None:
            if dst not in list_fields:
                err(f"{rp}.to", f"{dst!r} is not a declared list")
            elif rel.get("to_field") and rel["to_field"] not in list_fields[dst]:
                err(f"{rp}.to_field", f"{rel['to_field']!r} not a field of list {dst!r}")
        enum(f"{rp}.kind", rel.get("kind"), RELATION_KINDS, "relation kind")
        if rel.get("kind") == "lookup":
            err(f"{rp}.kind", "'lookup' is not permitted -- Lookup columns are not "
                              "delegable. Use kind 'text_key'.")
        if not rel.get("reason"):
            err(f"{rp}.reason", "required -- a relation without a stated reason gets "
                                "'improved' by the next builder")

    # ---- screens ----------------------------------------------------------
    screen_ids = set()
    for i, s in enumerate(spec["screens"] or []):
        s = s or {}
        sid = s.get("id")
        sp = f"screens[{i}]"
        if not sid:
            err(f"{sp}.id", "required")
            continue
        if sid in screen_ids:
            err(f"{sp}.id", f"duplicate screen id {sid!r}")
        screen_ids.add(sid)
        if not s.get("name"):
            err(f"{sp}.name", "required")
        for r in s.get("roles") or []:
            if r not in role_ids:
                err(f"{sp}({sid}).roles", f"{r!r} is not a role id")
        if not (s.get("roles") or []):
            warn(f"{sp}({sid}).roles", "no roles -- the manual cannot place this screen "
                                       "in a user or admin section")
        stage = s.get("process_stage")
        if stage and stage not in stage_ids:
            err(f"{sp}({sid}).process_stage", f"{stage!r} is not a process id")
        for key in ("reads", "writes"):
            for ln in s.get(key) or []:
                if ln not in list_fields:
                    err(f"{sp}({sid}).{key}", f"{ln!r} is not a declared list")

    # ---- variables --------------------------------------------------------
    var_names = set()
    for i, v in enumerate(spec["variables"] or []):
        v = v or {}
        vp = f"variables[{i}]"
        name = v.get("name")
        if not name:
            err(f"{vp}.name", "required")
            continue
        if name in var_names:
            err(f"{vp}.name", f"duplicate variable name {name!r}")
        var_names.add(name)
        kind = v.get("kind")
        enum(f"{vp}.kind", kind, VAR_KINDS, "variable kind")
        prefix = VAR_PREFIX.get(kind)
        if prefix and not name.startswith(prefix):
            warn(f"{vp}.name", f"{name!r} is kind {kind!r} so it should start with "
                               f"{prefix!r} (gbl/col/var convention)")
        if not v.get("set_by"):
            err(f"{vp}.set_by", "required")
        bl = v.get("backing_list")
        if bl and bl not in list_fields:
            err(f"{vp}.backing_list", f"{bl!r} is not a declared list")
        for sc in v.get("used_on") or []:
            if sc not in screen_ids:
                err(f"{vp}.used_on", f"{sc!r} is not a screen id")

    # ---- flows ------------------------------------------------------------
    flow_ids = set()
    for i, f in enumerate(spec["flows"] or []):
        f = f or {}
        fp = f"flows[{i}]"
        fid = f.get("id")
        if not fid:
            err(f"{fp}.id", "required")
            continue
        if fid in flow_ids:
            err(f"{fp}.id", f"duplicate flow id {fid!r}")
        flow_ids.add(fid)
        enum(f"{fp}.type", f.get("type"), FLOW_TYPES, "flow type")
        trig = f.get("trigger") or {}
        kind = trig.get("kind")
        enum(f"{fp}({fid}).trigger.kind", kind, TRIGGER_KINDS, "trigger kind")
        if kind == "sharepoint_item":
            if not trig.get("splits_on"):
                err(f"{fp}({fid}).trigger.splits_on",
                    "required for a sharepoint_item trigger -- without splitOn the flow "
                    "fires once per batch instead of once per item")
            if not trig.get("list"):
                err(f"{fp}({fid}).trigger.list", "required for a sharepoint_item trigger")
        elif trig.get("splits_on"):
            warn(f"{fp}({fid}).trigger.splits_on",
                 f"set on a {kind!r} trigger, which does not return an array")
        for ln in f.get("lists") or []:
            if ln not in list_fields:
                err(f"{fp}({fid}).lists", f"{ln!r} is not a declared list")

    for i, f in enumerate(spec["flows"] or []):
        for callee in (f or {}).get("calls") or []:
            if callee not in flow_ids:
                err(f"flows[{i}].calls", f"{callee!r} is not a flow id")
    for i, s in enumerate(spec["screens"] or []):
        for fl in (s or {}).get("fires_flows") or []:
            if fl not in flow_ids:
                err(f"screens[{i}].fires_flows", f"{fl!r} is not a flow id")

    # ---- bindings ---------------------------------------------------------
    bound_vars, bound_screens = set(), set()
    for i, b in enumerate(spec["bindings"] or []):
        b = b or {}
        bp = f"bindings[{i}]"
        sc = b.get("screen")
        if sc not in screen_ids:
            err(f"{bp}.screen", f"{sc!r} is not a screen id")
        else:
            bound_screens.add(sc)
        if not b.get("control"):
            err(f"{bp}.control", "required")
        direction = b.get("direction")
        enum(f"{bp}.direction", direction, DIRECTIONS, "direction")

        ln, fn = b.get("list"), b.get("field")
        if direction == "ui":
            if ln or fn:
                warn(f"{bp}", "direction is 'ui' but a list/field is named")
        else:
            if not ln:
                err(f"{bp}.list", f"required when direction is {direction!r}")
            elif ln not in list_fields:
                err(f"{bp}.list", f"{ln!r} is not a declared list")
            elif not fn:
                err(f"{bp}.field", f"required when direction is {direction!r}")
            elif fn not in list_fields[ln]:
                err(f"{bp}.field", f"{fn!r} is not a field of list {ln!r}")
        var = b.get("variable")
        if var:
            if var not in var_names:
                err(f"{bp}.variable", f"{var!r} is not a declared variable")
            else:
                bound_vars.add(var)

    # ---- orphans ----------------------------------------------------------
    for v in spec["variables"] or []:
        name = (v or {}).get("name")
        if name and name not in bound_vars and not (v or {}).get("used_on"):
            warn(f"variables({name})", "orphan -- referenced by no binding and no "
                                       "used_on screen")
    for sid in screen_ids - bound_screens:
        warn(f"screens({sid})", "no bindings reference this screen")
    used_lists = set()
    for s in spec["screens"] or []:
        used_lists |= set((s or {}).get("reads") or []) | set((s or {}).get("writes") or [])
    for f in spec["flows"] or []:
        used_lists |= set((f or {}).get("lists") or [])
    for ln in set(list_fields) - used_lists:
        warn(f"lists({ln})", "no screen or flow reads or writes this list")


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.is_file():
        print(f"No such file: {path}", file=sys.stderr)
        return 2
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR  <parse>: {e}", file=sys.stderr)
        return 2

    validate(spec)
    for line in errors + warnings:
        print(line)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
    if errors:
        print("Spec is not valid. Fix every ERROR before any skill reads it.")
        return 1
    print("Spec is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
