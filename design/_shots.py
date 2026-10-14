"""Export each top-level board frame to its own PNG."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import call

OUT = "/tmp/opencode/boards"
os.makedirs(OUT, exist_ok=True)


def boards():
    docs = call("inspect_document", {"depth": 1})[0][0]
    d = json.loads(docs)
    return [(c["id"], c["name"]) for p in d["pages"] for c in (p.get("children") or [])]


if __name__ == "__main__":
    for bid, name in boards():
        slug = name.replace(" — ", "-").replace(" ", "_").replace("·", "")
        path = f"{OUT}/{slug}.png"
        call("export", {"path": path, "format": "png", "scale": 1,
                        "ids": [str(bid)]})
        print(bid, name, "->", path)
