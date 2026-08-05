#!/usr/bin/env python3
"""Build an importable Power Automate legacy package (.zip) from a spec flow, anchored to a
real export from the target tenant.

TEMPLATE ANCHORING — the central idea. A package carries values that cannot be derived:
per-connection identifiers, resource GUIDs, tenant identifiers. They are opaque strings owned
by one tenant. So this script regenerates ONLY definition.json's triggers and actions, and
carries everything else from the template byte for byte:

    manifest.json                                 carried (displayName updated)
    Microsoft.Flow/flows/manifest.json            carried
    .../<asset>/apisMap.json                      carried
    .../<asset>/connectionsMap.json               carried
    .../<asset>/definition.json
        properties.connectionReferences           carried
        properties.definition.metadata            carried
        properties.definition.triggers            REGENERATED
        properties.definition.actions             REGENERATED

Usage:
    python3 build_package.py spec.yaml flow_1_submit --template export.zip -o out.zip
    python3 build_package.py spec.yaml flow_1_submit --template export.zip --dir out/
"""
import argparse
import copy
import json
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile

import yaml

SPLIT_ON = "@triggerOutputs()?['body/value']"
WDL_SCHEMA = ("https://schema.management.azure.com/providers/Microsoft.Logic/schemas/"
              "2016-06-01/workflowdefinition.json#")


def die(msg):
    print(f"ERROR  {msg}", file=sys.stderr)
    sys.exit(1)


def load_template(path):
    """Unpack a real export and return (tempdir, asset_guid, files)."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="paflow-"))
    if path.is_dir():
        shutil.copytree(path, tmp / "pkg")
        root = tmp / "pkg"
    else:
        root = tmp / "pkg"
        with zipfile.ZipFile(path) as z:
            z.extractall(root)

    flows_dir = root / "Microsoft.Flow" / "flows"
    if not flows_dir.is_dir():
        die(f"{path} has no Microsoft.Flow/flows — is this a legacy package export?")
    assets = [d for d in flows_dir.iterdir() if d.is_dir()]
    if len(assets) != 1:
        die(f"expected exactly one flow asset folder, found {len(assets)}. A legacy package "
            f"holds one flow")
    return root, assets[0]


def connector_of(step):
    """Map a spec step's connector string to a connector API name, if it names one."""
    c = (step.get("connector") or "").lower()
    if "sharepoint" in c:
        return "shared_sharepointonline"
    if "outlook" in c or "office 365" in c or "send an email" in c:
        return "shared_office365"
    if "approval" in c:
        return "shared_approvals"
    if "teams" in c:
        return "shared_teams"
    return None


def action_name(step, i):
    base = re.sub(r"[^A-Za-z0-9]+", "_", str(step.get("action") or f"Step_{i}")).strip("_")
    return base or f"Step_{i}"


def build_trigger(flow, conn_refs):
    trig = flow.get("trigger") or {}
    kind = trig.get("kind")

    if kind == "powerapps":
        return {"manual": {"type": "Request", "kind": "PowerApp",
                           "inputs": {"schema": {"type": "object", "properties": {}}}}}
    if kind == "child":
        return {"manual": {"type": "Request", "kind": "Button",
                           "inputs": {"schema": {"type": "object", "properties": {}}}}}
    if kind == "recurrence":
        return {"Recurrence": {"type": "Recurrence",
                               "recurrence": {"frequency": trig.get("frequency", "Day"),
                                              "interval": trig.get("interval", 1)}}}
    if kind == "sharepoint_item":
        api = "shared_sharepointonline"
        if api not in conn_refs:
            die(f"the template has no {api} connection, but this flow needs a SharePoint "
                f"trigger. Ask for an export from a flow that uses SharePoint")
        t = {
            "recurrence": {"frequency": "Minute", "interval": 1},
            # PLATFORM: an item trigger returns an array. Without splitOn the flow fires once
            # per batch instead of once per item.
            "splitOn": SPLIT_ON,
            "type": "OpenApiConnection",
            "inputs": {
                "host": {"apiId": f"/providers/Microsoft.PowerApps/apis/{api}",
                         "connectionName": api,
                         "operationId": "GetOnUpdatedItems"},
                "parameters": {"dataset": "REPLACE-SITE-URL",
                               "table": f"REPLACE-LIST-GUID ({trig.get('list','')})"},
                "authentication": "@parameters('$authentication')",
            },
        }
        return {"When_an_item_is_created_or_modified": t}
    die(f"unknown trigger kind {kind!r}. Expected one of: powerapps, sharepoint_item, "
        f"recurrence, child")


