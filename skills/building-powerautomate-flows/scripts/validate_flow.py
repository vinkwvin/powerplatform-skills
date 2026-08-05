#!/usr/bin/env python3
"""Validate a Power Automate legacy package before import.

Every PLATFORM rule below was observed in a real export from a live tenant. Where the old
version of this validator checked a package's self-consistency with its own conventions — and
therefore always passed anything built from its own template — these check against what a real
export actually contains.

WHAT THIS CANNOT TELL YOU: whether the package imports into your tenant. That depends on
per-connection identifiers only that tenant holds. This validator is backed by one observed
export; the Power Apps validator in this suite is backed by seventeen compiling screens. Treat
the first import as a test.

Exit codes:  0 = no PLATFORM errors   1 = at least one ERROR   2 = usage failure

Usage:
    python3 validate_flow.py package.zip
    python3 validate_flow.py unpacked-dir/
"""
import json
import pathlib
import re
import sys
import tempfile
import zipfile

SPLIT_ON = "@triggerOutputs()?['body/value']"
SPLIT_ON_RE = re.compile(r"@\s*triggerOutputs\(\)\s*\?\s*\[\s*'body/value'\s*\]")
ARRAY_TRIGGER_TYPES = {"OpenApiConnection"}
ARRAY_OPERATION_HINT = re.compile(r"^(GetOnNewItems|GetOnUpdatedItems|OnNewItems|OnUpdatedItems"
                                  r"|GetOnNewFiles|OnNewFiles)$")

errors, warns = [], []


def err(loc, msg):
    errors.append(f"ERROR  [PLATFORM] {loc}: {msg}")


def warn(loc, msg):
    warns.append(f"WARN              {loc}: {msg}")


def walk_ops(container, path, out):
    """Yield (name, action, path) for every action at every nesting level."""
    for name, act in (container or {}).items():
        if not isinstance(act, dict):
            continue
        out.append((name, act, f"{path}.{name}"))
        for key in ("actions", "else"):
            sub = act.get(key)
            if isinstance(sub, dict):
                inner = sub.get("actions") if "actions" in sub else sub
                if isinstance(inner, dict):
                    walk_ops(inner, f"{path}.{name}.{key}", out)
        for case in (act.get("cases") or {}).values():
            if isinstance(case, dict):
                walk_ops(case.get("actions") or {}, f"{path}.{name}.cases", out)


