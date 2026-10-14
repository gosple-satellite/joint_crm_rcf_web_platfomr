"""Export the Tenant (RCF) page frames to PNG."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import call

OUT = "/tmp/opencode/tenant"
os.makedirs(OUT, exist_ok=True)

d = json.loads(call("inspect_document", {"depth": 1})[0][0])
for p in d["pages"]:
    if p["name"] != "Tenant (RCF)":
        continue
    for c in (p.get("children") or []):
        slug = c["name"].replace(" — ", "-").replace(" ", "_")
        path = f"{OUT}/{slug}.png"
        call("export", {"path": path, "format": "png", "scale": 1,
                        "ids": [str(c["id"])]})
        print("->", path)