def build_actions(flow, conn_refs, warnings):
    actions, prev = {}, None
    for i, step in enumerate(flow.get("steps") or [], 1):
        name = action_name(step, i)
        while name in actions:
            name += "_2"
        api = connector_of(step)
        if api and api not in conn_refs:
            warnings.append(
                f"step {i} ({step.get('action')}) wants {api}, which the template does not "
                f"have. Its connection identifiers cannot be invented — get an export from a "
                f"flow that uses it, or the import will fail on this connector")
        if api:
            act = {
                "type": "OpenApiConnection",
                "inputs": {
                    "host": {"apiId": f"/providers/Microsoft.PowerApps/apis/{api}",
                             "connectionName": api,
                             "operationId": "REPLACE-OPERATION-ID"},
                    "parameters": {},
                    "authentication": "@parameters('$authentication')",
                },
            }
        else:
            act = {"type": "Compose", "inputs": f"REPLACE — {step.get('action','')}"}
        # PLATFORM: order comes from runAfter, not key order.
        act["runAfter"] = {} if prev is None else {prev: ["Succeeded"]}
        if step.get("notes"):
            act["description"] = str(step["notes"])
        actions[name] = act
        prev = name

    if flow.get("responds_to_app"):
        actions["Respond_to_a_Power_App_or_flow"] = {
            "type": "Response",
            "kind": "PowerApp",
            "inputs": {"statusCode": 200, "body": {}},
            "runAfter": {} if prev is None else {prev: ["Succeeded"]},
        }
    return actions


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("flow_id")
    ap.add_argument("--template", required=True,
                    help="a REAL .zip (or unpacked dir) exported from the target tenant")
    ap.add_argument("-o", "--out")
    ap.add_argument("--dir", help="write the unpacked package here instead of a zip")
    args = ap.parse_args()

    spec = yaml.safe_load(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    flows = {f.get("id"): f for f in (spec.get("flows") or [])}
    if args.flow_id not in flows:
        die(f"no flow {args.flow_id!r} in the spec. Available: {', '.join(flows) or '(none)'}")
    flow = flows[args.flow_id]

    tpl = pathlib.Path(args.template)
    if not tpl.exists():
        die(f"template not found: {tpl}")
    root, asset = load_template(tpl)

    defn_path = asset / "definition.json"
    if not defn_path.is_file():
        die("template asset folder has no definition.json")
    defn = json.loads(defn_path.read_text(encoding="utf-8"))
    props = defn.setdefault("properties", {})
    conn_refs = props.get("connectionReferences") or {}
    if not conn_refs:
        die("the template has no connectionReferences. It cannot anchor a package — export a "
            "flow that actually uses a connector")

    warnings = []
    inner = props.setdefault("definition", {})
    inner["$schema"] = inner.get("$schema", WDL_SCHEMA)
    inner.setdefault("contentVersion", "1.0.0.0")
    inner.setdefault("parameters", {"$authentication": {"defaultValue": {},
                                                        "type": "SecureObject"},
                                    "$connections": {"defaultValue": {}, "type": "Object"}})
    # REGENERATED
    inner["triggers"] = build_trigger(flow, conn_refs)
    inner["actions"] = build_actions(flow, conn_refs, warnings)
    inner.setdefault("outputs", {})
    # `metadata` is carried from the template untouched — it holds tenant GUIDs.

    display = flow.get("name") or args.flow_id
    props["displayName"] = display
    defn_path.write_text(json.dumps(defn, indent=2, ensure_ascii=False), encoding="utf-8")

    man_path = root / "manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    man.setdefault("details", {})["displayName"] = display
    for res in (man.get("resources") or {}).values():
        if res.get("type") == "Microsoft.Flow/flows":
            res.setdefault("details", {})["displayName"] = display
    man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.dir:
        out = pathlib.Path(args.dir)
        if out.exists():
            shutil.rmtree(out)
        shutil.copytree(root, out)
        print(f"wrote {out}/")
    else:
        out = pathlib.Path(args.out or f"{args.flow_id}.zip")
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(root).as_posix())
        print(f"wrote {out}")

    print(f"  flow: {display}   trigger: {(flow.get('trigger') or {}).get('kind')}")
    print(f"  carried verbatim: connectionReferences ({', '.join(conn_refs)}), "
          f"definition.metadata, both manifests, apisMap, connectionsMap")
    print(f"  regenerated: triggers, actions ({len(inner['actions'])})")
    for w in warnings:
        print(f"  WARNING: {w}")
    print("  Placeholders marked REPLACE- must be filled before import.")
    print("  At import you WILL be asked to pick connections. That is normal for a legacy "
          "package, not a failure.")
    shutil.rmtree(root.parent, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