def validate(root):
    # ---- 1. the five files ------------------------------------------------
    man = root / "manifest.json"
    flows_man = root / "Microsoft.Flow" / "flows" / "manifest.json"
    if not man.is_file():
        err("manifest.json", "missing at the package root")
    if not flows_man.is_file():
        err("Microsoft.Flow/flows/manifest.json", "missing — a real export has a SECOND manifest "
                                                  "listing the asset folders")
    flows_dir = root / "Microsoft.Flow" / "flows"
    if not flows_dir.is_dir():
        err("Microsoft.Flow/flows/", "missing")
        return
    assets = [d for d in flows_dir.iterdir() if d.is_dir()]
    if len(assets) != 1:
        err("Microsoft.Flow/flows/", f"expected one flow asset folder, found {len(assets)}")
        if not assets:
            return
    asset = assets[0]
    for fn in ("definition.json", "apisMap.json", "connectionsMap.json"):
        if not (asset / fn).is_file():
            extra = ("  This is almost certainly what PackageFlowMissingConnectionMap refers to."
                     if fn == "connectionsMap.json" else "")
            err(f"{asset.name}/{fn}", f"missing — a real export contains it.{extra}")

    def js(p):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            err(p.name, f"could not read as JSON: {e}")
            return None

    manifest = js(man) if man.is_file() else None
    defn = js(asset / "definition.json") if (asset / "definition.json").is_file() else None
    apis_map = js(asset / "apisMap.json") if (asset / "apisMap.json").is_file() else {}
    conns_map = js(asset / "connectionsMap.json") if (asset / "connectionsMap.json").is_file() else {}
    if defn is None:
        return

    # ---- 2. manifest resources -------------------------------------------
    resources = (manifest or {}).get("resources") or {}
    apis_res = {k: v for k, v in resources.items()
                if v.get("type") == "Microsoft.PowerApps/apis"}
    conn_res = {k: v for k, v in resources.items()
                if v.get("type") == "Microsoft.PowerApps/apis/connections"}
    flow_res = {k: v for k, v in resources.items()
                if v.get("type") == "Microsoft.Flow/flows"}
    if len(flow_res) != 1:
        err("manifest.resources", f"expected one Microsoft.Flow/flows resource, "
                                  f"found {len(flow_res)}")
    if apis_res and not conn_res:
        err("manifest.resources",
            "there are connector (Microsoft.PowerApps/apis) resources but no connection "
            "(Microsoft.PowerApps/apis/connections) resources. The connections resource is the "
            "one with configurableBy: User — it is what makes the import UI offer a connection "
            "picker, and without it the import cannot map anything")
    for k, v in conn_res.items():
        if v.get("configurableBy") != "User":
            err(f"manifest.resources.{k}", "an apis/connections resource must be "
                                           "configurableBy: User")
        deps = v.get("dependsOn") or []
        if not any(d in apis_res for d in deps):
            err(f"manifest.resources.{k}", "must dependsOn its Microsoft.PowerApps/apis resource")
    for k, v in apis_res.items():
        if v.get("configurableBy") != "System":
            warn(f"manifest.resources.{k}", "an apis resource is configurableBy: System in a "
                                            "real export")

    # ---- 3. the maps ------------------------------------------------------
    for label, m in (("apisMap.json", apis_map), ("connectionsMap.json", conns_map)):
        if not isinstance(m, dict):
            err(label, "must be a flat object mapping connector name to resource GUID")
            continue
        for api, guid in m.items():
            if guid not in resources:
                err(f"{label}[{api}]", f"{guid!r} is not a resource in manifest.json")
    if isinstance(apis_map, dict) and isinstance(conns_map, dict):
        only_apis = set(apis_map) - set(conns_map)
        only_conns = set(conns_map) - set(apis_map)
        for a in sorted(only_apis):
            err("connectionsMap.json", f"{a!r} is in apisMap but not connectionsMap — every "
                                       f"connector needs both")
        for a in sorted(only_conns):
            err("apisMap.json", f"{a!r} is in connectionsMap but not apisMap")

    # ---- 4. connectionReferences -----------------------------------------
    props = defn.get("properties") or {}
    refs = props.get("connectionReferences") or {}
    if not refs:
        err("definition.properties.connectionReferences", "missing or empty")
    for key, ref in refs.items():
        cn = ref.get("connectionName")
        if not cn:
            err(f"connectionReferences.{key}.connectionName", "missing")
        elif cn == key:
            err(f"connectionReferences.{key}.connectionName",
                f"is {cn!r}, the same as the key. In a real export this field is an OPAQUE "
                f"per-connection identifier (a 32-hex string, or shared-<api>-<guid>) — not the "
                f"connector API name. It cannot be authored; carry it verbatim from a real "
                f"export of the target tenant")
        if key not in apis_map and apis_map:
            warn(f"connectionReferences.{key}", "has no entry in apisMap.json")

    # ---- 5. the definition ------------------------------------------------
    inner = props.get("definition") or {}
    if not inner.get("$schema"):
        err("definition.properties.definition.$schema", "missing")
    params = inner.get("parameters") or {}
    for p in ("$connections", "$authentication"):
        if p not in params:
            err(f"definition.parameters.{p}", "missing — required for connector auth at runtime")

    triggers = inner.get("triggers") or {}
    if len(triggers) != 1:
        err("definition.triggers", f"expected exactly one trigger, found {len(triggers)}")
    for tname, trig in triggers.items():
        op = ((trig.get("inputs") or {}).get("host") or {}).get("operationId", "")
        is_array = (trig.get("type") in ARRAY_TRIGGER_TYPES
                    and ARRAY_OPERATION_HINT.match(str(op)))
        split = trig.get("splitOn")
        if is_array and not split:
            err(f"triggers.{tname}.splitOn",
                f"{op} returns an array and has no splitOn. Without it the flow fires ONCE PER "
                f'BATCH instead of once per item. Expected: {SPLIT_ON}')
        if split and not SPLIT_ON_RE.search(str(split)):
            warn(f"triggers.{tname}.splitOn",
                 f"{split!r} is not the observed form: {SPLIT_ON}")
        if split and not is_array:
            warn(f"triggers.{tname}.splitOn",
                 "set on a trigger that does not appear to return an array")

    ops = []
    walk_ops(inner.get("actions") or {}, "actions", ops)
    names = {n for n, _, _ in ops}

    for name, act, path in ops:
        if "operationMetadataId" in act:
            err(f"{path}.operationMetadataId",
                "never appears in a real export — zero occurrences on the trigger or any "
                "action. Do not generate it")
        if "metadata" in act:
            err(f"{path}.metadata", "per-action metadata does not exist in a real export")
        ins = act.get("inputs")
        # A Compose/expression action has a scalar `inputs`, not a mapping.
        host = (ins.get("host") or {}) if isinstance(ins, dict) else {}
        cn = host.get("connectionName")
        if cn and cn not in refs:
            err(f"{path}.inputs.host.connectionName",
                f"{cn!r} is used but not declared in connectionReferences")
        # A real export OMITS runAfter on the first action of a nested scope or condition
        # branch — absence means "start of this scope", and is legal. Only the references
        # themselves have to resolve.
        for dep in (act.get("runAfter") or {}):
            if dep not in names:
                err(f"{path}.runAfter", f"names {dep!r}, which is not an action in this flow")

    # ---- 6. runAfter cycles ----------------------------------------------
    graph = {n: [d for d in (a.get("runAfter") or {}) if d in names] for n, a, _ in ops}
    state = {}

    def cyclic(node, trail):
        state[node] = 1
        for dep in graph.get(node, []):
            if state.get(dep) == 1:
                err("definition.actions",
                    f"runAfter cycle: {' -> '.join(trail + [node, dep])}. The flow will not save")
                return True
            if state.get(dep, 0) == 0 and cyclic(dep, trail + [node]):
                return True
        state[node] = 2
        return False

    for n in graph:
        if state.get(n, 0) == 0 and cyclic(n, []):
            break

    roots = [n for n, deps in graph.items() if not deps]
    if ops and not roots:
        err("definition.actions",
            "every action has a runAfter dependency — nothing can start. At least one action "
            "must have an empty or absent runAfter")

    # ---- 7. leftovers -----------------------------------------------------
    blob = json.dumps(defn, ensure_ascii=False)
    for token in ("REPLACE-", "<TENANT>", "contoso.com", "contoso.sharepoint.com"):
        if token in blob:
            warn("definition.json", f"contains {token!r} — a placeholder is still in the file")


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    target = pathlib.Path(sys.argv[1])
    if not target.exists():
        print(f"No such path: {target}", file=sys.stderr)
        return 2

    tmp = None
    if target.is_file():
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="paflowval-"))
        try:
            with zipfile.ZipFile(target) as z:
                z.extractall(tmp)
        except zipfile.BadZipFile:
            print(f"ERROR  {target} is not a zip", file=sys.stderr)
            return 2
        root = tmp
    else:
        root = target

    validate(root)
    for line in errors + warns:
        print(line)
    print(f"\n{len(errors)} error(s) [PLATFORM], {len(warns)} warning(s).")
    if errors:
        print("Do not import this package. Every ERROR is a structural rule observed in a real "
              "export.")
        return 1
    print("Structure matches a real export.")
    print("Note: this cannot confirm the package imports into YOUR tenant — that depends on "
          "per-connection identifiers only that tenant holds. Treat the first import as a test, "
          "and expect to be asked to pick connections. That prompt is normal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
