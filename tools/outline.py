"""Print the node tree of a League Broadcast style variant with the style values that matter for theming."""
import json, sys

KEYS = ("color", "gradient", "fontFamily", "fontWeight", "fontSize", "letterSpacing", "textTransform", "radius", "width")

def show(node, depth=0):
    meta = node.get("_node", {})
    label = meta.get("label") or meta.get("id") or "?"
    print("  " * depth + f"- {label} [{meta.get('type','')}]")
    for section, val in node.items():
        if section.startswith("_") or not isinstance(val, dict):
            continue
        if "_node" in val:
            continue
        flat = []
        def walk(o, p):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, f"{p}.{k}" if p else k)
            elif o not in (None, "", [], False) and any(k.lower() in p.lower() for k in KEYS):
                flat.append(f"{p}={json.dumps(o)[:60]}")
        walk(val, section)
        if flat:
            print("  " * depth + "    " + "; ".join(flat)[:400])
    for val in node.values():
        if isinstance(val, dict) and "_node" in val:
            show(val, depth + 1)

show(json.load(open(sys.argv[1], encoding="utf-8")))
