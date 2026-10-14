"""Super-Admin screens.

Frames live on the "Super-Admin" page, 1440x1024 each.

    python3 design/screens.py 1        # sign in, dashboard, tenants
    python3 design/screens.py all
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import (B, C, UI, SERIF, CLEAR, S1, S2, sides, btn, icon_btn,
                      badge, field, divider, cell, cell_stack, tab_row, tone,
                      spacer, t_micro, t_meta, t_body, t_ui, t_card, t_page, t_stat,
                      t_display, send, call, batch_text)
from _reset import reset
from chrome import (SCREEN_H, BODY_W, PAD, SIDEBAR, sidebar, topbar,
                    page_header, screen, toolbar, table, row_shell, check_cell,
                    pagination, content_card, card_grid, stat_row, status_dot)

STEP = 1560


# =====================================================================
# 01 · Sign in
# =====================================================================

def sign_in(b):
    root = b.root_of(b.frame("01 — Sign in", x=0, y=0, width=1440,
                             height=SCREEN_H, fill=C["surface"],
                             layout="horizontal", gap=0, padding=0,
                             clip=True))

    # brand panel
    panel = b.frame("brand panel", parent=root, width=560, height=SCREEN_H,
                    fill=C["primary"], layout="vertical", gap=0, padding=0,
                    sizingV="fill", clip=True)
    inner = b.v("panel content", parent=panel, gap=0, padding=[48, 56],
                sizingH="fill", sizingV="fill")
    lock = b.h("lockup", parent=inner, gap=10, crossAlign="center")
    b.rect(parent=lock, width=32, height=32, fill=C["accent"],
           cornerRadius=8)
    t_ui(b, "CRM Platform", lock, C["textInv"], "SemiBold")

    b.frame("spacer", parent=inner, sizingV="fill", fill=CLEAR)
    mid = b.v("panel copy", parent=inner, gap=0, sizingH="fill")
    head = t_display(b, "Every fellowship,\none platform.", mid, C["textInv"],
                     w=460)
    head.props.update({"textAlign": "left", "lineHeight": "46px"})
    gap = b.frame("panel gap", parent=mid, height=20, fill=CLEAR,
                  sizingH="fill", sizingV="fixed")
    lead = t_body(b, "Provision ministries, issue certificates and publish "
                     "sites — from a single console.",
                  mid, "#A9C0D8", wrap=420)
    lead.props["lineHeight"] = "24px"
    b.frame("panel gap", parent=inner, height=36, fill=CLEAR,
            sizingH="fill", sizingV="fixed")

    bullets = b.v("trust list", parent=inner, gap=14, sizingH="fill")
    for txt in ("34 fellowships provisioned and isolated",
                "Automatic TLS for every custom domain",
                "Shared theme and section library"):
        bl = b.h(f"bullet {txt[:12]}", parent=bullets, gap=12,
                 crossAlign="min", sizingH="fill")
        ic = b.frame("bullet icon", parent=bl, width=20, height=20,
                     fill="#FFFFFF14", cornerRadius=999, stroke="#FFFFFF26",
                     strokeWeight=1, strokeAlign="inside",
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", sizingH="fixed", sizingV="fixed")
        b.text("\u2713", parent=ic, fontFamily=UI, fontSize=11,
               lineHeight="20px", fill="#8FB8E8",
               textAutoResize="widthAndHeight")
        t_body(b, txt, bl, "#C4D3E2", wrap=380)
    b.frame("spacer", parent=inner, sizingV="fill", fill=CLEAR)
    t_meta(b, "© 2026 Christ Redeemer Ministry", inner, "#7E96AF")

    # form side
    form_side = b.frame("form side", parent=root, fill=C["subtle"],
                        layout="horizontal", mainAlign="center",
                        crossAlign="center", gap=0, padding=0,
                        sizingH="fill", sizingV="fill")
    cardf = b.v("sign in card", parent=form_side, gap=16, padding=[36, 36],
                width=416, fill=C["surface"], stroke=C["border"],
                strokeWeight=1, strokeAlign="inside", cornerRadius=8,
                effects=S1, sizingH="fixed", sizingV="hug", clip=True)
    t_card(b, "Sign in", cardf)
    t_body(b, "Use your platform administrator account.", cardf,
           C["textMuted"], wrap=344)
    warn = b.v("alert", parent=cardf, gap=4, padding=[12, 16],
               sizingH="fill", fill=C["dangerBg"], stroke=C["dangerBd"],
               strokeWeight=1, strokeAlign="inside", cornerRadius=6)
    t_body(b, "Incorrect email or password.", warn, C["danger"], "Medium")
    t_body(b, "Two attempts remain before lockout.", warn, C["danger"],
           wrap=304)

    field(b, "Email address", "name@christredeemer.org", cardf, w=344,
          state="error")
    field(b, "Password", "••••••••••••", cardf, w=344, trailing="Show")

    row = b.h("form row", parent=cardf, gap=12, crossAlign="center",
              sizingH="fill")
    chk = b.h("remember", parent=row, gap=8, crossAlign="center")
    b.rect(parent=chk, width=16, height=16, fill=C["surface"],
           stroke=C["borderStrong"], strokeWeight=1, strokeAlign="inside",
           cornerRadius=3)
    t_body(b, "Keep me signed in", chk, C["textSec"])
    spacer(b, row)
    t_body(b, "Forgot password?", row, C["accent"], "Medium")

    btn(b, "Sign in", cardf, kind="primary", size="lg", full=True)

    divider(b, cardf, color=C["border"])
    t_meta(b, "OR CONTINUE WITH", cardf, C["textMuted"])
    sso = b.h("sso", parent=cardf, gap=10, crossAlign="center",
              sizingH="fill")
    btn(b, "Continue with Google", sso, kind="secondary")
    t_meta(b, "SSO placeholder — not wired in Phase 1.", cardf,
           C["textMuted"], wrap=344)
    return root


# =====================================================================
# 02 · Dashboard
# =====================================================================

def dashboard(b):
    root, body = screen(b, STEP, "02 — Dashboard", "overview",
                        ["Platform", "Overview"], "Overview",
                        "Platform health across every fellowship.",
                        tabs=["Overview", "Tenants", "Users"])

    stat_row(b, body, [
        ("Total tenants", "34", "+3 this month", "success"),
        ("Active", "31", "91%", "success"),
        ("Domains connected", "27", "−4", "danger"),
        ("Page views · 30d", "184k", "+18%", "success"),
    ])

    half = (BODY_W - 24) // 2
    mid = b.frame("mid row", parent=body, gap=24, crossAlign="min",
                  sizingH="fill", sizingV="hug", fill=CLEAR)
    left = b.v("left column", parent=mid, gap=24, width=half, fill=CLEAR,
               sizingH="fixed", sizingV="hug")
    right = b.v("right column", parent=mid, gap=24, sizingH="fill",
                sizingV="hug", fill=CLEAR)

    # ---- tenants by status (proportion bar, not a donut) -------------
    c1 = content_card(b, left, "Tenants by status")
    seg = b.h("proportion bar", parent=c1, height=12, cornerRadius=999,
              sizingH="fill", sizingV="fixed", clip=True)
    seg_w = half - 48
    for tn, n in (("success", 31), ("warning", 3), ("danger", 4)):
        b.rect(parent=seg, width=max(8, round(seg_w * n / 38)), height=12,
               fill=tone(tn)[2], cornerRadius=999, sizingH="fixed",
               sizingV="fixed")
    legend = b.v("legend", parent=c1, gap=12, sizingH="fill")
    for lbl, n, tn in (("Active", "31  ·  91%", "success"),
                       ("Pending setup", "3  ·  8%", "warning"),
                       ("Suspended", "4  ·  1%", "danger")):
        lg = b.h(f"legend {lbl}", parent=legend, gap=10, crossAlign="center",
                 sizingH="fill", sizingV="hug")
        status_dot(b, lg, tn)
        t_body(b, lbl, lg, C["textSec"])
        spacer(b, lg)
        t_body(b, n, lg, C["text"], "Medium")

    # ---- new tenants trend -------------------------------------------
    c2 = content_card(b, left, "New tenants", actions=["Last 90 days"])
    chart = b.h("chart", parent=c2, height=168, crossAlign="max", gap=14,
                sizingH="fill", sizingV="fixed", fill=CLEAR)
    for i, hh in enumerate((40, 56, 44, 72, 60, 80, 64, 96, 74, 104, 86,
                            112)):
        b.rect(parent=chart, width=20, height=hh, fill=C["accent"],
               cornerRadius=[3, 3, 0, 0] if i == 11 else 3)
    axis = b.h("axis", parent=c2, gap=14, sizingH="fill", sizingV="hug")
    for lbl in ("Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"):
        cell(b, lbl, axis, 20, size=12, color=C["textMuted"])
        spacer(b, axis)

    # ---- needs attention ---------------------------------------------
    c3 = content_card(b, right, "Needs attention", actions=["View all"])
    for slug, issue, tn in (("living-word", "Domain not verified", "warning"),
                            ("redeemed-city", "Tenant suspended", "danger"),
                            ("hope-lekki", "No pages published", "neutral")):
        lr = b.h(f"attn {slug}", parent=c3, height=56, gap=12,
                 crossAlign="center", sizingH="fill", sizingV="fixed",
                 cornerRadius=4)
        b.rect(parent=lr, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        col = b.v("attn meta", parent=lr, gap=1, sizingH="fill")
        t_body(b, slug, col, C["text"], "Medium")
        t_meta(b, issue, col, C["textMuted"])
        spacer(b, lr)
        badge(b, "Resolve", lr, t=tn)
        t_ui(b, "\u203a", lr, C["textMuted"])

    # ---- recent activity ---------------------------------------------
    c4 = content_card(b, right, "Recent activity", actions=["Open log"])
    tl = b.v("timeline", parent=c4, gap=16, sizingH="fill")
    for actor, act, when, tn in (
            ("David Okonkwo", "suspended Redeemed City Church", "12 min ago",
             "danger"),
            ("Ada Nwosu", "published 4 pages for Lighthouse Chapel",
             "1 hr ago", "success"),
            ("System", "issued a TLS certificate for hopechapellekki.org",
             "3 hrs ago", "info"),
            ("Bola Adeyemi", "provisioned Living Word Fellowship",
             "yesterday", "neutral")):
        item = b.h(f"tl {actor}", parent=tl, gap=12, crossAlign="min",
                   sizingH="fill", sizingV="hug")
        b.ell(parent=item, width=8, height=8, fill=tone(tn)[2],
              cornerRadius=999)
        col = b.v("tl meta", parent=item, gap=2, sizingH="fill")
        line = b.h("tl line", parent=col, gap=6, crossAlign="center",
                   sizingH="fill", sizingV="hug")
        t_body(b, actor, line, C["text"], "Medium")
        t_meta(b, when, line, C["textMuted"])
        t_body(b, act, col, C["textSec"], wrap=half - 44)

    return root


# =====================================================================
# 03 · Tenants
# =====================================================================

TENANTS = [
    ("Grace Chapel RCF", "grace-chapel", "Active", "success",
     "gracechapel.org", "verified", "Covenant", 6, 12, "4 Mar 2026"),
    ("Living Word Fellowship", "living-word", "Pending", "warning",
     "—", "none", "Covenant", 0, 5, "1 Mar 2026"),
    ("Lighthouse Chapel", "lighthouse", "Active", "success",
     "lighthouse.church", "verified", "Mercy", 9, 8, "22 Feb 2026"),
    ("Redeemed City Church", "redeemed-city", "Suspended", "danger",
     "redeemedcity.org", "failed", "Covenant", 4, 21, "9 Feb 2026"),
    ("Hope Chapel Lekki", "hope-lekki", "Active", "success",
     "hopechapellekki.org", "verified", "Mercy", 7, 4, "28 Jan 2026"),
    ("Faith Assembly Yaba", "faith-assembly", "Active", "success",
     "faithassemblyyaba.org", "verified", "Covenant", 3, 6, "19 Jan 2026"),
    ("Cornerstone Bible Church", "cornerstone-bible", "Active", "success",
     "cornerstonebible.org", "verified", "Mercy", 5, 9, "12 Jan 2026"),
    ("Grace Hill Assembly", "grace-hill", "Pending", "warning",
     "—", "none", "Covenant", 0, 3, "6 Jan 2026"),
    ("Solace Chapel Ikorodu", "solace-ikorodu", "Active", "success",
     "solacechapel.org", "verified", "Mercy", 8, 7, "2 Jan 2026"),
    ("Zion Worship Centre", "zion-worship", "Suspended", "danger",
     "zionworshipcentre.org", "failed", "Covenant", 2, 11, "18 Dec 2025"),
]

# 1128 content - 40 row padding - 64 actions column = 1024 for the fields
CW = [40, 272, 112, 208, 144, 56, 56, 104]


def tenants(b):
    root, body = screen(b, STEP * 2, "03 — Tenants", "tenants",
                        ["Platform", "Tenants"], "Tenants",
                        "Every fellowship running on the platform.")

    toolbar(b, body, "Search fellowships",
            filters=["Status: All", "Theme: All"], primary="New tenant")

    tbl = b.frame("table", parent=body, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    heads = ["", "Fellowship", "Status", "Domain", "Theme", "Pages", "Users",
             "Created"]
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", sizingV="fixed",
                 fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                 strokeSides=sides("b"), strokeAlign="inside")
    for name, w in zip(heads, CW):
        cell(b, name, hr, w, size=11, weight="SemiBold", color=C["textMuted"])
    spacer(b, hr)
    cell(b, "ACTIONS", hr, 64, size=11, weight="SemiBold",
         color=C["textMuted"], align="right")

    for i, (name, slug, st, tn, dom, ver, theme, pages, users,
            created) in enumerate(TENANTS):
        r = row_shell(b, tbl, CW, fill=C["surface"])
        check_cell(b, r, CW[0])
        fc = b.h("fellowship cell", parent=r, width=CW[1], gap=10,
                 crossAlign="center", fill=CLEAR, sizingH="fixed",
                 sizingV="hug")
        b.rect(parent=fc, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        cell_stack(b, [(name, 13, "Medium", C["text"]),
                       (slug, 12, "Regular", C["textMuted"])], fc,
                   CW[1] - 42)
        sw = b.frame("status cell", parent=r, width=CW[2], fill=CLEAR,
                     layout="horizontal", crossAlign="center", sizingH="fixed",
                     sizingV="hug")
        badge(b, st, sw, t=tn, dot=True)
        dw = b.h("domain cell", parent=r, width=CW[3], gap=8,
                 crossAlign="center", fill=CLEAR, sizingH="fixed",
                 sizingV="hug")
        status_dot(b, dw, {"verified": "success", "none": "warning",
                           "failed": "danger"}[ver], r=8)
        dom_label = dom if dom != "—" else "Not connected"
        t_body(b, dom_label, dw, C["text"] if ver == "verified"
               else C["textMuted"], wrap=CW[3] - 20)
        cell(b, theme, r, CW[4], color=C["textSec"])
        cell(b, str(pages), r, CW[5], color=C["textSec"])
        cell(b, str(users), r, CW[6], color=C["textSec"])
        cell(b, created, r, CW[7], color=C["textMuted"])
        cell(b, "⋯", r, 64, size=16, color=C["textMuted"], align="right")

    pagination(b, tbl, "Showing 1–10 of 34",
               34, pages=("‹", "1", "2", "3", "4", "…", "6", "›"))
    return root


# =====================================================================
# 04 · Tenant detail
# =====================================================================

def tenant_detail(b):
    root, body = screen(b, STEP * 3, "04 — Tenant detail", "tenants",
                        ["Platform", "Tenants", "Grace Chapel RCF"])

    # entity header
    hdr = b.frame("entity header", parent=body, gap=16, crossAlign="min",
                  sizingH="fill", sizingV="hug")
    av = b.frame("avatar", parent=hdr, width=56, height=56, fill=C["subtle"],
                 stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=12, layout="horizontal", mainAlign="center",
                 crossAlign="center", sizingH="fixed", sizingV="fixed")
    b.text("GC", parent=av, fontFamily=UI, fontSize=20,
           fontStyle="SemiBold", lineHeight="56px", fill=C["textSec"],
           textAutoResize="widthAndHeight")
    col = b.v("entity meta", parent=hdr, gap=6, sizingH="fill")
    trow = b.h("entity title", parent=col, gap=12, crossAlign="center",
               sizingH="fill", sizingV="hug")
    t_page(b, "Grace Chapel RCF", trow)
    badge(b, "Active", trow, t="success", dot=True)
    t_body(b, "grace-chapel  ·  created 4 Mar 2026 by David Okonkwo",
           col, C["textMuted"])
    spacer(b, hdr)
    acts = b.h("entity actions", parent=hdr, gap=8, crossAlign="min",
               sizingH="hug")
    btn(b, "Suspend", acts, kind="secondary")
    btn(b, "Edit details", acts, kind="secondary")
    btn(b, "Open site", acts, kind="primary")

    tab_row(b, body, ["Overview", "Users", "Domains", "Theme", "Pages",
                      "Activity"], active=0)

    stat_row(b, body, [
        ("Pages published", "6", "2 drafts", "neutral"),
        ("Users", "12", "3 editors", "neutral"),
        ("Page views · 30d", "27k", "+6%", "success"),
        ("Storage used", "184 MB", "of 2 GB", "neutral"),
    ])

    half = (BODY_W - 24) // 2
    mid = b.frame("mid row", parent=body, gap=24, crossAlign="min",
                  sizingH="fill", sizingV="hug", fill=CLEAR)
    left = b.v("left column", parent=mid, gap=24, width=half, fill=CLEAR,
               sizingH="fixed", sizingV="hug")
    right = b.v("right column", parent=mid, gap=24, sizingH="fill",
                sizingV="hug", fill=CLEAR)

    # identity
    c1 = content_card(b, left, "Identity", actions=["Edit"])
    for k, v in (("Legal name", "Grace Chapel Redeemed Fellowship"),
                 ("Slug", "grace-chapel"),
                 ("Region", "South West, Nigeria"),
                 ("Created", "4 March 2026"),
                 ("Provisioned by", "David Okonkwo")):
        kv = b.h(f"kv {k}", parent=c1, gap=16, sizingH="fill", sizingV="hug")
        cell(b, k, kv, 160, color=C["textMuted"])
        cell(b, v, kv, half - 48 - 160)

    # domain + DNS
    c2 = content_card(b, left, "Domain", actions=["Open DNS settings"])
    dns = b.v("dns records", parent=c2, gap=8, sizingH="fill")
    for kind, name, target in (("CNAME", "www", "cname.platform.church"),
                               ("A", "gracechapel.org", "203.0.113.24")):
        rec = b.h(f"dns {name}", parent=dns, height=44, gap=12,
                  crossAlign="center", sizingH="fill", sizingV="fixed",
                  padding=[0, 12], fill=C["subtle"],
                  stroke=C["borderSubtle"], strokeWeight=1,
                  strokeAlign="inside", cornerRadius=6)
        b.text(kind, parent=rec, fontFamily=UI, fontSize=12,
               fontStyle="SemiBold", lineHeight="20px", fill=C["textMuted"],
               textAutoResize="widthAndHeight")
        cell(b, name, rec, 120, weight="Medium")
        cell(b, target, rec, 208, color=C["textSec"])
        badge(b, "Verified", rec, t="success", dot=True)
    t_meta(b, "Certificate issued 4 Mar 2026 · expires 4 Jun 2026", c2,
           C["textMuted"])

    # theme
    c3 = content_card(b, right, "Theme", actions=["Change"])
    prev = b.frame("theme preview", parent=c3, height=180, fill=C["subtle"],
                   stroke=C["border"], strokeWeight=1, strokeAlign="inside",
                   cornerRadius=6, layout="horizontal", mainAlign="center",
                   crossAlign="center", sizingH="fill", sizingV="fixed")
    t_meta(b, "Covenant — theme preview", prev, C["textMuted"])
    row = b.h("theme meta", parent=c3, gap=12, crossAlign="center",
              sizingH="fill", sizingV="hug")
    colt = b.v("theme text", parent=row, gap=2, sizingH="fill")
    t_body(b, "Covenant", colt, C["text"], "Medium")
    t_meta(b, "By CRM Platform · installed 4 Mar 2026", colt,
           C["textMuted"])
    spacer(b, row)
    badge(b, "Published", row, t="info")

    # team
    c4 = content_card(b, right, "Team", actions=["Manage users"])
    for name, email, role, tn in (
            ("Ada Nwosu", "ada@gracechapel.org", "Tenant admin", "info"),
            ("Chinedu Okafor", "chinedu@gracechapel.org", "Editor",
             "neutral"),
            ("Bola Adeyemi", "bola@gracechapel.org", "Editor", "neutral")):
        lr = b.h(f"member {email}", parent=c4, height=52, gap=12,
                 crossAlign="center", sizingH="fill", sizingV="hug")
        b.ell(parent=lr, width=32, height=32, fill=C["subtle"],
              stroke=C["border"], strokeWeight=1, strokeAlign="inside")
        mc = b.v("member meta", parent=lr, gap=1, sizingH="fill")
        t_body(b, name, mc, C["text"], "Medium")
        t_meta(b, email, mc, C["textMuted"])
        spacer(b, lr)
        badge(b, role, lr, t=tn)
    more = b.h("more members", parent=c4, gap=8, crossAlign="center",
               sizingH="fill", sizingV="hug")
    t_body(b, "+9 more members", more, C["accent"], "Medium")
    return root


# =====================================================================
# 06 · Users
# =====================================================================

USERS = [
    ("David Okonkwo", "david@christredeemer.org", "Super admin",
     "Platform", "2 min ago", "Active", "success"),
    ("Ada Nwosu", "ada@gracechapel.org", "Tenant admin",
     "Grace Chapel RCF", "18 min ago", "Active", "success"),
    ("Bola Adeyemi", "bola@christredeemer.org", "Tenant admin",
     "Redeemed City Church", "1 hr ago", "Active", "success"),
    ("Chinedu Okafor", "chinedu@gracechapel.org", "Editor",
     "Grace Chapel RCF", "3 hrs ago", "Active", "success"),
    ("Ngozi Eze", "ngozi@livingword.org", "Tenant admin",
     "Living Word Fellowship", "2 days ago", "Active", "success"),
    ("Emeka Obi", "emeka@lighthouse.church", "Editor",
     "Lighthouse Chapel", "4 days ago", "Active", "success"),
    ("Tunde Bakare", "tunde@zionworship.org", "Editor",
     "Zion Worship Centre", "12 days ago", "Suspended", "danger"),
    ("Fatima Yusuf", "fatima@hopechapel.org", "Editor",
     "Hope Chapel Lekki", "20 days ago", "Active", "success"),
    ("Ibrahim Sanni", "ibrahim@solace.org", "Tenant admin",
     "Solace Chapel Ikorodu", "24 days ago", "Active", "success"),
    ("Grace Mbeki", "grace@cornerstone.org", "Editor",
     "Cornerstone Bible Church", "31 days ago", "Suspended", "danger"),
]

UW = [40, 320, 148, 208, 124, 132]


def users(b):
    root, body = screen(b, STEP * 5, "06 — Users", "users",
                        ["Platform", "Users"], "Users",
                        "Every account that can sign in to the platform.",
                        actions=[("Export", "secondary")])

    toolbar(b, body, "Search by name or email",
            filters=["Role: All", "Status: All"], primary="Invite user")

    tbl = b.frame("table", parent=body, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    heads = ["", "User", "Platform role", "Primary tenant", "Last active",
             "Status"]
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", sizingV="fixed",
                 fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                 strokeSides=sides("b"), strokeAlign="inside")
    for name, w in zip(heads, UW):
        cell(b, name, hr, w, size=11, weight="SemiBold", color=C["textMuted"])
    spacer(b, hr)
    cell(b, "ACTIONS", hr, 64, size=11, weight="SemiBold",
         color=C["textMuted"], align="right")

    for name, email, role, tenant, last, st, tn in USERS:
        r = row_shell(b, tbl, UW)
        check_cell(b, r, UW[0])
        uc = b.h("user cell", parent=r, width=UW[1], gap=10,
                 crossAlign="center", fill=CLEAR, sizingH="fixed",
                 sizingV="hug")
        initials = "".join(p[0] for p in name.split()[:2])
        av = b.frame("avatar", parent=uc, width=32, height=32,
                     fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                     strokeAlign="inside", cornerRadius=999,
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", sizingH="fixed", sizingV="fixed")
        it = b.text(initials, parent=av, fontFamily=UI, fontSize=12,
                    fontStyle="SemiBold", lineHeight="32px",
                    fill=C["textSec"], textAutoResize="widthAndHeight")
        cell_stack(b, [(name, 13, "Medium", C["text"]),
                       (email, 12, "Regular", C["textMuted"])], uc,
                   UW[1] - 42)
        rw = b.frame("role cell", parent=r, width=UW[2], fill=CLEAR,
                     layout="horizontal", crossAlign="center", sizingH="fixed",
                     sizingV="hug")
        badge(b, role, rw, t="info" if role == "Super admin" else "neutral")
        cell(b, tenant, r, UW[3], color=C["textSec"], wrap=UW[3] - 16)
        cell(b, last, r, UW[4], color=C["textMuted"])
        sw = b.frame("status cell", parent=r, width=UW[5], fill=CLEAR,
                     layout="horizontal", crossAlign="center", sizingH="fixed",
                     sizingV="hug")
        badge(b, st, sw, t=tn, dot=True)
        cell(b, "\u22ef", r, 64, size=16, color=C["textMuted"],
             align="right")

    pagination(b, tbl, "Showing 1–10 of 212",
               212, pages=("\u2039", "1", "2", "3", "\u2026", "27", "\u203a"))
    return root


GROUPS = {
    1: [("sign_in", 0), ("dashboard", 1), ("tenants", 2)],
}


def build(names, page_name="Super-Admin"):
    reset("Foundations")
    pages = json.loads(call("run_command",
                            {"command": "page.list"})[0][0])
    call("run_command", {"command": "page.add",
                         "params": {"name": page_name}})
    pages = json.loads(call("run_command",
                            {"command": "page.list"})[0][0])
    pid = next(p["id"] for p in pages if p["name"] == page_name)

    idx = 0
    for fn_name, _ in names:
        call("run_command", {"command": "page.select", "params": {"id": str(pid)}})
        b = B()
        globals()[fn_name](b)
        send(b, label=fn_name)
        call("save_file", {})
        print(f"  {fn_name}: {len(b.nodes)} nodes")
        idx += 1


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    sel = list(GROUPS.values())[0] if which == "1" else None
    if sel is None:
        print("unknown group", which)
        sys.exit(1)
    build(sel)