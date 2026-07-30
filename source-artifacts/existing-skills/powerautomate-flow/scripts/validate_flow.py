#!/usr/bin/env python3
"""
validate_flow.py — dependency-free checker + zip builder for Power Automate
legacy import packages.

Usage:
    python3 validate_flow.py <package-folder>              # validate
    python3 validate_flow.py <package-folder> --zip out.zip  # validate, then build zip

A <package-folder> looks like:
    <FlowName>_YYYYMMDD/
    ├── manifest.json
    └── Microsoft.Flow/flows/<GUID>/definition.json

Exit code is non-zero if any ERROR is found, so it can gate delivery.
Checks the failure modes that make imports fail silently:
  - invalid JSON
  - folder/GUID structure wrong
  - runAfter targets a non-existent action (at the same nesting level)
  - expression references (outputs/body/actions/items) to a non-existent action
  - connector action missing authentication
  - connectionName not declared in connectionReferences
  - connectionReferences entry not backed by a manifest resource + dependsOn (WARN)
  - action name contains spaces (WARN)
Stdlib only (json, os, re, sys, zipfile, argparse). No install.
"""
import argparse
import json
import os
import re
import sys
import zipfile

ERRORS = []
WARNS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNS.append(msg)


# ---------- locate files ----------

def find_package(folder):
    manifest_path = os.path.join(folder, "manifest.json")
    if not os.path.isfile(manifest_path):
        err(f"manifest.json not found at package root ({manifest_path}). "
            f"Zip contents must have manifest.json at the top level.")
        return None, None, None
    flows_dir = os.path.join(folder, "Microsoft.Flow", "flows")
    if not os.path.isdir(flows_dir):
        err("Missing 'Microsoft.Flow/flows/' folder — do not rename or re-nest the structure.")
        return manifest_path, None, None
    guids = [d for d in os.listdir(flows_dir) if os.path.isdir(os.path.join(flows_dir, d))]
    if len(guids) != 1:
        err(f"Expected exactly one <GUID> folder under Microsoft.Flow/flows/, found {len(guids)}: {guids}")
        return manifest_path, None, None
    guid = guids[0]
    def_path = os.path.join(flows_dir, guid, "definition.json")
    if not os.path.isfile(def_path):
        err(f"definition.json not found in Microsoft.Flow/flows/{guid}/")
        return manifest_path, None, guid
    return manifest_path, def_path, guid


def load_json(path, label):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        err(f"{label} is not valid JSON: line {e.lineno} col {e.colno}: {e.msg}")
    except Exception as e:
        err(f"{label} could not be read: {e}")
    return None


# ---------- traversal ----------

def walk_operations(container, level_name, all_names, level_map):
    """Collect action names per nesting level and record runAfter targets.
    container: an 'actions' (or trigger) dict at one level.
    Recurses into If (actions/else), Foreach/Scope/Until (actions), Switch (cases/default)."""
    names_here = list(container.keys())
    level_map.setdefault(level_name, set()).update(names_here)
    for name, body in container.items():
        all_names.add(name)
        if " " in name:
            warn(f"Action name '{name}' contains a space — keys should use underscores "
                 f"(references like outputs('{name.replace(' ', '_')}') must match the key).")
        if not isinstance(body, dict):
            continue
        # runAfter integrity at this level
        ra = body.get("runAfter", {})
        if isinstance(ra, dict):
            for target in ra.keys():
                if target not in names_here:
                    err(f"'{name}'.runAfter points to '{target}', which is not an action "
                        f"at the same level ({level_name}). Valid siblings: {sorted(names_here)}")
        # recurse into nested actions
        for key in ("actions",):
            if isinstance(body.get(key), dict):
                walk_operations(body[key], f"{name}/{key}", all_names, level_map)
        if isinstance(body.get("else"), dict) and isinstance(body["else"].get("actions"), dict):
            walk_operations(body["else"]["actions"], f"{name}/else", all_names, level_map)
        if isinstance(body.get("cases"), dict):
            for cname, cbody in body["cases"].items():
                if isinstance(cbody, dict) and isinstance(cbody.get("actions"), dict):
                    walk_operations(cbody["actions"], f"{name}/case:{cname}", all_names, level_map)
        if isinstance(body.get("default"), dict) and isinstance(body["default"].get("actions"), dict):
            walk_operations(body["default"]["actions"], f"{name}/default", all_names, level_map)


REF_RE = re.compile(r"(?:outputs|body|actions|item)\(\s*'([^']+)'\s*\)")


