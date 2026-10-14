"""FigCraft command builder.

FigCraft's `parent` takes a layer *id*, not a name, and ids are only known
once the command runs. So the builder is two-phase:

    b = B(); ...compose with Node handles...
    created  = run_batch(b.create_batch())   # nodes created parentless
    b.resolve(created)                       # handle -> real id
    run_batch(b.props_batch())               # reparent + apply props

create_batch() emits nodes in tree order, so parents are always created
before their children and reparenting in that same order is safe.
"""
import json
import subprocess
import os

PORT = os.environ.get("FIGCRAFT_PORT", "47800")


class Node:
    __slots__ = ("kind", "name", "props", "parent", "text", "id")

    def __init__(self, kind, name, props, parent, text=None):
        self.kind = kind
        self.name = name
        self.props = props
        self.parent = parent
        self.text = text
        self.id = None

    def __repr__(self):
        return f"<{self.kind} {self.name}>"


class B:
    def __init__(self):
        self.nodes = []
        self.extras = []          # raw commands needing no id resolution
        self.root = []            # top-level parents (Nodes)

    # ---- construction ------------------------------------------------

    def _n(self, kind, name, props, parent, text=None):
        node = Node(kind, name, props, parent, text)
        self.nodes.append(node)
        return node

    def frame(self, name, parent=None, **p):
        return self._n("frame", name, self._fd(p), parent)

    def rect(self, parent=None, name="rect", **p):
        return self._n("rectangle", name, p, parent)

    def ell(self, parent=None, name="ellipse", **p):
        return self._n("ellipse", name, p, parent)

    def text(self, t, parent=None, name=None, **p):
        return self._n("text", name or t[:32], p, parent, t)

    @staticmethod
    def _fd(p):
        """Frame defaults: transparent containers that hug their content.

        FigCraft hands back opaque white 100x100 frames, which both hide
        their children and stop a row of controls from laying out.
        """
        p = dict(p)
        lay = p.get("layout")
        if lay:
            p.setdefault("fill", CLEAR)
            # An explicit width/height means "a real box", not a hugger.
            if "width" in p:
                p.setdefault("sizingH", "fixed")
            else:
                p.setdefault("sizingH", "hug")
            if "height" in p:
                p.setdefault("sizingV", "fixed")
            else:
                p.setdefault("sizingV", "hug")
        return p

    def v(self, name, parent=None, gap=8, pad=0, **p):
        return self.frame(name, parent=parent, layout="vertical",
                          gap=gap, padding=p.pop("padding", pad), **p)

    def h(self, name, parent=None, gap=8, pad=0, **p):
        return self.frame(name, parent=parent, layout="horizontal",
                          gap=gap, padding=p.pop("padding", pad), **p)

    def raw(self, command, **params):
        self.extras.append({"command": command, "params": params})

    def root_of(self, node):
        self.root.append(node)
        return node

    # ---- emission ----------------------------------------------------

    def create_batch(self):
        out = []
        for n in self.nodes:
            params = {"type": n.kind, "name": n.name, "select": False}
            if n.text is not None:
                params["text"] = n.text
            path = n.props.get("_path")
            if path:
                params["path"] = path
            out.append({"command": "node.create", "params": params})
        return self.extras + out

    def resolve(self, results):
        """results = list returned by the create batch, same length as nodes."""
        start = len(self.extras)
        for i, n in enumerate(self.nodes):
            r = results[start + i]
            n.id = r.get("id") or (r.get("result") or {}).get("id")

    def props_batch(self):
        """Interleave reparent + props in tree order.

        Parents are always earlier in self.nodes, so by the time a child's
        props land its parent is already inside the layout tree with its own
        layout applied - which sizingH/sizingV="fill" requires.
        """
        out = []
        for n in self.nodes:
            if n.parent is not None and n.parent.id is not None:
                out.append({"command": "node.reparent",
                            "params": {"ids": [n.id], "parent": n.parent.id}})
            if n.props:
                # keys starting with "_" are builder-internal (e.g. _path)
                props = {k: v for k, v in n.props.items()
                         if not k.startswith("_")}
                out.append({"command": "node.set",
                            "params": {"ids": [n.id], "props": props}})
        return out


