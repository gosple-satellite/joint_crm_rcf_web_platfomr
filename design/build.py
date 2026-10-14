"""Build the whole design file.

    figcraft --control 47800 figcraft/UIDESIGN.figcraft
    python3 design/build.py

Pages
    Foundations  - tokens, type, geometry, shell, component sheet
    Super-Admin  - the twelve admin screens
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import B, call, send
from _reset import reset

import foundations
import screens

PAGES = ["Foundations", "Super-Admin"]

# screen function name -> (group, ordinal)
SCREEN_ORDER = [
    ("sign_in", 0), ("dashboard", 1), ("tenants", 2), ("tenant_detail", 3),
    ("provision", 4), ("users", 5), ("themes", 6), ("sections", 7),
    ("domains", 8), ("analytics", 9), ("activity", 10), ("settings", 11),
]


def fresh_pages(names):
    reset(names[0])
    for n in names[1:]:
        call("run_command", {"command": "page.add", "params": {"name": n}})
    pages = json.loads(call("run_command", {"command": "page.list"})[0][0])
    return {p["name"]: p["id"] for p in pages}


def select(pid):
    call("run_command", {"command": "page.select", "params": {"id": str(pid)}})


def build_foundations(pid):
    select(pid)
    b = B()
    for fn in foundations.BOARDS:
        fn(b)
    send(b, label="foundations")
    print(f"  foundations: {len(b.nodes)} nodes / {len(foundations.BOARDS)} boards")


def build_screens(pid, only=None):
    made = 0
    for name, _ in SCREEN_ORDER:
        if only and name not in only:
            continue
        fn = getattr(screens, name, None)
        if fn is None:
            print(f"  {name}: not implemented yet")
            continue
        select(pid)
        b = B()
        fn(b)
        send(b, label=name)
        print(f"  {name}: {len(b.nodes)} nodes")
        made += 1
    return made


if __name__ == "__main__":
    args = sys.argv[1:]
    only = None
    if args and args[0] not in ("all",):
        only = set(args)
    ids = fresh_pages(PAGES)
    build_foundations(ids["Foundations"])
    n = build_screens(ids["Super-Admin"], only)
    call("save_file", {})
    print(f"done: {n} screens, saved")