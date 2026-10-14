"""Shared app chrome — sidebar, topbar, page header.

Every Super-Admin screen is `screen(...)` plus body content, so the shell
cannot drift between screens: there is exactly one implementation.

    python3 design/screens.py [group]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import (B, C, UI, CLEAR, S1, S2, sides, btn, icon_btn, badge,
                      field, divider, cell, cell_stack, tab_row, tone,
                      spacer, check, t_micro, t_meta, t_body, t_ui, t_card,
                      t_page, t_stat,
                      t_display, send, call, batch_text)
from _reset import reset

SIDEBAR = 248
TOPBAR = 56
PAD = 32
BODY_W = 1440 - SIDEBAR - PAD * 2      # 1128
SCREEN_H = 1024

NAIL = "#8A9AB0"
NAIL_DIM = "#A9B6C7"

NAV = [
    ("Platform", [("Overview", "overview"), ("Tenants", "tenants"),
                  ("Users", "users"), ("Themes", "themes"),
                  ("Sections", "sections")]),
    ("Operations", [("Domains", "domains"), ("Analytics", "analytics"),
                    ("Activity", "activity")]),
    ("Configuration", [("Settings", "settings")]),
]


def sidebar(b, parent, active, brand="CRM Platform", user="David Okonkwo",
            role="Super admin", back=None):
    side = b.frame("sidebar", parent=parent, width=SIDEBAR, height=SCREEN_H,
                   fill=C["inverse"], layout="vertical", gap=0, padding=0,
                   sizingV="fill", clip=True)

    brandrow = b.h("brand", parent=side, height=64, gap=10,
                   crossAlign="center", padding=[0, 16], fill=C["inverse"],
                   sizingH="fill", sizingV="fixed")
    b.rect(parent=brandrow, width=28, height=28, fill=C["accent"],
           cornerRadius=6)
    btext = b.v("brand meta", parent=brandrow, gap=0, sizingH="fill")
    b.text(brand, parent=btext, fontFamily=UI, fontSize=14,
           fontStyle="SemiBold", lineHeight="20px", fill=C["textInv"],
           textAutoResize="widthAndHeight")

    nav = b.v("nav", parent=side, gap=0, padding=[16, 12], sizingH="fill",
              sizingV="fill")
    for gname, items in NAV:
        t_micro(b, gname, nav, NAIL)
        b.frame("nav gap", parent=nav, height=8, fill=CLEAR, sizingH="fill")
        for lbl, key in items:
            on = key == active
            item = b.h(f"nav: {lbl}", parent=nav, height=36, gap=10,
                       crossAlign="center", padding=[0, 12], fill=CLEAR,
                       sizingH="fill", sizingV="fixed", cornerRadius=4)
            if on:
                item.props["fill"] = "#FFFFFF14"
            b.rect(parent=item, width=6, height=6,
                   fill=C["accent"] if on else "#FFFFFF00", cornerRadius=999)
            b.text(lbl, parent=item, fontFamily=UI, fontSize=14,
                   fontStyle="Medium" if on else "Regular", lineHeight="20px",
                   fill=C["textInv"] if on else NAIL_DIM,
                   textAutoResize="widthAndHeight")
        b.frame("nav gap", parent=nav, height=16, fill=CLEAR, sizingH="fill")

    foot = b.h("user chip", parent=side, height=64, gap=10,
               crossAlign="center", padding=[0, 16], fill="#0B1220",
               sizingH="fill", sizingV="fixed")
    b.ell(parent=foot, width=28, height=28, fill="#3A4C63")
    col = b.v("user meta", parent=foot, gap=1, sizingH="fill")
    t_body(b, user, col, C["textInv"], "Medium")
    t_meta(b, role, col, NAIL)
    return side


def topbar(b, parent, crumbs, search=True):
    top = b.h("topbar", parent=parent, height=TOPBAR, gap=16,
              crossAlign="center", padding=[0, 24], fill=C["surface"],
              sizingH="fill", sizingV="fixed", stroke=C["border"],
              strokeWeight=1, strokeSides=sides("b"), strokeAlign="inside")
    bc = b.h("breadcrumb", parent=top, gap=8, crossAlign="center",
             sizingH="fill")
    for i, seg in enumerate(crumbs):
        t_ui(b, seg, bc, C["accent"] if i < len(crumbs) - 1 else C["text"])
        if i < len(crumbs) - 1:
            t_ui(b, "/", bc, C["textMuted"])
    if search:
        s = b.h("global search", parent=top, width=320, height=36, gap=8,
                crossAlign="center", padding=[0, 12], fill=C["subtle"],
                stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                cornerRadius=4, sizingH="fixed", sizingV="fixed")
        t_ui(b, "Search", s, C["textMuted"])
        kbd = b.h("kbd", parent=s, height=20, gap=2, crossAlign="center",
                  padding=[0, 6], fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=4)
        t_micro(b, "⌘ K", kbd, C["textMuted"])
        b.ell(parent=top, width=28, height=28, fill=C["subtle"],
              stroke=C["border"], strokeWeight=1, strokeAlign="inside",
              sizingH="fixed", sizingV="fixed")
    return top


def page_header(b, parent, title, subtitle=None, actions=None):
    ph = b.h("page header", parent=parent, gap=24, crossAlign="min",
             sizingH="fill", sizingV="hug", padding=[0, 0, 8, 0])
    col = b.v("page title", parent=ph, gap=4, sizingH="fill")
    t_page(b, title, col)
    if subtitle:
        t_body(b, subtitle, col, C["textMuted"], wrap=BODY_W - 360)
    if actions:
        acts = b.h("page actions", parent=ph, gap=8, crossAlign="min")
        for a in actions:
            if isinstance(a, tuple):
                btn(b, a[0], acts, kind=a[1], size="sm")
            else:
                btn(b, a, acts, kind="primary")
    return ph


def screen(b, x, name, active, crumbs, title=None, subtitle=None,
           actions=None, tabs=None, brand="CRM Platform", height=SCREEN_H,
           user="David Okonkwo", role="Super admin"):
    """Build a full screen frame; returns (root, body_content_node)."""
    root = b.root_of(b.frame(name, x=x, y=0, width=1440, height=height,
                             fill=C["canvas"], layout="horizontal", gap=0,
                             padding=0, sizingH="fixed", sizingV="fixed",
                             clip=True))
    sidebar(b, root, active, brand=brand, user=user, role=role)
    main = b.frame("main", parent=root, layout="vertical", gap=0, padding=0,
                   sizingH="fill", sizingV="fill")
    topbar(b, main, crumbs)
    body = b.v("body", parent=main, gap=24, padding=[PAD, PAD, PAD, PAD],
               sizingH="fill", sizingV="fill", fill=C["canvas"])
    if title:
        page_header(b, body, title, subtitle, actions)
    if tabs:
        tab_row(b, body, tabs, active=0)
    return root, body


def toolbar(b, parent, search_ph="Search", filters=(), primary=None,
            height=64):
    """Table toolbar: search, filters, spacer, primary action."""
    t = b.h("toolbar", parent=parent, height=height, gap=12,
            crossAlign="center", padding=[0, 20], sizingH="fill",
            sizingV="fixed", fill=C["surface"])
    s = b.h("search", parent=t, width=280, height=36, gap=8,
            crossAlign="center", padding=[0, 12], fill=C["surface"],
            stroke=C["border"], strokeWeight=1, strokeAlign="inside",
            cornerRadius=4, sizingH="fixed", sizingV="fixed")
    t_ui(b, search_ph, s, C["textMuted"])
    for f in filters:
        fl = b.h(f"filter: {f}", parent=t, height=36, gap=8,
                 crossAlign="center", padding=[0, 12], fill=C["surface"],
                 stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=4, sizingH="hug", sizingV="fixed")
        t_ui(b, f, fl, C["text"])
        t_meta(b, "⌄", fl, C["textMuted"])
    spacer(b, t)
    if primary:
        btn(b, primary, t, kind="primary")
    return t


def table(b, parent, widths, heads, rows, row_h=56, checkbox=True,
          actions_head="ACTIONS"):
    """A data table frame. `rows` renders its own body cells."""
    tbl = b.frame("table", parent=parent, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", sizingV="fixed",
                 fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                 strokeSides=sides("b"), strokeAlign="inside")
    for name, w in zip(heads, widths):
        if checkbox and name == "":
            cell(b, "", hr, w)
        else:
            cell(b, name, hr, w, size=11, weight="SemiBold",
                 color=C["textMuted"])
    spacer(b, hr)
    if actions_head:
        cell(b, actions_head, hr, 64, size=11, weight="SemiBold",
             color=C["textMuted"], align="right")
    for render in rows:
        render(b, tbl, widths)
    return tbl


def row_shell(b, tbl, widths, height=56, fill=None, selected=False):
    r = b.frame("row", parent=tbl, height=height, gap=0, crossAlign="center",
                padding=[0, 20], sizingH="fill", sizingV="fixed",
                fill=fill or C["surface"], stroke=C["borderSubtle"],
                strokeWeight=1, strokeSides=sides("b"), strokeAlign="inside")
    if selected:
        r.props["fill"] = "#EFF4FF"
    spacer(b, r)
    return r


def check_cell(b, parent, w=40, checked=False):
    chk = b.h("check cell", parent=parent, width=w, crossAlign="center",
              fill=CLEAR, sizingH="fixed", sizingV="hug")
    b.rect(parent=chk, width=16, height=16,
           fill=C["accent"] if checked else C["surface"],
           stroke=C["borderStrong"], strokeWeight=1, strokeAlign="inside",
           cornerRadius=3)
    if checked:
        check(b, chk, C["textInv"], size=11, weight=2)
    return chk


def pagination(b, tbl, shown, total, pages=("‹", "1", "2", "›")):
    f = b.h("pagination", parent=tbl, height=56, gap=12, crossAlign="center",
            padding=[0, 20], sizingH="fill", sizingV="fixed")
    t_body(b, shown, f, C["textMuted"])
    spacer(b, f)
    for p in pages:
        is_num = p.isdigit()
        t_body(b, p, f, C["accent"] if is_num else C["textSec"],
              "Medium" if is_num else "Regular")
    return f


def content_card(b, parent, title=None, actions=None, gap=16, pad=24,
                 fill=None):
    cd = b.frame("card", parent=parent, fill=fill or C["surface"],
                 stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=6, effects=S1, layout="vertical", gap=gap,
                 padding=pad, sizingH="fill", sizingV="hug", clip=True)
    if title:
        ch = b.h("card header", parent=cd, gap=12, crossAlign="center",
                 sizingH="fill", sizingV="hug")
        t_card(b, title, ch)
        spacer(b, ch)
        for a in (actions or []):
            btn(b, a, ch, kind="secondary", size="sm")
    return cd


def card_grid(b, parent, n, gap=24, min_w=300):
    """A wrapping grid of n equal columns."""
    row = b.frame("grid", parent=parent, gap=gap, crossAlign="min",
                  sizingH="fill", sizingV="hug", fill=CLEAR)
    return [b.frame(f"grid col {i + 1}", parent=row, layout="vertical",
                    gap=gap, sizingH="fill", sizingV="hug", fill=CLEAR)
            for i in range(n)]


def stat_row(b, parent, tiles, gap=24):
    """tiles: [(label, value, delta, tone)]"""
    row = b.frame("stat row", parent=parent, gap=gap, crossAlign="min",
                  sizingH="fill", sizingV="hug", fill=CLEAR)
    w = (BODY_W - gap * (len(tiles) - 1)) // len(tiles)
    out = []
    for lbl, val, delta, tn in tiles:
        cd = b.frame(f"kpi: {lbl}", parent=row, width=w, layout="vertical",
                     gap=12, padding=20, fill=C["surface"], stroke=C["border"],
                     strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                     effects=S1, sizingH="fixed", sizingV="hug", clip=True)
        t_micro(b, lbl, cd)
        vrow = b.h("kpi value", parent=cd, gap=8, crossAlign="center",
                   sizingH="fill")
        t_stat(b, val, vrow)
        if delta:
            badge(b, delta, vrow, t=tn, dot=False)
        out.append(cd)
    return out


def axis_row(b, parent, labels, size=12, color=None):
    """Evenly distributed chart axis labels.

    Fixed-width cells clip anything wider than the cell, so each label gets a
    fill-width slot and centres inside it.
    """
    row = b.h("axis", parent=parent, gap=8, sizingH="fill", sizingV="hug")
    for lbl in labels:
        f = b.frame("axis slot", parent=row, layout="horizontal",
                    mainAlign="center", crossAlign="center", fill=CLEAR,
                    sizingH="fill", sizingV="hug")
        t_meta(b, lbl, f, color or C["textMuted"])
    return row


def status_dot(b, parent, tone_name, r=8):
    b.ell(parent=parent, width=r, height=r, fill=tone(tone_name)[2],
          cornerRadius=999)