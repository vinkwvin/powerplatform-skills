#!/usr/bin/env python3
"""Empirically measure the conventions in a folder of *.pa.yaml screens.

Reads every *.pa.yaml in the target folder and reports only what is actually
there. No rules are assumed and nothing is inferred: every number printed is a
count over the files.

Uses yaml.compose() rather than safe_load() because scalar *style* matters here —
whether a value used a `|` block scalar is one of the things being measured, and
safe_load discards it.

Usage:  python3 scripts/harvest_yaml.py source-artifacts/yaml
"""
import sys
import re
import pathlib
from collections import Counter, defaultdict

import yaml

RGBA_RE = re.compile(r"RGBA\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)")
SIZING_KEYS = ("Height", "Width", "Size", "FillPortions", "TemplateSize")


class Harvest:
    def __init__(self):
        self.control_types = Counter()                    # "Label@2.5.1" -> n
        self.variants = Counter()                         # (control, variant) -> n
        self.props_by_control = defaultdict(Counter)      # control -> prop -> n
        self.prop_files = defaultdict(set)                # (control, prop) -> {files}
        self.sorted_ok = 0
        self.sorted_bad = 0
        self.sort_violations = []                         # (file, control_name, first_bad_pair)
        self.sizing = defaultdict(Counter)                # key -> value -> n
        self.block_scalars = Counter()                    # prop -> n
        self.block_reasons = defaultdict(Counter)         # prop -> reason -> n
        self.block_no_reason = []                         # (file, prop) with no forcing char
        self.depths = Counter()                           # depth -> n controls
        self.max_depth_per_file = {}
        self.overflow = defaultdict(Counter)              # control -> value -> n
        self.overflow_depths = Counter()
        self.rgba = Counter()
        self.screens = []                                 # (file, screen name)
        self.screen_props = Counter()                     # prop -> n screens
        self.dup_keys = []                                # (file, path, key)

    # ---------- helpers -------------------------------------------------

    @staticmethod
    def _map_items(node):
        """Yield (key_str, value_node) for a MappingNode, preserving order."""
        for k, v in node.value:
            yield k.value, v

    @staticmethod
    def _why_block(text):
        """Which characters plausibly forced a block scalar, per YAML rules."""
        reasons = []
        if "\n" in text.strip():
            reasons.append("multiline")
        if ": " in text:
            reasons.append("': ' (colon-space)")
        if " #" in text:
            reasons.append("' #' (comment marker)")
        if text.lstrip().startswith(("&", "*", "!", "%", "@", "`")):
            reasons.append("leading indicator char")
        if text.rstrip() != text:
            reasons.append("trailing whitespace")
        return reasons

    # ---------- walkers -------------------------------------------------

    def properties(self, fname, owner, node, is_screen=False):
        keys = []
        seen = set()
        for key, vnode in self._map_items(node):
            if key in seen:
                self.dup_keys.append((fname, owner, key))
            seen.add(key)
            keys.append(key)

            if is_screen:
                self.screen_props[key] += 1
            else:
                self.props_by_control[owner][key] += 1
                self.prop_files[(owner, key)].add(fname)

            if isinstance(vnode, yaml.ScalarNode):
                if key in SIZING_KEYS:
                    self.sizing[key][vnode.value.strip()] += 1
                if vnode.style == "|":
                    self.block_scalars[key] += 1
                    why = self._why_block(vnode.value)
                    if why:
                        for r in why:
                            self.block_reasons[key][r] += 1
                    else:
                        self.block_no_reason.append((fname, key))
                if key == "LayoutOverflowY":
                    self.overflow[owner][vnode.value.strip()] += 1

        lowered = [k.lower() for k in keys]
        if lowered == sorted(lowered):
            self.sorted_ok += 1
        else:
            self.sorted_bad += 1
            pair = next(
                (f"{keys[i]} before {keys[i+1]}"
                 for i in range(len(lowered) - 1) if lowered[i] > lowered[i + 1]),
                "?",
            )
            self.sort_violations.append((fname, owner, pair))

    def children(self, fname, node, depth):
        """node is a SequenceNode of single-key mappings: - Name: {Control:, ...}"""
        for item in node.value:
            if not isinstance(item, yaml.MappingNode):
                continue
            for name, body in self._map_items(item):
                if not isinstance(body, yaml.MappingNode):
                    continue
                fields = dict(self._map_items(body))
                ctrl = fields["Control"].value.strip() if "Control" in fields else "(no Control)"
                self.control_types[ctrl] += 1
                self.depths[depth] += 1
                self.max_depth_per_file[fname] = max(
                    self.max_depth_per_file.get(fname, 0), depth
                )
                if "Variant" in fields:
                    self.variants[(ctrl, fields["Variant"].value.strip())] += 1
                if "Properties" in fields:
                    self.properties(fname, ctrl, fields["Properties"])
                    if "LayoutOverflowY" in dict(self._map_items(fields["Properties"])):
                        self.overflow_depths[depth] += 1
                if "Children" in fields:
                    self.children(fname, fields["Children"], depth + 1)

    def file(self, path):
        fname = path.name
        raw = path.read_text(encoding="utf-8")
        for m in RGBA_RE.finditer(raw):
            self.rgba[re.sub(r"\s+", "", m.group(0))] += 1

        root = yaml.compose(raw)
        top = dict(self._map_items(root))
        if "Screens" not in top:
            print(f"  !! {fname}: no top-level 'Screens' key", file=sys.stderr)
            return
        for screen_name, screen in self._map_items(top["Screens"]):
            self.screens.append((fname, screen_name))
            sf = dict(self._map_items(screen))
            if "Properties" in sf:
                self.properties(fname, f"SCREEN:{screen_name}", sf["Properties"], is_screen=True)
            if "Children" in sf:
                self.children(fname, sf["Children"], 1)