# ---- transport -----------------------------------------------------

def _rpc(proc, msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("figcraft control channel closed")
        try:
            resp = json.loads(line)
        except json.JSONDecodeError:
            continue
        if resp.get("id") == msg.get("id"):
            return resp


def _session():
    proc = subprocess.Popen(
        ["figcraft-cli", "mcp", "--attach", PORT],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, bufsize=1)
    _rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "figbuild", "version": "1"}}})
    proc.stdin.write(json.dumps({"jsonrpc": "2.0",
                                 "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()
    return proc


def call(tool, args, proc=None):
    own = proc is None
    proc = proc or _session()
    try:
        r = _rpc(proc, {"jsonrpc": "2.0", "id": 99, "method": "tools/call",
                        "params": {"name": tool, "arguments": args}})
        res = r.get("result", {})
        texts = [c["text"] for c in res.get("content", []) if c.get("type") == "text"]
        return texts, r
    finally:
        if own:
            proc.stdin.close()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


def batch_text(r):
    """FigCraft reports per-command failures as text inside content."""
    out = []
    for c in r.get("result", {}).get("content", []):
        if c.get("type") != "text":
            continue
        t = c["text"].strip()
        for ln in t.splitlines():
            ln = ln.strip()
            if any(w in ln.lower() for w in
                   ("error", "invalid", "not available", "unknown",
                    "failed", "cannot", "must ")):
                out.append(ln)
    if r.get("error"):
        out.append(json.dumps(r["error"]))
    return out


def send(b, proc=None, label="build"):
    """Create + resolve + apply props for a builder, on one session."""
    own = proc is None
    proc = proc or _session()
    try:
        _, r = call("batch", {"commands": b.create_batch(),
                              "label": label + ":create"}, proc)
        errs = batch_text(r)
        if errs:
            raise RuntimeError("CREATE failed:\n  " + "\n  ".join(errs[:6]))
        results = []
        for c in r.get("result", {}).get("content", []):
            if c.get("type") != "text":
                continue
            raw = c["text"].strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = []
                for ln in raw.splitlines():
                    ln = ln.strip().rstrip(",")
                    if ln.startswith("{"):
                        try:
                            parsed.append(json.loads(ln))
                        except json.JSONDecodeError:
                            pass
            if isinstance(parsed, dict):
                parsed = [parsed]
            results.extend(parsed)
        b.resolve(results)
        _, r2 = call("batch", {"commands": b.props_batch(),
                               "label": label + ":props"}, proc)
        errs = batch_text(r2)
        if errs:
            raise RuntimeError("PROPS failed:\n  " + "\n  ".join(errs[:6]))
        return b
    finally:
        if own:
            proc.stdin.close()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


def export_png(path, scale=1, ids=None, max_side=None):
    args = {"path": path, "format": "png", "scale": scale}
    if ids:
        args["ids"] = ids
    texts, _ = call("export", args)
    return texts


def shot_window(out, max_side=1400):
    import base64
    _, r = call("screenshot", {"window": True})
    for c in r.get("result", {}).get("content", []):
        if c.get("type") == "image":
            with open(out, "wb") as f:
                f.write(base64.b64decode(c["data"]))
            return out
    return None


# ---- design tokens -------------------------------------------------
# Mirrors docs/superpowers/specs/2026-10-14-admin-design-system.md

C = {
    "canvas": "#F7F8FA", "surface": "#FFFFFF", "subtle": "#F1F3F6",
    "inverse": "#101828",
    "borderSubtle": "#EDEFF3", "border": "#E4E7EC", "borderStrong": "#CDD3DC",
    "text": "#101828", "textSec": "#475467", "textMuted": "#667085",
    "textInv": "#FFFFFF",
    "primary": "#1B3A5C", "primaryHover": "#14293F",
    "accent": "#2E6BE6", "accentHover": "#2559C4",
    "success": "#067647", "successBg": "#ECFDF3", "successBd": "#ABEFC6",
    "warning": "#B54708", "warningBg": "#FFFAEB", "warningBd": "#FEDF89",
    "danger":  "#B42318", "dangerBg":  "#FEF3F2", "dangerBd":  "#FECDCA",
    "info":    "#175CD3", "infoBg":    "#EFF8FF", "infoBd":    "#B2DDFF",
    "neutral": "#475467", "neutralBg": "#F2F4F7", "neutralBd": "#E4E7EC",
}

def _rgba(hexv, a):
    h = hexv.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)] + [a]


def _shadow(a1, off1, r1, sp1, a2=None, off2=None, r2=None, sp2=None):
    """FigCraft drop shadows: dropShadow + RGBA float colour."""
    out = [{"type": "dropShadow", "color": _rgba("#101828", a1),
            "offset": off1, "radius": r1, "spread": sp1}]
    if a2 is not None:
        out.append({"type": "dropShadow", "color": _rgba("#101828", a2),
                    "offset": off2, "radius": r2, "spread": sp2})
    return out


S1 = _shadow(0.06, [0, 1], 2, 0)
S2 = _shadow(0.10, [0, 4], 8, -2, 0.06, [0, 2], 4, -2)
S3 = _shadow(0.14, [0, 20], 24, -4)
FOCUS_RING = [{"type": "dropShadow", "color": _rgba(C["accent"], 0.24),
               "offset": [0, 0], "radius": 3, "spread": 3}]

UI = "Inter"
SERIF = "Source Serif 4"
CLEAR = "#FFFFFF00"


def tone(name):
    return (C[name + "Bg"], C[name + "Bd"], C[name])


# ---- typed text helpers --------------------------------------------
#
# wrap=<px> makes the text fold inside a fixed-width box: it switches
# textAutoResize to "height" and pins a width. Without it every helper hugs
# its content and will overflow any container narrower than the string.


def _txt(b, t, parent, font, size, weight, lh, color, wrap, ls=None,
         case=None, align=None):
    p = dict(fontFamily=font, fontSize=size, fontStyle=weight,
             lineHeight=f"{lh}px", fill=color or C["text"])
    if ls is not None:
        p["letterSpacing"] = ls
    if case:
        p["textCase"] = case
    if align:
        p["textAlign"] = align
    if wrap:
        p["width"] = wrap
        p["textAutoResize"] = "height"
    else:
        p["textAutoResize"] = "widthAndHeight"
    return b.text(t, parent=parent, **p)


def t_micro(b, t, parent, color=None, wrap=None):
    return _txt(b, t, parent, UI, 11, "SemiBold", 16, color or C["textMuted"],
                wrap, ls=0.44, case="upper")


def t_meta(b, t, parent, color=None, weight="Regular", wrap=None):
    return _txt(b, t, parent, UI, 12, weight, 16, color or C["textMuted"],
                wrap)


def t_body(b, t, parent, color=None, weight="Regular", wrap=None, align=None):
    return _txt(b, t, parent, UI, 13, weight, 20, color or C["text"], wrap,
                align=align)


def t_ui(b, t, parent, color=None, weight="Regular", wrap=None):
    return _txt(b, t, parent, UI, 14, weight, 20, color or C["text"], wrap)


def t_card(b, t, parent, color=None, wrap=None):
    return _txt(b, t, parent, UI, 16, "SemiBold", 24, color or C["text"],
                wrap, ls=-0.16)


def t_page(b, t, parent, color=None, wrap=None):
    return _txt(b, t, parent, UI, 20, "SemiBold", 28, color or C["text"],
                wrap, ls=-0.4)


def t_stat(b, t, parent, color=None, wrap=None):
    return _txt(b, t, parent, UI, 24, "Bold", 32, color or C["text"], wrap,
                ls=-0.4)


def t_display(b, t, parent, color=None, w=None):
    return _txt(b, t, parent, SERIF, 32, "SemiBold", 40, color or C["text"],
                w, ls=-0.4, align="center")


# ---- components ----------------------------------------------------

SIDES = {"t": 0, "r": 1, "b": 2, "l": 3}


def sides(*names):
    """FigCraft takes strokeSides as [top, right, bottom, left] booleans."""
    v = [False, False, False, False]
    for n in names:
        v[SIDES[n]] = True
    return v


CHECK_PATH = "M2.5 6.8 L5.2 9.6 L11.5 2.6"


def check(b, parent, color=None, size=12, weight=2):
    """A checkmark drawn as a vector path.

    Inter's bundled build has no U+2713, so a text glyph silently renders
    as a blank box. A path always draws.
    """
    node = Node("vector", "check", {
        "fill": CLEAR, "stroke": color or C["success"], "strokeWeight": weight,
        "strokeCap": "round", "strokeJoin": "round", "width": size,
        "height": size, "sizingH": "fixed", "sizingV": "fixed",
        "_path": CHECK_PATH,
    }, parent)
    b.nodes.append(node)
    return node


def spacer(b, parent, horizontal=True):
    """Fill-the-remainder gap.

    Must be explicitly 1px tall: an unsized frame is 100x100 and would
    stretch whatever hugs it.
    """
    if horizontal:
        return b.frame("spacer", parent=parent, sizingH="fill",
                       sizingV="fixed", height=1, fill=CLEAR)
    return b.frame("spacer", parent=parent, sizingH="fixed",
                   sizingV="fill", width=1, fill=CLEAR)


def card_props(parent_fill=None):
    return {"fill": parent_fill or C["surface"], "stroke": C["border"],
            "strokeWeight": 1, "strokeAlign": "inside", "cornerRadius": 6,
            "effects": S1, "clip": True}


def btn(b, label, parent, kind="secondary", size="md", full=False, **over):
    h = {"sm": 32, "md": 36, "lg": 40}[size]
    pad = 16 if size == "sm" else 20
    fs = 13 if size == "sm" else 14
    style = {
        "primary":   {"fill": C["primary"],   "fg": C["textInv"]},
        "accent":    {"fill": C["accent"],    "fg": C["textInv"]},
        "secondary": {"fill": C["surface"],   "fg": C["text"],
                      "stroke": C["border"]},
        "ghost":     {"fill": CLEAR,          "fg": C["textSec"]},
        "danger":    {"fill": C["dangerBg"],  "fg": C["danger"],
                      "stroke": C["dangerBd"]},
    }[kind]
    props = {"height": h, "cornerRadius": 4, "padding": [0, pad],
             "layout": "horizontal", "mainAlign": "center",
             "crossAlign": "center", "sizingH": "hug", "sizingV": "fixed",
             "clip": True, "fill": style["fill"]}
    if style.get("stroke"):
        props["stroke"] = style["stroke"]
        props["strokeWeight"] = 1
        props["strokeAlign"] = "inside"
    if full:
        props["sizingH"] = "fill"
        props["mainAlign"] = "center"
    props.update(over)
    f = b.frame(f"btn: {label}", parent=parent, **props)
    lt = b.text(label, parent=f, fontFamily=UI, fontSize=fs,
                fontStyle="SemiBold", lineHeight=f"{h}px", fill=style["fg"],
                textAutoResize="widthAndHeight")
    if full:
        lt.props["sizingH"] = "fill"
        lt.props["textAlign"] = "center"
    return f


def icon_btn(b, glyph, parent, kind="secondary", size="md", **over):
    h = {"sm": 32, "md": 36, "lg": 40}[size]
    style = {"secondary": (C["surface"], C["border"], C["textSec"]),
             "ghost": (CLEAR, None, C["textSec"]),
             "danger": (C["dangerBg"], C["dangerBd"], C["danger"])}[kind]
    props = {"width": h, "height": h, "cornerRadius": 4,
             "layout": "horizontal", "mainAlign": "center",
             "crossAlign": "center", "clip": True, "fill": style[0]}
    if style[1]:
        props["stroke"] = style[1]
        props["strokeWeight"] = 1
        props["strokeAlign"] = "inside"
    props.update(over)
    f = b.frame(f"icon: {glyph}", parent=parent, **props)
    b.text(glyph, parent=f, fontFamily=UI, fontSize=15, lineHeight=f"{h}px",
           fill=style[2], textAutoResize="widthAndHeight")
    return f


def badge(b, label, parent, t="neutral", h=20, pad=8, dot=False):
    bg, bd, fg = tone(t)
    f = b.frame(f"badge: {label}", parent=parent, height=h,
                cornerRadius=999, padding=[0, pad], layout="horizontal",
                mainAlign="center", crossAlign="center", gap=6,
                sizingH="hug", sizingV="fixed", clip=True,
                fill=bg, stroke=bd, strokeWeight=1, strokeAlign="inside")
    if dot:
        b.ell(parent=f, width=6, height=6, fill=fg)
    b.text(label, parent=f, fontFamily=UI, fontSize=12, fontStyle="SemiBold",
           lineHeight="20px", fill=fg, textAutoResize="widthAndHeight")
    return f


def field(b, label, placeholder, parent, w="fill", state="default",
          note=None, icon=None, trailing=None):
    # w is either the literal "fill" or a pixel width
    sizing = {"sizingH": "fill"} if w == "fill" else {"width": w,
                                                       "sizingH": "fixed"}
    wrap = b.v(f"field: {label}", parent=parent, gap=6, **sizing)
    b.text(label, parent=wrap, fontFamily=UI, fontSize=14,
           fontStyle="Medium", lineHeight="20px", fill=C["text"],
           textAutoResize="widthAndHeight")
    bd = {"default": C["border"], "hover": C["borderStrong"],
          "error": C["danger"], "focus": C["accent"],
          "disabled": C["border"]}[state]
    fl = {"default": C["surface"], "hover": C["surface"],
          "error": C["surface"], "focus": C["surface"],
          "disabled": C["subtle"]}[state]
    inp = b.frame(f"input: {label}", parent=wrap, height=36, cornerRadius=4,
                  fill=fl, stroke=bd, strokeWeight=1, strokeAlign="inside",
                  clip=True, layout="horizontal", crossAlign="center",
                  padding=[0, 12], gap=8, **sizing)
    if state == "focus":
        inp.props["effects"] = FOCUS_RING
    # order matters: leading icon, value, filler, trailing action
    if icon:
        b.text(icon, parent=inp, fontFamily=UI, fontSize=14,
               lineHeight="36px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
    b.text(placeholder, parent=inp, fontFamily=UI, fontSize=14,
           lineHeight="36px", fill=C["textMuted"], sizingH="fill",
           textAutoResize="widthAndHeight")
    if trailing:
        b.frame("spacer", parent=inp, sizingH="fill", sizingV="fixed",
                height=1, fill=CLEAR)
        b.text(trailing, parent=inp, fontFamily=UI, fontSize=13,
               fontStyle="Medium", lineHeight="36px", fill=C["accent"],
               textAutoResize="widthAndHeight")
    if note:
        b.text(note, parent=wrap, fontFamily=UI, fontSize=12, lineHeight="16px",
               fill=C["danger"] if state == "error" else C["textMuted"],
               textAutoResize="widthAndHeight")
    return wrap


def swatch(b, name, hexv, parent, size=32, r=6):
    row = b.h(f"swatch: {name}", parent=parent, gap=10, crossAlign="center")
    b.rect(parent=row, width=size, height=size, fill=hexv, cornerRadius=r,
           stroke=C["border"], strokeWeight=1, strokeAlign="inside")
    col = b.v("swatch meta", parent=row, gap=1)
    t_body(b, name, col, C["text"], "Medium")
    t_meta(b, hexv.upper(), col, C["textMuted"])
    return row


def section(b, name, parent, title, note=None, w="fill"):
    col = b.v(name, parent=parent, gap=6, sizingH=w)
    if w != "fill":
        col.props["width"] = w
    t_micro(b, title, col)
    if note:
        t_meta(b, note, col, C["textMuted"])
    return col


def divider(b, parent, horizontal=True, w=None, h=None, color=None):
    """Hairline rule. `fill` is expressed via sizing, never via width."""
    props = {"fill": color or C["borderSubtle"]}
    if horizontal:
        props["height"] = h or 1
        props["sizingH"] = "fixed" if w else "fill"
        props["sizingV"] = "fixed"
        if w:
            props["width"] = w
    else:
        props["width"] = w or 1
        props["sizingH"] = "fixed"
        props["sizingV"] = "fixed" if h else "fill"
        if h:
            props["height"] = h
    return b.frame("divider", parent=parent, **props)


def kpi(b, label, value, delta, tone_name, parent, w=248):
    props = card_props()
    props.update({"layout": "vertical", "gap": 12, "padding": 20,
                  "sizingH": "fixed" if w != "fill" else "fill",
                  "sizingV": "hug"})
    if w != "fill":
        props["width"] = w
    f = b.frame(f"kpi: {label}", parent=parent, **props)
    t_micro(b, label, f)
    row = b.h("kpi value", parent=f, gap=8, crossAlign="center")
    t_stat(b, value, row, C["text"])
    if delta:
        badge(b, delta, row, tone_name, h=20)
    return f

def cell(b, value, parent, w, size=13, weight="Regular", color=None,
          align="min", wrap=False):
    """A fixed-width table cell.

    Text nodes ignore `width` when textAutoResize is widthAndHeight, so the
    width has to live on a wrapping frame for columns to line up.
    """
    f = b.frame("cell", parent=parent, width=w, layout="horizontal",
                crossAlign="center", fill=CLEAR,
                sizingH="fixed", sizingV="hug")
    t = b.text(value, parent=f, fontFamily=UI, fontSize=size,
               fontStyle=weight, lineHeight="20px",
               fill=color or C["text"],
               textAutoResize="height" if wrap else "widthAndHeight")
    if wrap:
        t.props["width"] = w
    if align in ("center", "right", "justified"):
        t.props["textAlign"] = align
    return f


def cell_stack(b, lines, parent, w):
    """A fixed-width table cell with a primary and a secondary line."""
    f = b.frame("cell stack", parent=parent, width=w, layout="vertical",
                gap=1, crossAlign="min", fill=CLEAR,
                sizingH="fixed", sizingV="hug")
    for txt, sz, wt, col in lines:
        b.text(txt, parent=f, fontFamily=UI, fontSize=sz, fontStyle=wt,
               lineHeight="16px", fill=col, textAutoResize="widthAndHeight")
    return f


def tab_row(b, parent, items, active=0, height=40, color=None,
            border=True):
    """Horizontal tabs with the active underline sitting under its label.

    The underline lives inside a per-tab frame; as a sibling of the labels it
    would land after the last tab.
    """
    row = b.h("tabs", parent=parent, gap=24, crossAlign="min",
              height=height, sizingH="fill",
              stroke=C["border"], strokeWeight=1, strokeSides=sides("b"),
              strokeAlign="inside") if border else \
        b.h("tabs", parent=parent, gap=24, crossAlign="min", height=height,
            sizingH="fill", fill=CLEAR)
    for i, t in enumerate(items):
        is_a = i == active
        tb = b.v(f"tab: {t}", parent=row, gap=0, crossAlign="center",
                 fill=CLEAR, height=height)
        b.text(t, parent=tb, fontFamily=UI, fontSize=14,
               fontStyle="Medium" if is_a else "Regular",
               lineHeight=f"{height - 2}px",
               fill=(color or C["text"]) if is_a else C["textSec"],
               textAutoResize="widthAndHeight")
        u = b.rect(parent=tb, width="fill", height=2,
                   fill=C["accent"] if is_a else CLEAR)
        u.props.pop("width", None)
        u.props["sizingH"] = "fill"
    return row