def collect_refs_and_hosts(obj, all_names, conn_names_used, needs_auth):
    """Walk the whole definition dict; collect action references in expressions,
    connectionNames used in host blocks, and actions missing authentication."""
    if isinstance(obj, dict):
        # host block?
        host = obj.get("host") if isinstance(obj.get("host"), dict) else None
        if host and "connectionName" in host:
            conn_names_used.add(host["connectionName"])
            # this obj is an action 'inputs' with a host -> must have authentication
            if "authentication" not in obj:
                needs_auth.append(host.get("operationId", "?"))
        for v in obj.values():
            collect_refs_and_hosts(v, all_names, conn_names_used, needs_auth)
    elif isinstance(obj, list):
        for v in obj:
            collect_refs_and_hosts(v, all_names, conn_names_used, needs_auth)
    elif isinstance(obj, str):
        for m in REF_RE.finditer(obj):
            ref = m.group(1)
            # 'item' refers to a loop name; outputs/body/actions refer to action names
            if ref not in all_names:
                err(f"Expression references action '{ref}' which does not exist. "
                    f"Check the action key spelling/underscores.")


# ---------- main validation ----------

def validate(folder):
    manifest_path, def_path, guid = find_package(folder)
    if not def_path:
        return
    manifest = load_json(manifest_path, "manifest.json")
    definition_file = load_json(def_path, "definition.json")
    if definition_file is None:
        return

    props = definition_file.get("properties", {})
    definition = props.get("definition", {})
    if not definition:
        err("definition.json has no properties.definition block.")
        return

    # schema basics
    if "$schema" not in definition:
        warn("definition is missing $schema (Logic Apps workflowdefinition schema).")
    if definition.get("contentVersion") != "1.0.0.0":
        warn("definition.contentVersion should be '1.0.0.0'.")

    # GUID consistency
    name_field = definition_file.get("name")
    if name_field and guid and name_field != guid:
        err(f"GUID mismatch: folder is '{guid}' but definition.name is '{name_field}'. "
            f"They must be identical (also check the manifest resource key).")

    triggers = definition.get("triggers", {})
    actions = definition.get("actions", {})
    if not triggers:
        err("No triggers defined — a flow needs exactly one trigger.")
    if not actions:
        warn("No actions defined — the flow does nothing.")

    all_names = set()
    level_map = {}
    if isinstance(actions, dict):
        walk_operations(actions, "root", all_names, level_map)
    # triggers are also referenceable but not via outputs('name'); skip name collision checks

    conn_names_used = set()
    needs_auth = []
    collect_refs_and_hosts(definition, all_names, conn_names_used, needs_auth)

    for op in needs_auth:
        err(f"A connector action (operationId '{op}') has a host block but no "
            f"\"authentication\": \"@parameters('$authentication')\".")

    # connectionReferences cross-check (definition side)
    conn_refs = props.get("connectionReferences", {})
    declared = set(conn_refs.keys())
    for cn in conn_names_used:
        if cn not in declared:
            err(f"connectionName '{cn}' is used in an action but not declared in "
                f"properties.connectionReferences. Add it (key = connectionName).")

    # manifest cross-check
    if isinstance(manifest, dict):
        resources = manifest.get("resources", {})
        conn_resource_names = {
            r.get("name") for r in resources.values()
            if isinstance(r, dict) and r.get("type") == "Microsoft.PowerApps/apis"
        }
        flow_resources = [
            r for r in resources.values()
            if isinstance(r, dict) and r.get("type") == "Microsoft.Flow/flows"
        ]
        depends = set()
        for fr in flow_resources:
            depends.update(fr.get("dependsOn", []) or [])
        # every declared connection should be backed by a manifest resource
        for cn in declared:
            if cn not in conn_resource_names:
                warn(f"connectionReference '{cn}' has no matching Microsoft.PowerApps/apis "
                     f"resource in manifest.json — the connection may show a grey X on import.")
        # flow resource key should equal the guid
        if guid and guid not in resources:
            warn(f"manifest.json resources has no key equal to the flow GUID '{guid}'.")
        if not depends and conn_names_used:
            warn("The flow resource's dependsOn is empty but the flow uses connectors — "
                 "connections may not wire up on import.")


def build_zip(folder, out_zip):
    """Zip the *contents* of the package folder (manifest.json at zip root)."""
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(folder):
            for fn in files:
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, folder)  # relative to folder -> manifest at root
                zf.write(full, arc)
    print(f"Built {out_zip}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="package folder (contains manifest.json)")
    ap.add_argument("--zip", dest="zip_out", default=None, help="build a zip after validating")
    args = ap.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Not a folder: {args.folder}", file=sys.stderr)
        sys.exit(2)

    validate(args.folder)

    for w in WARNS:
        print(f"WARN  {w}")
    for e in ERRORS:
        print(f"ERROR {e}")
    print(f"\n{len(ERRORS)} error(s), {len(WARNS)} warning(s).")

    if ERRORS:
        print("Fix ERRORs before importing — the package will likely fail silently otherwise.")
        sys.exit(1)

    if args.zip_out:
        build_zip(args.folder, args.zip_out)
    else:
        print("OK. Build the zip with --zip <out.zip>, then import via "
              "My Flows → Import → Import Package (Legacy).")


if __name__ == "__main__":
    main()