def report(h, n_files):
    def hdr(t):
        print(f"\n{'=' * 74}\n{t}\n{'=' * 74}")

    print(f"{n_files} files, {len(h.screens)} screens, "
          f"{sum(h.control_types.values())} controls")

    hdr("1. CONTROL TYPES")
    for ctrl, n in h.control_types.most_common():
        vs = [f"{var} x{cnt}" for (c, var), cnt in h.variants.items() if c == ctrl]
        print(f"  {n:5}  {ctrl}" + (f"   variants: {', '.join(vs)}" if vs else ""))

    hdr("2. PROPERTIES PER CONTROL TYPE  (prop:count, files/17)")
    for ctrl, _ in h.control_types.most_common():
        props = h.props_by_control[ctrl]
        print(f"\n  {ctrl}  ({sum(props.values())} property uses, {len(props)} distinct)")
        for p, n in props.most_common():
            print(f"      {p:24} {n:5}   {len(h.prop_files[(ctrl, p)])}/{n_files} files")

    hdr("3. SCREEN-LEVEL PROPERTIES")
    for p, n in h.screen_props.most_common():
        print(f"  {p:26} {n}/{len(h.screens)} screens")

    hdr("4. ALPHABETICAL SORTING WITHIN Properties BLOCKS")
    tot = h.sorted_ok + h.sorted_bad
    print(f"  sorted:     {h.sorted_ok}/{tot}")
    print(f"  violations: {h.sorted_bad}/{tot}")
    for f, owner, pair in h.sort_violations[:20]:
        print(f"      {f}  {owner}  -> {pair}")
    if len(h.sort_violations) > 20:
        print(f"      ... {len(h.sort_violations) - 20} more")

    hdr("5. SIZING VALUES")
    for k in SIZING_KEYS:
        vals = h.sizing[k]
        print(f"\n  {k}  ({sum(vals.values())} uses, {len(vals)} distinct)")
        for v, n in vals.most_common(25):
            print(f"      {n:5}  {v}")
        if len(vals) > 25:
            print(f"      ... {len(vals) - 25} more distinct values")

    hdr("6. BLOCK SCALARS  ( | )")
    if not h.block_scalars:
        print("  none")
    for p, n in h.block_scalars.most_common():
        print(f"  {p:22} {n:4}   forced by: "
              f"{', '.join(f'{r} x{c}' for r, c in h.block_reasons[p].most_common())}")
    if h.block_no_reason:
        print(f"\n  !! {len(h.block_no_reason)} block scalars with NO forcing character "
              f"(style choice, not necessity):")
        for f, p in h.block_no_reason[:10]:
            print(f"      {f}  {p}")

    hdr("7. NESTING DEPTH")
    for d in sorted(h.depths):
        print(f"  depth {d}: {h.depths[d]:5} controls")
    print(f"\n  max depth per file:")
    for f in sorted(h.max_depth_per_file):
        print(f"      {h.max_depth_per_file[f]}  {f}")

    hdr("8. LayoutOverflowY")
    if not h.overflow:
        print("  never appears")
    for ctrl, vals in h.overflow.items():
        for v, n in vals.most_common():
            print(f"  {n:4}  {ctrl:22} {v}")
    if h.overflow_depths:
        print(f"\n  by nesting depth: "
              f"{', '.join(f'depth {d}: {n}' for d, n in sorted(h.overflow_depths.items()))}")

    hdr("9. RGBA VALUES")
    print(f"  {len(h.rgba)} distinct, {sum(h.rgba.values())} uses")
    for v, n in h.rgba.most_common():
        print(f"      {n:5}  {v}")

    if h.dup_keys:
        hdr("10. DUPLICATE KEYS WITHIN A Properties BLOCK")
        for f, owner, k in h.dup_keys:
            print(f"  {f}  {owner}  {k}")


def main():
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "source-artifacts/yaml")
    files = sorted(folder.glob("*.pa.yaml"))
    if not files:
        print(f"No *.pa.yaml in {folder}", file=sys.stderr)
        return 2
    h = Harvest()
    for p in files:
        h.file(p)
    report(h, len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
