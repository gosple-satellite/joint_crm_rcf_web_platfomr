"""Foundations boards — tokens, type, geometry, shell, component sheet.

Renders into figcraft/UIDESIGN.figcraft via the live FigCraft app.

    python3 design/foundations.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import *          # noqa: F403,F401
from figbuild import (B, C, UI, SERIF, CLEAR, S1, S2, S3, FOCUS_RING, tone,
                      btn, icon_btn, badge, field, swatch, section, divider,
                      kpi, card_props, sides, cell, cell_stack, tab_row, t_micro, t_meta, t_body, t_ui, t_card,
                      t_page, t_stat, t_display, send, call, batch_text)
from _reset import reset

W = 1440
PAD = 40
GUT = 32


def board(b, name, x, title, subtitle):
    f = b.root_of(b.frame(name, x=x, y=0, width=W, layout="vertical",
                          gap=GUT, padding=PAD, fill=C["canvas"],
                          sizingV="hug", clip=True))
    hdr = b.v("board header", parent=f, gap=6, sizingH="fill")
    t_page(b, title, hdr)
    t_meta(b, subtitle, hdr, C["textMuted"])
    divider(b, f, color=C["border"])
    return f


def cols(b, parent, n, gap=GUT, pad=0):
    """A horizontal row of n equal-width vertical columns."""
    row = b.frame("cols", parent=parent, layout="horizontal", gap=gap,
                  padding=pad, sizingH="fill", crossAlign="min")
    out = []
    for i in range(n):
        col = b.frame(f"col {i + 1}", parent=row, layout="vertical", gap=12,
                      sizingH="fill", sizingV="hug", fill=CLEAR)
        out.append(col)
    return row, out


def demo(b, parent, title, note=None, w="fill", surface=None):
    """A small boxed example with a micro caption."""
    wrap = b.v(f"demo: {title}", parent=parent, gap=8, sizingH=w)
    if w != "fill":
        wrap.props["width"] = w
    surface = surface or C["subtle"]
    if note:
        t_micro(b, title, wrap)
    box = b.frame("demo surface", parent=wrap, fill=surface,
                  stroke=C["borderSubtle"], strokeWeight=1,
                  strokeAlign="inside", cornerRadius=6, layout="vertical",
                  gap=12, padding=20, sizingH="fill", sizingV="hug", clip=True)
    return box, wrap


# ---------------------------------------------------------------------
# 00 · Colour
# ---------------------------------------------------------------------

def colour(b):
    f = board(b, "00 — Colour", 0, "Colour",
              "Semantic tokens, named by role. Light mode only.")

    row, c = cols(b, f, 5)
    groups = [
        ("Surface", [("bg.canvas", C["canvas"]), ("bg.surface", C["surface"]),
                     ("bg.subtle", C["subtle"]), ("bg.inverse", C["inverse"])]),
        ("Border", [("border.subtle", C["borderSubtle"]),
                    ("border.default", C["border"]),
                    ("border.strong", C["borderStrong"])]),
        ("Text", [("text.primary", C["text"]), ("text.secondary", C["textSec"]),
                  ("text.muted", C["textMuted"]), ("text.inverse", C["textInv"])]),
        ("Action", [("action.primary", C["primary"]),
                    ("action.accent", C["accent"]),
                    ("focus.ring", C["accent"])]),
    ]
    for i, (title, items) in enumerate(groups):
        t_micro(b, title, c[i])
        for name, hexv in items:
            swatch(b, name, hexv, c[i])

    t_micro(b, "Status", c[4])
    for name in ("success", "warning", "danger", "info", "neutral"):
        bg, bd, fg = tone(name)
        line = b.frame(f"status: {name}", parent=c[4], layout="horizontal",
                       gap=8, crossAlign="center", fill=CLEAR)
        b.rect(parent=line, width=32, height=32, fill=bg, cornerRadius=6,
               stroke=bd, strokeWeight=1, strokeAlign="inside")
        b.text(name, parent=line, fontFamily=UI, fontSize=13,
               fontStyle="Medium", lineHeight="32px", fill=fg,
               textAutoResize="widthAndHeight")

    # live status badges
    box, wrap = demo(b, f, "Status triplets in use")
    strip = b.h("badge strip", parent=box, gap=10, wrap=True)
    for lbl, tn in (("Active", "success"), ("Pending", "warning"),
                    ("Suspended", "danger"), ("Verified", "success"),
                    ("Failed", "danger"), ("Unverified", "warning"),
                    ("Published", "info"), ("Draft", "neutral")):
        badge(b, lbl, strip, t=tn, dot=True)
    return f


# ---------------------------------------------------------------------
# 01 · Typography
# ---------------------------------------------------------------------

def typography(b):
    f = board(b, "01 — Typography", W + 120, "Typography",
              "Inter for all UI. Source Serif 4 reserved for three contexts "
              "only. 13px is the default admin body size.")

    card = b.frame("type card", parent=f, fill=C["surface"], stroke=C["border"],
                   strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                   effects=S1, layout="vertical", gap=0, padding=0,
                   sizingH="fill", sizingV="hug", clip=True)

    rows = [
        ("type.display", "Display", 32, 40, "SemiBold", SERIF,
         "Empty states, sign-in panel, wizard review headline"),
        ("type.stat", "24 / 32", 24, 32, "Bold", UI, "KPI numbers only"),
        ("type.page", "Page title", 20, 28, "SemiBold", UI,
         "Screen title in the page header"),
        ("type.card", "Card title", 16, 24, "SemiBold", UI,
         "Card and panel titles"),
        ("type.ui", "Form label", 14, 20, "Medium", UI,
         "Form labels, buttons, nav items"),
        ("type.body", "Body — default", 13, 20, "Regular", UI,
         "Table primary cells, body copy, descriptions"),
        ("type.meta", "Meta", 12, 16, "Regular", UI,
         "Table secondary cells, badges, timestamps"),
        ("type.micro", "MICRO LABEL", 11, 16, "SemiBold", UI,
         "Column headers, group labels, KPI labels"),
    ]
    for i, (tok, sample, fs, lh, wt, fam, use) in enumerate(rows):
        r = b.frame(f"type row: {tok}", parent=card, height=88,
                    layout="horizontal", gap=24, crossAlign="center",
                    padding=[16, 24], fill=CLEAR,
                    sizingH="fill", sizingV="fixed",
                    stroke=C["borderSubtle"], strokeWeight=1,
                    strokeSides=sides("b"), strokeAlign="inside")
        spec = b.v("spec", parent=r, width=184, gap=4)
        b.text(tok, parent=spec, fontFamily=UI, fontSize=12,
               fontStyle="Medium", lineHeight="16px", fill=C["accent"],
               textAutoResize="widthAndHeight")
        b.text(f"{fs} / {lh}  ·  {wt}", parent=spec, fontFamily=UI,
               fontSize=12, lineHeight="16px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
        b.text(fam, parent=spec, fontFamily=UI, fontSize=12,
               lineHeight="16px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
        sample_wrap = b.v("sample", parent=r, gap=4, sizingH="fill",
                          sizingV="hug")
        s = b.text(sample, parent=sample_wrap, fontFamily=fam,
                   fontSize=fs, fontStyle=wt, lineHeight=f"{lh}px",
                   fill=C["text"], textAutoResize="widthAndHeight")
        if tok == "type.micro":
            s.props["letterSpacing"] = 0.44
            s.props["textCase"] = "upper"
        if tok == "type.page":
            s.props["letterSpacing"] = -0.4
        if tok == "type.card":
            s.props["letterSpacing"] = -0.16
        if tok == "type.stat":
            s.props["letterSpacing"] = -0.4
        b.text(use, parent=sample_wrap, fontFamily=UI, fontSize=12,
               lineHeight="16px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
    return f


# ---------------------------------------------------------------------
# 02 · Spacing, radius, elevation
# ---------------------------------------------------------------------

def geometry(b):
    f = board(b, "02 — Geometry", (W + 120) * 2, "Spacing · Radius · Elevation",
              "4px base grid. Cards never rely on shadow alone — every "
              "surface carries a border edge as well.")

    row, c = cols(b, f, 3)

    # spacing
    t_micro(b, "Spacing scale", c[0])
    for v in (4, 8, 12, 16, 20, 24, 32, 40, 48, 64):
        line = b.frame(f"space {v}", parent=c[0], layout="horizontal",
                       gap=12, crossAlign="center", fill=CLEAR)
        b.rect(parent=line, width=v, height=20, fill=C["accent"],
               cornerRadius=2)
        b.text(f"{v}", parent=line, fontFamily=UI, fontSize=12,
               lineHeight="20px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")

    # radius
    t_micro(b, "Corner radius", c[1])
    for name, val, use in (("radius.control", 4, "buttons, inputs, badges"),
                           ("radius.card", 6, "cards, panels, list rows"),
                           ("radius.overlay", 8, "modals, drawers, menus"),
                           ("radius.pill", 999, "status badges, avatars")):
        line = b.frame(f"radius {name}", parent=c[1], layout="horizontal",
                       gap=12, crossAlign="center", fill=CLEAR)
        b.rect(parent=line, width=64, height=48, fill=C["surface"],
               stroke=C["borderStrong"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=val)
        meta = b.v("radius meta", parent=line, gap=2)
        b.text(name, parent=meta, fontFamily=UI, fontSize=13,
               fontStyle="Medium", lineHeight="16px", fill=C["text"],
               textAutoResize="widthAndHeight")
        b.text(use, parent=meta, fontFamily=UI, fontSize=12,
               lineHeight="16px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")

    # elevation
    t_micro(b, "Elevation", c[2])
    for name, eff, use in (
            ("shadow.s0", None, "inset panels, table headers"),
            ("shadow.s1", S1, "cards at rest"),
            ("shadow.s2", S2, "dropdowns, popovers, tooltips"),
            ("shadow.s3", S3, "modals, drawers")):
        line = b.frame(f"elev {name}", parent=c[2], layout="horizontal",
                       gap=16, crossAlign="center", fill=CLEAR)
        props = {"width": 72, "height": 56, "fill": C["surface"],
                 "stroke": C["border"], "strokeWeight": 1,
                 "strokeAlign": "inside", "cornerRadius": 6}
        if eff:
            props["effects"] = eff
        b.frame("swatch", parent=line, **props)
        meta = b.v("elev meta", parent=line, gap=2)
        b.text(name, parent=meta, fontFamily=UI, fontSize=13,
               fontStyle="Medium", lineHeight="16px", fill=C["text"],
               textAutoResize="widthAndHeight")
        b.text(use, parent=meta, fontFamily=UI, fontSize=12,
               lineHeight="16px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
    return f


# ---------------------------------------------------------------------
# 03 · App shell
# ---------------------------------------------------------------------

def shell(b):
    f = board(b, "03 — App shell", (W + 120) * 3, "App shell",
              "One shell for both surfaces. Sidebar 248 · topbar 56 · "
              "content max 1440, page padding 32.")

    # exploded anatomy diagram
    diag = b.frame("anatomy", parent=f, layout="horizontal", gap=8,
                   sizingH="fill", sizingV="hug", crossAlign="min", fill=CLEAR)
    parts = [("sidebar", 248, 620, C["primary"]),
             ("topbar", 880, 56, C["subtle"]),
             ("page header", 880, 96, C["surface"]),
             ("content", 880, 300, C["canvas"])]
    col = b.v("bars", parent=diag, gap=8, width=248, fill=CLEAR)
    p = b.frame("sidebar bar", parent=col, width=248, height=620,
                fill=C["primary"], cornerRadius=6)
    b.text("sidebar  248", parent=col, fontFamily=UI, fontSize=12,
           fontStyle="Medium", lineHeight="20px", fill=C["textMuted"],
           textAutoResize="widthAndHeight")
    stack = b.v("right stack", parent=diag, gap=8, width=880, fill=CLEAR)
    for label, h, fillc in (("topbar  56", 56, C["subtle"]),
                            ("page header  ~96", 96, C["surface"]),
                            ("content  max 1440", 300, C["canvas"])):
        n = b.frame(f"{label} bar", parent=stack, width=880, height=h,
                    fill=fillc, stroke=C["border"], strokeWeight=1,
                    strokeAlign="inside", cornerRadius=6, layout="vertical",
                    mainAlign="center", crossAlign="center", gap=0)
        t_meta(b, label, n, C["textSec"])

    divider(b, f)

    # assembled, annotated
    frame = b.frame("assembled", parent=f, width=W, height=680,
                    layout="horizontal", fill=C["surface"], stroke=C["border"],
                    strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                    clip=True, sizingH="fill")

    side = b.frame("sidebar", parent=frame, width=248, height=680,
                   fill=C["inverse"], layout="vertical", gap=0, padding=0,
                   sizingV="fill", clip=True)
    brand = b.h("brand", parent=side, height=64, gap=10, crossAlign="center",
                padding=[0, 16], fill=C["inverse"], sizingH="fill")
    b.rect(parent=brand, width=28, height=28, fill=C["accent"], cornerRadius=6)
    b.text("CRM Platform", parent=brand, fontFamily=UI, fontSize=14,
           fontStyle="SemiBold", lineHeight="20px", fill=C["textInv"],
           textAutoResize="widthAndHeight")
    nav = b.v("nav", parent=side, gap=0, padding=[16, 12], sizingH="fill",
              sizingV="fill")
    groups = [("Platform", [("Overview", True), ("Tenants", False),
                            ("Users", False), ("Themes", False),
                            ("Sections", False)]),
              ("Operations", [("Domains", False), ("Analytics", False),
                              ("Activity", False)]),
              ("Configuration", [("Settings", False)])]
    for gname, items in groups:
        b.text(gname.upper(), parent=nav, fontFamily=UI, fontSize=11,
               fontStyle="SemiBold", lineHeight="16px", letterSpacing=0.44,
               fill="#8A9AB0", textAutoResize="widthAndHeight")
        b.frame("nav pad", parent=nav, height=8, fill=CLEAR, sizingH="fill")
        for lbl, active in items:
            item = b.h(f"nav: {lbl}", parent=nav, height=36, gap=10,
                       crossAlign="center", padding=[0, 12], fill=CLEAR,
                       sizingH="fill", cornerRadius=4)
            if active:
                item.props["fill"] = "#FFFFFF14"
            b.rect(parent=item, width=6, height=6,
                   fill=C["accent"] if active else "#FFFFFF00",
                   cornerRadius=999)
            b.text(lbl, parent=item, fontFamily=UI, fontSize=14,
                   fontStyle="Medium" if active else "Regular",
                   lineHeight="20px",
                   fill=C["textInv"] if active else "#A9B6C7",
                   textAutoResize="widthAndHeight")
        b.frame("nav pad", parent=nav, height=16, fill=CLEAR, sizingH="fill")
    foot = b.h("user chip", parent=side, height=64, gap=10,
               crossAlign="center", padding=[0, 16], fill="#0B1220",
               sizingH="fill")
    b.ell(parent=foot, width=28, height=28, fill="#3A4C63")
    col = b.v("user meta", parent=foot, gap=1)
    b.text("David Okonkwo", parent=col, fontFamily=UI, fontSize=13,
           fontStyle="Medium", lineHeight="16px", fill=C["textInv"],
           textAutoResize="widthAndHeight")
    b.text("Super admin", parent=col, fontFamily=UI, fontSize=12,
           lineHeight="16px", fill="#8A9AB0", textAutoResize="widthAndHeight")

    main = b.frame("main", parent=frame, layout="vertical", gap=0,
                   padding=0, sizingH="fill", sizingV="fill")
    top = b.h("topbar", parent=main, height=56, gap=16, crossAlign="center",
              padding=[0, 24], fill=C["surface"], sizingH="fill",
              stroke=C["border"], strokeWeight=1, strokeSides=sides("b"),
              strokeAlign="inside")
    bc = b.h("breadcrumb", parent=top, gap=8, crossAlign="center")
    for i, seg in enumerate(("Platform", "Tenants", "Grace Chapel")):
        b.text(seg, parent=bc, fontFamily=UI, fontSize=14,
               fontStyle="Regular", lineHeight="20px",
               fill=C["accent"] if i < 2 else C["text"],
               textAutoResize="widthAndHeight")
        if i < 2:
            b.text("/", parent=bc, fontFamily=UI, fontSize=14,
                   lineHeight="20px", fill=C["textMuted"],
                   textAutoResize="widthAndHeight")
    spacer = b.frame("spacer", parent=top, sizingH="fill", fill=CLEAR)
    search = b.h("global search", parent=top, width=320, height=36,
                 gap=8, crossAlign="center", padding=[0, 12], fill=C["subtle"],
                 stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=4, sizingH="fixed")
    b.text("Search", parent=search, fontFamily=UI, fontSize=14,
           lineHeight="36px", fill=C["textMuted"],
           textAutoResize="widthAndHeight")
    kbd = b.h("kbd", parent=search, gap=2, crossAlign="center", padding=[0, 6],
              fill=C["surface"], stroke=C["border"], strokeWeight=1,
              strokeAlign="inside", cornerRadius=4, height=20)
    b.text("⌘ K", parent=kbd, fontFamily=UI, fontSize=11, fontStyle="Medium",
           lineHeight="20px", fill=C["textMuted"],
           textAutoResize="widthAndHeight")
    b.ell(parent=top, width=28, height=28, fill=C["subtle"],
          stroke=C["border"], strokeWeight=1, strokeAlign="inside")

    body = b.v("body", parent=main, padding=[32, 32, 0, 32], gap=24,
               sizingH="fill", sizingV="fill", fill=C["canvas"])
    ph = b.h("page header", parent=body, gap=24, crossAlign="min",
             sizingH="fill")
    pt = b.v("page title", parent=ph, gap=4, sizingH="fill")
    t_page(b, "Tenants", pt)
    t_body(b, "Every fellowship running on the platform.", pt, C["textMuted"])
    acts = b.h("page actions", parent=ph, gap=8)
    btn(b, "Export", acts, kind="secondary")
    btn(b, "New tenant", acts, kind="primary")
    tab_row(b, body, ("Overview", "Users", "Domains", "Theme", "Pages",
                      "Activity"), active=0)
    return f


# ---------------------------------------------------------------------
# 04 · Actions and forms
# ---------------------------------------------------------------------

def actions(b):
    f = board(b, "04 — Actions & forms", (W + 120) * 4, "Actions & forms",
              "Four button variants across three sizes; six input states.")

    row, c = cols(b, f, 3)

    box, wrap = demo(b, c[0], "Primary button — sizes and states")
    for size, label_ in (("sm", "Small  32"), ("md", "Medium  36"),
                         ("lg", "Large  40")):
        line = b.h(f"size row {size}", parent=box, gap=12, height=48,
                   crossAlign="center", sizingH="fill", sizingV="fixed")
        t_meta(b, label_, line, C["textMuted"])
        b.frame("spacer", parent=line, sizingH="fill", fill=CLEAR)
        btn(b, "New tenant", line, kind="primary", size=size)
    line = b.h("state row", parent=box, gap=12, height=48,
               crossAlign="center", sizingH="fill", sizingV="fixed")
    t_meta(b, "States", line, C["textMuted"])
    b.frame("spacer", parent=line, sizingH="fill", fill=CLEAR)
    btn(b, "Disabled", line, kind="primary", opacity=0.48)
    btn(b, "Loading…", line, kind="primary")

    box, wrap = demo(b, c[1], "Variants — secondary, ghost, danger")
    for label_, kind in (("Secondary", "secondary"), ("Ghost", "ghost"),
                         ("Suspend tenant", "danger")):
        line = b.h(f"variant {kind}", parent=box, gap=12, height=48,
                   crossAlign="center", sizingH="fill", sizingV="fixed")
        t_meta(b, kind.capitalize(), line, C["textMuted"])
        b.frame("spacer", parent=line, sizingH="fill", fill=CLEAR)
        btn(b, label_, line, kind=kind)
    line = b.h("icon variants", parent=box, gap=8, height=48,
               crossAlign="center", sizingH="fill", sizingV="fixed")
    t_meta(b, "Icon", line, C["textMuted"])
    b.frame("spacer", parent=line, sizingH="fill", fill=CLEAR)
    icon_btn(b, "Edit", line, kind="secondary")
    icon_btn(b, "⋯", line, kind="secondary")
    icon_btn(b, "×", line, kind="ghost")

    box, wrap = demo(b, c[2], "Control sizing")
    for lbl in ("Button", "Input", "Select", "Badge", "Tab"):
        line = b.frame(f"metric: {lbl}", parent=box, layout="horizontal",
                       gap=16, crossAlign="center", sizingH="fill")
        b.text(lbl, parent=line, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=C["textSec"], textAutoResize="widthAndHeight",
               width=60)
        b.text({"Button": "36 px height", "Input": "36 px height",
                "Select": "36 px height", "Badge": "20 px height",
                "Tab": "40 px height"}[lbl], parent=line, fontFamily=UI,
               fontSize=13, fontStyle="Medium", lineHeight="20px",
               fill=C["text"], textAutoResize="widthAndHeight")

    row2, d = cols(b, f, 4)
    states = [("Default", "default", None),
              ("Hover", "hover", None),
              ("Focus", "focus", None),
              ("Error", "error", "That domain is already connected to "
                                 "another fellowship.")]
    for i, (name, st, note) in enumerate(states):
        field(b, name, "name@fellowship.org", d[i], state=st, note=note)
    field(b, "Disabled", "Locked by platform owner", d[0], state="disabled")
    return f


# ---------------------------------------------------------------------
# 05 · Navigation and data
# ---------------------------------------------------------------------

def data(b):
    f = board(b, "05 — Navigation & data", (W + 120) * 5,
              "Navigation & data",
              "Sidebar states, tabs, and the sortable table that carries the "
              "34-tenant list.")

    row, c = cols(b, f, 2, gap=48)

    box, wrap = demo(b, c[0], "Sidebar item states", surface=C["inverse"])
    for lbl, active in (("Overview", True), ("Tenants", False),
                        ("Domains", False), ("Activity (disabled)", False)):
        item = b.h(f"nav {lbl}", parent=box, width=248, height=36, gap=10,
                   crossAlign="center", padding=[0, 12],
                   fill="#FFFFFF14" if active else CLEAR, cornerRadius=4)
        b.rect(parent=item, width=6, height=6,
               fill=C["accent"] if active else "#FFFFFF00", cornerRadius=999)
        b.text(lbl, parent=item, fontFamily=UI, fontSize=14,
               fontStyle="Medium" if active else "Regular", lineHeight="20px",
               fill=C["textInv"] if active else "#A9B6C7",
               textAutoResize="widthAndHeight")

    box, wrap = demo(b, c[1], "Tabs and breadcrumb")
    tab_row(b, box, ("Overview", "Users", "Domains", "Theme"), active=0)
    bc = b.h("breadcrumb", parent=box, gap=8, crossAlign="center")
    for i, seg in enumerate(("Platform", "Tenants", "Grace Chapel")):
        b.text(seg, parent=bc, fontFamily=UI, fontSize=14, lineHeight="20px",
               fill=C["accent"] if i < 2 else C["text"],
               textAutoResize="widthAndHeight")
        if i < 2:
            b.text("/", parent=bc, fontFamily=UI, fontSize=14,
                   lineHeight="20px", fill=C["textMuted"],
                   textAutoResize="widthAndHeight")

    divider(b, f)

    # the reference table
    tbl = b.frame("table", parent=f, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    head = b.h("table toolbar", parent=tbl, height=64, gap=12,
               crossAlign="center", padding=[0, 20], sizingH="fill",
               stroke=C["border"], strokeWeight=1, strokeSides=sides("b"),
               strokeAlign="inside")
    search = b.h("search", parent=head, width=280, height=36, gap=8,
                 crossAlign="center", padding=[0, 12], fill=C["surface"],
                 stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=4)
    b.text("Search fellowships", parent=search, fontFamily=UI, fontSize=14,
           lineHeight="36px", fill=C["textMuted"],
           textAutoResize="widthAndHeight")
    fsel = b.h("filter", parent=head, height=36, gap=8, crossAlign="center",
               padding=[0, 12], fill=C["surface"], stroke=C["border"],
               strokeWeight=1, strokeAlign="inside", cornerRadius=4)
    b.text("Status: All", parent=fsel, fontFamily=UI, fontSize=14,
           lineHeight="36px", fill=C["text"], textAutoResize="widthAndHeight")
    b.frame("spacer", parent=head, sizingH="fill", fill=CLEAR)
    btn(b, "New tenant", head, kind="primary")

    CW = [40, 300, 116, 232, 180, 72, 72, 116]
    heads = ["", "Fellowship", "Status", "Domain", "Theme", "Pages", "Users",
             "Created"]
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", fill=C["subtle"],
                 stroke=C["border"], strokeWeight=1, strokeSides=sides("b"),
                 strokeAlign="inside")
    for name, cw in zip(heads, CW):
        cell(b, name, hr, cw, size=11, weight="SemiBold", color=C["textMuted"])
    b.frame("spacer", parent=hr, sizingH="fill", fill=CLEAR)
    cell(b, "ACTIONS", hr, 64, size=11, weight="SemiBold",
         color=C["textMuted"], align="max")

    rows = [
        ("Grace Chapel RCF", "grace-chapel", "Active", "success",
         "gracechapel.org", True, "Covenant", 6, 12, "4 Mar 2026"),
        ("Living Word Fellowship", "living-word", "Pending", "warning",
         "Not connected", False, "Covenant", 0, 5, "1 Mar 2026"),
        ("Lighthouse Chapel", "lighthouse", "Active", "success",
         "lighthouse.church", True, "Mercy", 9, 8, "22 Feb 2026"),
        ("Redeemed City Church", "redeemed-city", "Suspended", "danger",
         "redeemedcity.org", False, "Covenant", 4, 21, "9 Feb 2026"),
        ("Hope Chapel Lekki", "hope-lekki", "Active", "success",
         "hopechapellekki.org", True, "Mercy", 7, 4, "28 Jan 2026"),
    ]
    for name, slug, st, tn, dom, ver, theme, pages, users, created in rows:
        r = b.frame(f"row: {slug}", parent=tbl, height=56, gap=0,
                    crossAlign="center", padding=[0, 20], sizingH="fill",
                    fill=CLEAR, stroke=C["borderSubtle"], strokeWeight=1,
                    strokeSides=sides("b"), strokeAlign="inside")
        chk = b.h("check cell", parent=r, width=CW[0],
                  crossAlign="center", fill=CLEAR)
        b.rect(parent=chk, width=16, height=16, fill=C["surface"],
               stroke=C["borderStrong"], strokeWeight=1,
               strokeAlign="inside", cornerRadius=3)

        fc = b.h("fellowship cell", parent=r, width=CW[1], gap=10,
                 crossAlign="center", fill=CLEAR)
        b.rect(parent=fc, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        cell_stack(b, [(name, 13, "Medium", C["text"]),
                       (slug, 12, "Regular", C["textMuted"])], fc,
                   CW[1] - 42)

        sw = b.frame("status cell", parent=r, width=CW[2], fill=CLEAR,
                     layout="horizontal", crossAlign="center")
        badge(b, st, sw, t=tn, dot=True)

        dw = b.h("domain cell", parent=r, width=CW[3], gap=8,
                 crossAlign="center", fill=CLEAR)
        dot_c = (C["success"] if ver else
                 (C["warning"] if dom == "Not connected" else C["danger"]))
        b.ell(parent=dw, width=8, height=8, fill=dot_c, cornerRadius=999)
        b.text(dom, parent=dw, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=C["text"] if ver else C["textMuted"],
               textAutoResize="widthAndHeight")

        cell(b, theme, r, CW[4], color=C["textSec"])
        cell(b, str(pages), r, CW[5], color=C["textSec"])
        cell(b, str(users), r, CW[6], color=C["textSec"])
        cell(b, created, r, CW[7], color=C["textMuted"])
        b.frame("spacer", parent=r, sizingH="fill", fill=CLEAR)
        cell(b, "⋯", r, 64, size=16, color=C["textMuted"], align="max")

    foot = b.h("pagination", parent=tbl, height=56, gap=12,
               crossAlign="center", padding=[0, 20], sizingH="fill")
    b.text("Showing 1–5 of 34", parent=foot, fontFamily=UI, fontSize=13,
           lineHeight="20px", fill=C["textMuted"],
           textAutoResize="widthAndHeight")
    b.frame("spacer", parent=foot, sizingH="fill", fill=CLEAR)
    for lbl in ("‹", "1", "2", "›"):
        is_num = lbl.isdigit()
        b.text(lbl, parent=foot, fontFamily=UI, fontSize=13,
               fontStyle="Medium" if is_num else "Regular",
               lineHeight="20px",
               fill=C["accent"] if is_num else C["textSec"],
               textAutoResize="widthAndHeight")
    return f


# ---------------------------------------------------------------------
# 06 · Feedback and overlays
# ---------------------------------------------------------------------

def feedback(b):
    f = board(b, "06 — Feedback & overlays", (W + 120) * 6,
              "Feedback & overlays",
              "Toasts, banners, empty states, modals, drawers, menus, "
              "tooltips and confirm dialogs.")

    row, c = cols(b, f, 3)

    box, wrap = demo(b, c[0], "Banner — four tones")
    for tone_name, title, body in (
            ("info", "Certificate issued",
             "A TLS certificate was provisioned for gracechapel.org."),
            ("success", "Tenant published",
             "6 pages are live on liveword.church."),
            ("warning", "Domain not verified",
             "DNS records have not propagated after 24 hours."),
            ("danger", "Publish failed",
             "The theme manifest references a missing section.")):
        bn = b.frame(f"banner {tone_name}", parent=box, layout="vertical",
                     gap=4, padding=[12, 16], sizingH="fill",
                     cornerRadius=6, fill=tone(tone_name)[0],
                     stroke=tone(tone_name)[1], strokeWeight=1,
                     strokeAlign="inside")
        b.text(title, parent=bn, fontFamily=UI, fontSize=13,
               fontStyle="SemiBold", lineHeight="20px", fill=tone(tone_name)[2],
               textAutoResize="widthAndHeight")
        b.text(body, parent=bn, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=tone(tone_name)[2], textAutoResize="widthAndHeight")

    box, wrap = demo(b, c[1], "Empty state")
    es = b.frame("empty", parent=box, fill=CLEAR, sizingH="fill",
                 sizingV="hug", layout="horizontal",
                 mainAlign="center", crossAlign="center", padding=[32, 24])
    ecol = b.v("empty column", parent=es, gap=12, width=300,
               crossAlign="center", fill=CLEAR)
    b.ell(parent=ecol, width=48, height=48, fill=C["subtle"],
          stroke=C["border"], strokeWeight=1, strokeAlign="inside",
          cornerRadius=999)
    t_display(b, "No themes yet", ecol, C["text"], w=300)
    t_body(b, "Publish your first theme to the shared library so "
              "fellowships can install it.", ecol, C["textMuted"],
              wrap=300, align="center")
    btn(b, "Upload a theme", ecol, kind="primary")

    box, wrap = demo(b, c[2], "Toast, tooltip, menu")
    tw = b.h("toast", parent=box, gap=12, crossAlign="center", padding=16,
             sizingH="fill", cornerRadius=8, fill=C["inverse"], effects=S2,
             clip=True)
    b.ell(parent=tw, width=8, height=8, fill="#6CE9A6", cornerRadius=999)
    tc = b.v("toast text", parent=tw, gap=2, sizingH="fill")
    b.text("Tenant suspended", parent=tc, fontFamily=UI, fontSize=13,
           fontStyle="Medium", lineHeight="20px", fill=C["textInv"],
           textAutoResize="widthAndHeight")
    b.text("Redeemed City Church cannot publish.", parent=tc, fontFamily=UI,
           fontSize=12, lineHeight="16px", fill="#A9B6C7",
           textAutoResize="widthAndHeight")

    tt = b.h("tooltip", parent=box, height=28, gap=8, crossAlign="center",
             padding=[0, 12], fill=C["inverse"], cornerRadius=8,
             sizingH="hug", effects=S2)
    b.text("Verification TXT record", parent=tt, fontFamily=UI, fontSize=11,
           lineHeight="28px", fill=C["textInv"], textAutoResize="widthAndHeight")

    menu = b.v("menu", parent=box, width=200, padding=[4, 0],
               cornerRadius=8, fill=C["surface"], stroke=C["border"],
               strokeWeight=1, strokeAlign="inside", effects=S2, gap=0)
    for lbl, tn in (("View site", None), ("Edit details", None),
                    ("Re-issue certificate", None),
                    ("Suspend tenant", "danger")):
        mi = b.h(f"menu: {lbl}", parent=menu, height=32, padding=[0, 12],
                 crossAlign="center", fill=CLEAR, sizingH="fill")
        b.text(lbl, parent=mi, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=C["danger"] if tn else C["text"],
               textAutoResize="widthAndHeight")

    divider(b, f)

    # modal + drawer + confirm
    strip = b.frame("overlay strip", parent=f, layout="horizontal", gap=32,
                    sizingH="fill", sizingV="hug", crossAlign="min", fill=CLEAR)

    md = b.frame("modal 640", parent=strip, width=480, layout="vertical",
                 gap=0, cornerRadius=8, fill=C["surface"], stroke=C["border"],
                 strokeWeight=1, strokeAlign="inside", effects=S3, clip=True)
    mh = b.v("modal header", parent=md, gap=4, padding=[24, 24, 16, 24],
             sizingH="fill")
    t_card(b, "Suspend this tenant?", mh)
    t_body(b, "Redeemed City Church will lose access immediately. "
              "Published pages stay online but can no longer be edited.",
           mh, C["textMuted"], wrap=432)
    b.frame("modal body", parent=md, height=1, fill=C["borderSubtle"],
            sizingH="fill")
    mf = b.h("modal footer", parent=md, height=68, gap=8, padding=[0, 24],
             crossAlign="center", sizingH="fill")
    b.frame("spacer", parent=mf, sizingH="fill", fill=CLEAR)
    btn(b, "Cancel", mf, kind="secondary")
    btn(b, "Suspend tenant", mf, kind="danger")

    dw_ = b.frame("drawer 480", parent=strip, width=360, height=420,
                  layout="vertical", gap=0, padding=0, cornerRadius=8,
                  fill=C["surface"], stroke=C["border"], strokeWeight=1,
                  strokeAlign="inside", effects=S3, clip=True,
                  sizingV="fixed")
    dh = b.h("drawer header", parent=dw_, height=64, gap=12,
             crossAlign="center", padding=[0, 24], sizingH="fill",
             stroke=C["border"], strokeWeight=1, strokeSides=sides("b"),
             strokeAlign="inside")
    t_card(b, "Theme details", dh)
    b.frame("spacer", parent=dh, sizingH="fill", fill=CLEAR)
    b.text("×", parent=dh, fontFamily=UI, fontSize=18, lineHeight="24px",
           fill=C["textMuted"], textAutoResize="widthAndHeight")
    dl = b.v("drawer body", parent=dw_, gap=16, padding=[24, 24],
             sizingH="fill", sizingV="fill")
    prev = b.frame("drawer preview", parent=dl, width=312, height=180,
                   fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                   strokeAlign="inside", cornerRadius=6,
                   layout="horizontal", mainAlign="center",
                   crossAlign="center", sizingH="fixed")
    t_meta(b, "Theme preview", prev, C["textMuted"])
    for k, v in (("Name", "Covenant"), ("Author", "CRM Platform"),
                 ("Installed by", "12 fellowships"),
                 ("Published", "12 Feb 2026")):
        kv = b.h(f"kv {k}", parent=dl, sizingH="fill", gap=16)
        b.text(k, parent=kv, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=C["textMuted"], textAutoResize="widthAndHeight",
               width=140)
        b.text(v, parent=kv, fontFamily=UI, fontSize=13,
               fontStyle="Medium", lineHeight="20px", fill=C["text"],
               textAutoResize="widthAndHeight")
    return f


# ---------------------------------------------------------------------
# 07 · Display
# ---------------------------------------------------------------------

def display(b):
    f = board(b, "07 — Display", (W + 120) * 7, "Display components",
              "KPI tiles, list rows, activity timeline, key-value lists and "
              "progress — the vocabulary of the dashboard.")

    row, c = cols(b, f, 4)
    for lbl, val, delta, tn in (("Total tenants", "34", "+3", "success"),
                                ("Active", "31", "+2", "success"),
                                ("Domains connected", "27", "−4", "danger"),
                                ("Page views · 30d", "184k", "+18%", "success")):
        kpi(b, lbl, val, delta, tn, c[0], w="fill")

    box, wrap = demo(b, c[1], "Content card")
    cd = b.frame("card", parent=box, **card_props())
    cd.props.update({"layout": "vertical", "gap": 16, "padding": 24,
                     "sizingH": "fill", "sizingV": "hug"})
    ch = b.h("card header", parent=cd, gap=12, crossAlign="center",
             sizingH="fill")
    t_card(b, "Needs attention", ch)
    b.frame("spacer", parent=ch, sizingH="fill", fill=CLEAR)
    btn(b, "View all", ch, kind="secondary", size="sm")
    for t, s in (("living-word", "Domain not verified"),
                 ("redeemed-city", "Tenant suspended"),
                 ("hope-lekki", "No pages published")):
        lr = b.h(f"list row {t}", parent=cd, height=56, gap=12,
                 crossAlign="center", sizingH="fill", cornerRadius=4,
                 fill=CLEAR)
        b.rect(parent=lr, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        lc = b.v("row meta", parent=lr, gap=1, sizingH="fill")
        b.text(t, parent=lc, fontFamily=UI, fontSize=13, fontStyle="Medium",
               lineHeight="16px", fill=C["text"], textAutoResize="widthAndHeight")
        b.text(s, parent=lc, fontFamily=UI, fontSize=12, lineHeight="16px",
               fill=C["textMuted"], textAutoResize="widthAndHeight")
        b.text("›", parent=lr, fontFamily=UI, fontSize=16, lineHeight="20px",
               fill=C["textMuted"], textAutoResize="widthAndHeight")

    box, wrap = demo(b, c[2], "Activity timeline")
    tl = b.v("timeline", parent=box, gap=0, sizingH="fill")
    for actor, act, when, tn in (
            ("David Okonkwo", "suspended Redeemed City Church", "12 min ago",
             "danger"),
            ("Ada Nwosu", "published 4 pages for Lighthouse Chapel",
             "1 hr ago", "success"),
            ("System", "issued TLS certificate for hopechapellekki.org",
             "3 hrs ago", "info")):
        item = b.h(f"tl {actor}", parent=tl, gap=12, crossAlign="min",
                   sizingH="fill", padding=[0, 0, 16, 0])
        b.ell(parent=item, width=8, height=8, fill=tone(tn)[2],
          cornerRadius=999)
        tc = b.v("tl meta", parent=item, gap=2, sizingH="fill")
        line = b.h("tl line", parent=tc, gap=4, crossAlign="center",
                   sizingH="fill")
        b.text(actor, parent=line, fontFamily=UI, fontSize=13,
               fontStyle="SemiBold", lineHeight="20px", fill=C["text"],
               textAutoResize="widthAndHeight")
        b.text(when, parent=line, fontFamily=UI, fontSize=12,
               lineHeight="20px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
        t_body(b, act, tc, C["textSec"], wrap=360)

    box, wrap = demo(b, c[3], "Key-value list and progress")
    kvl = b.v("kv list", parent=box, gap=12, sizingH="fill")
    for k, v in (("Slug", "living-word"), ("Custom domain", "—"),
                 ("Theme", "Covenant"), ("Created", "1 Mar 2026")):
        kv = b.h(f"kv {k}", parent=kvl, sizingH="fill", gap=16)
        b.text(k, parent=kv, fontFamily=UI, fontSize=13, lineHeight="20px",
               fill=C["textMuted"], textAutoResize="widthAndHeight",
               width=140)
        b.text(v, parent=kv, fontFamily=UI, fontSize=13, fontStyle="Medium",
               lineHeight="20px", fill=C["text"], textAutoResize="widthAndHeight")
    pv = b.v("progress meta", parent=box, gap=8, sizingH="fill")
    pl = b.h("progress labels", parent=pv, sizingH="fill")
    t_meta(b, "Pages published", pl, C["text"])
    b.frame("spacer", parent=pl, sizingH="fill", fill=CLEAR)
    t_meta(b, "6 of 12", pl, C["textMuted"])
    tr = b.h("track", parent=pv, height=6, fill=C["subtle"],
             cornerRadius=999)
    tr.props["sizingH"] = "fill"
    b.rect(parent=tr, width=136, height=6, fill=C["accent"],
           cornerRadius=999)
    return f


BOARDS = [colour, typography, geometry, shell, actions, data, feedback,
          display]


def main():
    page = reset("Foundations")
    b = B()
    for fn in BOARDS:
        fn(b)
    send(b, label="foundations")
    call("save_file", {})
    print(f"page {page}: {len(b.nodes)} nodes across {len(BOARDS)} boards")


if __name__ == "__main__":
    main()