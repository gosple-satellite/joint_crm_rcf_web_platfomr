"""Export every top-level frame on every page to PNG."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import call

OUT = "/tmp/opencode/screens"
os.makedirs(OUT, exist_ok=True)


def frames():
    d = json.loads(call("inspect_document", {"depth": 1})[0][0])
    out = []
    for p in d["pages"]:
        for c in (p.get("children") or []):
            out.append((c["id"], c["name"], p["name"]))
    return out


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for bid, name, page in frames():
        if only and only not in name:
            continue
        slug = name.replace(" — ", "-").replace(" ", "_").replace("·", "")
        path = f"{OUT}/{page}-{slug}.png"
        call("export", {"path": path, "format": "png", "scale": 1,
                        "ids": [str(bid)]})
        print("->", path)
