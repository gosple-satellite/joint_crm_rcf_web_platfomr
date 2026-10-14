"""Clear the design file back to a single empty page."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import call


def reset(page_name="Foundations"):
    call("run_command", {"command": "select.all"})
    call("run_command", {"command": "edit.delete"})
    for p in json.loads(call("run_command", {"command": "page.list"})[0][0])[1:]:
        call("run_command", {"command": "page.delete", "params": {"id": str(p["id"])}})
    pages = json.loads(call("run_command", {"command": "page.list"})[0][0])
    pid = pages[0]["id"]
    call("run_command", {"command": "page.rename",
                         "params": {"id": str(pid), "name": page_name}})
    call("run_command", {"command": "page.select", "params": {"id": str(pid)}})
    return pid


if __name__ == "__main__":
    print("page", reset(sys.argv[1] if len(sys.argv) > 1 else "Foundations"))
