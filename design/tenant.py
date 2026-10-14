"""Tenant (RCF) admin screens.

Same shell, same tokens, same components as the Super-Admin surface. The only
genuinely new things here are the publishing flow and the asset manager.

    python3 design/build.py          # builds Foundations + Super-Admin + Tenant
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figbuild import (B, C, UI, SERIF, CLEAR, S1, S2, S3, sides, btn,
                      icon_btn, badge, field, divider, cell, cell_stack,
                      tab_row, tone, check, spacer, t_micro, t_meta, t_body,
                      t_ui, t_card, t_page, t_stat, t_display, send, call,
                      batch_text)
from chrome import (SCREEN_H, BODY_W, PAD, SIDEBAR, TENANT_NAV, screen,
                    toolbar, table, row_shell, check_cell, pagination,
                    content_card, card_grid, stat_row, status_dot, axis_row)

STEP = 1560

BRAND = "Grace Chapel RCF"
MONO = "GC"
USER = "Ada Nwosu"
ROLE = "Tenant admin"

TENANT = dict(brand=BRAND, monogram=MONO, user=USER, role=ROLE,
              nav=TENANT_NAV, back="Back to platform")


# =====================================================================
# 01 · Sign in
# =====================================================================

def t_sign_in(b):
    """Fellowship sign-in.

    Same component as the Super-Admin sign-in, branded for the tenant. It is
    one component with a branding prop, not a second component - which is why
    the platform copy ("Every fellowship, one platform") does not appear here.
    """
    root = b.root_of(b.frame("01 — Sign in", x=0, y=0, width=1440,
                             height=SCREEN_H, fill=C["surface"],
                             layout="horizontal", gap=0, padding=0,
                             sizingH="fixed", sizingV="fixed", clip=True))

    # ---- fellowship panel -------------------------------------------
    panel = b.frame("fellowship panel", parent=root, width=560,
                    height=SCREEN_H, fill=C["primary"], layout="vertical",
                    gap=0, padding=0, sizingH="fixed", sizingV="fill",
                    clip=True)
    inner = b.v("panel content", parent=panel, gap=0, padding=[48, 56],
                sizingH="fill", sizingV="fill")
    lock = b.h("lockup", parent=inner, gap=10, crossAlign="center")
    mark = b.frame("monogram", parent=lock, width=32, height=32,
                   fill=C["accent"], cornerRadius=8, layout="horizontal",
                   mainAlign="center", crossAlign="center",
                   sizingH="fixed", sizingV="fixed")
    t_meta(b, MONO, mark, C["textInv"], weight="SemiBold")
    b.text(BRAND, parent=lock, fontFamily=UI, fontSize=15,
           fontStyle="SemiBold", lineHeight="20px", fill=C["textInv"],
           textAutoResize="widthAndHeight")

    b.frame("panel spacer", parent=inner, sizingV="fill", fill=CLEAR)
    mid = b.v("panel copy", parent=inner, gap=0, sizingH="fill")
    head = t_display(b, "Welcome back,\nGrace Chapel.", mid, C["textInv"],
                     w=460)
    head.props.update({"textAlign": "left", "lineHeight": "46px"})
    b.frame("panel gap", parent=mid, height=20, fill=CLEAR, sizingH="fill",
            sizingV="fixed")
    t_body(b, "Sign in to edit your pages, publish changes and manage your "
              "team.", mid, "#A9C0D8", wrap=420)
    b.frame("panel gap", parent=inner, height=36, fill=CLEAR,
            sizingH="fill", sizingV="fixed")

    # live status, so they can see the site's state at the door
    live = b.frame("live strip", parent=inner, gap=10, crossAlign="center",
                   padding=[10, 14], sizingH="hug", fill="#FFFFFF14",
                   cornerRadius=6)
    b.ell(parent=live, width=8, height=8, fill="#6CE9A6", cornerRadius=999)
    t_meta(b, "6 pages live on gracechapel.org", live, "#C4D3E2")

    b.frame("panel gap", parent=inner, height=36, fill=CLEAR,
            sizingH="fill", sizingV="fixed")

    caps = b.v("capability list", parent=inner, gap=14, sizingH="fill")
    for txt in ("Edit and publish pages without touching a developer",
                "Invite editors and manage their access",
                "Upload images, logos and documents"):
        bl = b.h(f"cap {txt[:12]}", parent=caps, gap=12, crossAlign="min",
                 sizingH="fill", sizingV="hug")
        ic = b.frame("cap icon", parent=bl, width=20, height=20,
                     fill="#FFFFFF14", cornerRadius=999, stroke="#FFFFFF26",
                     strokeWeight=1, strokeAlign="inside",
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", sizingH="fixed", sizingV="fixed")
        check(b, ic, "#8FB8E8", size=12, weight=2)
        t_body(b, txt, bl, "#C4D3E2", wrap=380)
    b.frame("panel spacer", parent=inner, sizingV="fill", fill=CLEAR)
    t_meta(b, "© 2026 Grace Chapel RCF", inner, "#7E96AF")

    # ---- form side ---------------------------------------------------
    form_side = b.frame("form side", parent=root, fill=C["subtle"],
                        layout="horizontal", mainAlign="center",
                        crossAlign="center", gap=0, padding=0,
                        sizingH="fill", sizingV="fill")
    cardf = b.v("sign in card", parent=form_side, width=416, gap=16,
                padding=[36, 36], fill=C["surface"], stroke=C["border"],
                strokeWeight=1, strokeAlign="inside", cornerRadius=8,
                effects=S1, sizingH="fixed", sizingV="hug", clip=True)
    t_card(b, "Sign in", cardf)
    t_body(b, "Use the email address your fellowship administrator "
              "invited.", cardf, C["textMuted"], wrap=344)

    warn = b.v("alert", parent=cardf, gap=4, padding=[12, 16],
               sizingH="fill", fill=C["dangerBg"], stroke=C["dangerBd"],
               strokeWeight=1, strokeAlign="inside", cornerRadius=6)
    t_body(b, "Incorrect email or password.", warn, C["danger"], "Medium")
    t_body(b, "Two attempts remain before lockout.", warn, C["danger"],
           wrap=304)

    field(b, "Email address", "ada@gracechapel.org", cardf, w=344,
          state="error")
    field(b, "Password", "••••••••••••", cardf, w=344, trailing="Show")

    row = b.h("form row", parent=cardf, gap=12, crossAlign="center",
              sizingH="fill", sizingV="hug")
    chk = b.h("remember", parent=row, gap=8, crossAlign="center",
              sizingH="hug", sizingV="hug")
    b.rect(parent=chk, width=16, height=16, fill=C["surface"],
           stroke=C["borderStrong"], strokeWeight=1, strokeAlign="inside",
           cornerRadius=3)
    t_body(b, "Keep me signed in", chk, C["textSec"])
    spacer(b, row)
    t_body(b, "Forgot password?", row, C["accent"], "Medium")

    btn(b, "Sign in", cardf, kind="primary", size="lg", full=True)

    divider(b, cardf, color=C["border"])
    t_micro(b, "Need an account?", cardf)
    t_body(b, "Only a fellowship administrator can invite new members. Ask "
              "them to send an invite to this address.", cardf, C["textSec"],
           wrap=344)
    btn(b, "Contact administrator", cardf, kind="secondary", full=True)
    return root


# =====================================================================
# 02 · Dashboard
# =====================================================================

def t_dashboard(b):
    root, body = screen(b, STEP, "02 — Dashboard", "overview",
                        ["Grace Chapel RCF", "Dashboard"], "Dashboard",
                        "Your site, and what needs doing to it.",
                        **TENANT)

    # publishing state lives here — a tenant's primary question is whether
    # their last change is live
    pub = b.frame("publish bar", parent=body,gap=12,
                  crossAlign="center", padding=[14, 20], fill="#ECFDF3",
                  stroke=C["successBd"], strokeWeight=1, strokeAlign="inside",
                  cornerRadius=6, sizingH="fill", sizingV="fixed")
    b.ell(parent=pub, width=8, height=8, fill=C["success"], cornerRadius=999)
    pubc = b.v("publish text", parent=pub, gap=2, sizingH="fill")
    t_body(b, "Everything is published", pubc, C["success"], "Medium")
    t_meta(b, "6 pages live on gracechapel.org · last published 2 hours ago",
           pubc, C["success"])
    spacer(b, pub)
    btn(b, "View site", pub, kind="secondary", size="sm")

    stat_row(b, body, [
        ("Pages", "6 live", "2 drafts", "neutral"),
        ("Page views · 30d", "27,115", "+6%", "success"),
        ("Team members", "12", "3 editors", "neutral"),
        ("Storage used", "184 MB", "of 2 GB", "neutral"),
    ])

    half = (BODY_W - 24) // 2
    mid = b.frame("mid row", parent=body,gap=24,
                  crossAlign="min", sizingH="fill", sizingV="hug", fill=CLEAR)
    left = b.v("left", parent=mid, gap=24, width=half, fill=CLEAR,
               sizingH="fixed", sizingV="hug")
    right = b.v("right", parent=mid, gap=24, sizingH="fill", sizingV="hug",
                fill=CLEAR)

    c1 = content_card(b, left, "Recent pages", actions=["All pages"])
    for title, status, stn, edited in (
            ("Home", "Published", "success", "Ada · 2 hrs ago"),
            ("Our Story", "Draft changes", "warning", "Chinedu · 5 hrs"),
            ("Sermons", "Published", "success", "Ada · 1 day ago"),
            ("Contact", "Published", "success", "Ada · 3 days ago"),):
        lr = b.h(f"page {title}", parent=c1, height=56, gap=12,
                 crossAlign="center", sizingH="fill", sizingV="fixed")
        b.rect(parent=lr, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        col = b.v("page meta", parent=lr, gap=1, sizingH="fill")
        t_body(b, title, col, C["text"], "Medium")
        t_meta(b, f"Edited {edited}", col, C["textMuted"])
        spacer(b, lr)
        badge(b, status, lr, t=stn, dot=True)
        t_ui(b, "›", lr, C["textMuted"])

    c2 = content_card(b, left, "Page views · 30 days", gap=12)
    chart = b.h("chart", parent=c2, height=88, crossAlign="max", gap=8,
                sizingH="fill", sizingV="fixed", fill=CLEAR)
    for hh in (38, 52, 44, 66, 58, 72, 64, 84, 70, 90, 76, 96, 82, 88):
        b.rect(parent=chart, width=20, height=hh, fill=C["accent"],
               cornerRadius=[3, 3, 0, 0])
    axis_row(b, c2, ("15 Feb", "22 Feb", "1 Mar", "8 Mar", "15 Mar"))

    c3 = content_card(b, right, "Setup checklist", actions=[])
    for task, done, note in (
            ("Connect a custom domain", True, "gracechapel.org"),
            ("Install a theme", True, "Covenant"),
            ("Publish your first page", True, "6 pages live"),
            ("Invite your team", True, "12 members"),
            ("Add a giving page", False, "Recommended")):
        lr = b.h(f"task {task}", parent=c3, height=44, gap=12,
                 crossAlign="center", sizingH="fill", sizingV="fixed")
        bx_props = {"width": 20, "height": 20, "cornerRadius": 5,
                    "layout": "horizontal", "mainAlign": "center",
                    "crossAlign": "center", "sizingH": "fixed",
                    "sizingV": "fixed"}
        if done:
            bx_props["fill"] = C["accent"]
        else:
            bx_props["fill"] = C["surface"]
            bx_props["stroke"] = C["borderStrong"]
            bx_props["strokeWeight"] = 1
            bx_props["strokeAlign"] = "inside"
        bx = b.frame("task box", parent=lr, **bx_props)
        if done:
            check(b, bx, C["textInv"], size=12, weight=2)
        col = b.v("task meta", parent=lr, gap=1, sizingH="fill")
        t_body(b, task, col, C["text"] if done else C["textSec"], "Medium")
        t_meta(b, note, col, C["textMuted"])
        spacer(b, lr)
        if not done:
            btn(b, "Set up", lr, kind="secondary", size="sm")

    c4 = content_card(b, right, "Team activity", gap=12)
    tl = b.v("timeline", parent=c4, gap=12, sizingH="fill")
    for who, act, when in (
            ("Ada Nwosu", "published Home", "2 hrs ago"),
            ("Chinedu Okafor", "edited Our Story", "5 hrs ago")):
        it = b.h(f"tl {who}", parent=tl, gap=12, crossAlign="min",
                 sizingH="fill", sizingV="hug")
        b.ell(parent=it, width=8, height=8, fill=C["accent"],
              cornerRadius=999)
        col = b.v("tl meta", parent=it, gap=2, sizingH="fill")
        line = b.h("tl line", parent=col, gap=6, crossAlign="center",
                   sizingH="fill", sizingV="hug")
        t_body(b, who, line, C["text"], "Medium")
        t_meta(b, when, line, C["textMuted"])
        t_body(b, act, col, C["textSec"], wrap=half - 40)
    return root


# =====================================================================
# 02 · Pages
# =====================================================================

PAGES = [
    ("Home", "/", "Published", "success", "Ada Nwosu", "2 hrs ago", "Yes"),
    ("Our Story", "/about", "Draft changes", "warning", "Chinedu Okafor",
     "5 hrs ago", "No"),
    ("Sermons", "/sermons", "Published", "success", "Ada Nwosu",
     "yesterday", "Yes"),
    ("Leadership", "/leadership", "Published", "success", "Ada Nwosu",
     "2 days ago", "Yes"),
    ("Events", "/events", "Published", "success", "Chinedu Okafor",
     "4 days ago", "Yes"),
    ("Contact", "/contact", "Published", "success", "Ada Nwosu",
     "1 week ago", "Yes"),
    ("Giving", "/giving", "Draft", "neutral", "Ada Nwosu", "2 weeks ago",
     "No"),
    ("Children's Ministry", "/children", "Published", "success",
     "Chinedu Okafor", "3 weeks ago", "Yes"),
]

PW = [312, 160, 152, 176, 136, 88]


def t_pages(b):
    root, body = screen(b, STEP * 2, "03 — Pages", "pages",
                        ["Grace Chapel RCF", "Pages"], "Pages",
                        "Every page on your site. Edits autosave; publishing "
                        "is yours to trigger.",
                        actions=[("New page", "primary")], **TENANT)

    toolbar(b, body, "Search pages", filters=["Status: All"])

    tbl = b.frame("table", parent=body, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    heads = ["Page", "Status", "Last edited by", "Last edited", "Homepage",
             "Actions"]
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", sizingV="fixed",
                 fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                 strokeSides=sides("b"), strokeAlign="inside")
    for name, w in zip(heads, PW):
        cell(b, name, hr, w, size=11, weight="SemiBold", color=C["textMuted"])
    spacer(b, hr)
    cell(b, "", hr, 64)

    for i, (title, slug, status, stn, who, when, home) in enumerate(PAGES):
        r = row_shell(b, tbl, PW, fill="#FFFDF5" if stn == "warning"
                      else C["surface"])
        pc = b.h("page cell", parent=r, width=PW[0], gap=10,
                 crossAlign="center", fill=CLEAR, sizingH="fixed",
                 sizingV="hug")
        b.rect(parent=pc, width=32, height=32, fill=C["subtle"],
               stroke=C["border"], strokeWeight=1, strokeAlign="inside",
               cornerRadius=6)
        cell_stack(b, [(title, 13, "Medium", C["text"]),
                       (slug, 12, "Regular", C["textMuted"])], pc,
                   PW[0] - 42)
        sw = b.frame("status cell", parent=r, width=PW[1], fill=CLEAR,
                     layout="horizontal", crossAlign="center",
                     sizingH="fixed", sizingV="hug")
        badge(b, status, sw, t=stn, dot=True)
        cell(b, who, r, PW[2], color=C["textSec"])
        cell(b, when, r, PW[3], color=C["textMuted"])
        hw = b.frame("home cell", parent=r, width=PW[4], fill=CLEAR,
                     layout="horizontal", crossAlign="center",
                     sizingH="fixed", sizingV="hug")
        if home == "Yes":
            check(b, hw, C["success"], size=13)
        else:
            t_body(b, "—", hw, C["textMuted"])
        spacer(b, r)
        ar = b.h("row actions", parent=r, gap=8, crossAlign="center",
                 sizingH="hug", sizingV="hug")
        if stn == "warning":
            btn(b, "Publish", ar, kind="primary", size="sm")
        else:
            btn(b, "Edit", ar, kind="secondary", size="sm")
        t_ui(b, "⋯", ar, C["textMuted"])
    pagination(b, tbl, "Showing 1–8 of 8", 8, pages=("‹", "1", "›"))
    return root


# =====================================================================
# 03 · Theme
# =====================================================================

INSTALLABLE = [
    ("Mercy", "CRM Platform", "Warm, editorial, strong on scripture", True),
    ("Covenant", "CRM Platform", "Currently installed", False),
    ("Anchor", "CRM Platform", "Plain and fast, minimal imagery", True),
    ("Harvest", "Living Word Fellowship", "Built for event-heavy weeks", True),
]


def t_theme(b):
    root, body = screen(b, STEP * 3, "04 — Theme", "theme",
                        ["Grace Chapel RCF", "Theme"], "Theme",
                        "Your installed theme, and what else is available.",
                        **TENANT)

    cur = content_card(b, body, "Installed theme")
    prow = b.frame("installed row", parent=cur,gap=20,
                   crossAlign="min", sizingH="fill", sizingV="hug",
                   fill=CLEAR)
    prev = b.frame("installed preview", parent=prow, width=280, height=160,
                   fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                   strokeAlign="inside", cornerRadius=6,
                   layout="horizontal", mainAlign="center",
                   crossAlign="center", sizingH="fixed", sizingV="fixed")
    t_meta(b, "Covenant — preview", prev, C["textMuted"])
    meta = b.v("installed meta", parent=prow, gap=10, sizingH="fill",
               sizingV="hug")
    line = b.h("installed title", parent=meta, gap=10, crossAlign="center",
               sizingH="fill", sizingV="hug")
    t_card(b, "Covenant", line)
    spacer(b, line)
    badge(b, "Published", line, t="info", dot=True)
    t_body(b, "By CRM Platform · installed 4 March 2026", meta, C["textMuted"])
    t_body(b, "Switching themes keeps your pages and content. Layout and "
              "styling come from the theme; your text and images stay yours.",
           meta, C["textSec"], wrap=560)
    spacer(b, meta)
    acts = b.h("installed actions", parent=meta, gap=8, crossAlign="center",
               sizingH="fill", sizingV="hug")
    btn(b, "Customise in editor", acts, kind="primary")
    btn(b, "Change theme", acts, kind="secondary")

    b.frame("section gap", parent=body, height=8, fill=CLEAR, sizingH="fill",
            sizingV="fixed")
    t_micro(b, "Available to install", body)

    grid = b.frame("install grid", parent=body,gap=24,
                   crossAlign="min", sizingH="fill", sizingV="hug",
                   fill=CLEAR)
    for name, author, blurb, avail in INSTALLABLE:
        cd = b.frame(f"theme {name}", parent=grid, layout="vertical", gap=0,
                     padding=0, width=(BODY_W - 3 * 24) // 4,
                     sizingH="fixed", sizingV="hug", fill=C["surface"],
                     stroke=C["border"], strokeWeight=1,
                     strokeAlign="inside", cornerRadius=6, effects=S1,
                     clip=True)
        pv = b.frame("preview", parent=cd, height=140, fill=C["subtle"],
                     stroke=C["borderSubtle"], strokeWeight=1,
                     strokeAlign="inside", cornerRadius=[6, 6, 0, 0],
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", sizingH="fill", sizingV="fixed")
        t_meta(b, name + " — preview", pv, C["textMuted"])
        meta2 = b.v("meta", parent=cd, gap=6, padding=16, sizingH="fill",
                    sizingV="hug")
        t_card(b, name, meta2)
        t_meta(b, f"by {author}", meta2, C["textMuted"])
        t_body(b, blurb, meta2, C["textSec"], wrap=220)
        b.frame("meta gap", parent=meta2, height=4, fill=CLEAR,
                sizingH="fill", sizingV="fixed")
        b.frame("meta gap", parent=meta2, height=4, fill=CLEAR,
                sizingH="fill", sizingV="fixed")
        if avail:
            btn(b, "Install", meta2, kind="secondary", size="sm")
        else:
            badge(b, "Installed", meta2, t="success", dot=True)
    return root


# =====================================================================
# 04 · Assets
# =====================================================================

ASSETS = [
    ("hero-home.jpg", "2.1 MB", "1,200 × 800", "14 Feb"),
    ("logo-primary.svg", "12 KB", "Vector", "4 Mar"),
    ("our-story-01.jpg", "1.4 MB", "1,600 × 1,067", "2 Mar"),
    ("pastor-portrait.jpg", "890 KB", "800 × 1,000", "28 Feb"),
    ("sermon-series.jpg", "1.8 MB", "1,600 × 900", "19 Feb"),
    ("og-default.png", "180 KB", "1,200 × 630", "4 Mar"),
    ("community-01.jpg", "1.1 MB", "1,600 × 1,067", "11 Feb"),
]


def t_assets(b):
    root, body = screen(b, STEP * 4, "05 — Assets", "assets",
                        ["Grace Chapel RCF", "Assets"], "Assets",
                        "Images and files used across your pages.",
                        **TENANT)

    stat_row(b, body, [
        ("Files", "48", "+6 this month", "neutral"),
        ("Storage used", "184 MB", "of 2 GB", "neutral"),
        ("Images", "41", "across 6 pages", "neutral"),
        ("Documents", "7", "PDF and slides", "neutral"),
    ])

    drop = b.frame("dropzone", parent=body, layout="vertical", gap=8,
                   crossAlign="center", mainAlign="center", padding=28,
                   fill="#EFF4FF", stroke="#C7DDFE", strokeWeight=1,
                   strokeAlign="inside", cornerRadius=6,
                   sizingH="fill", sizingV="fixed", height=132)
    b.ell(parent=drop, width=40, height=40, fill=C["surface"],
          stroke="#C7DDFE", strokeWeight=1, strokeAlign="inside",
          cornerRadius=999)
    t_body(b, "Drop files here, or browse", drop, C["text"], "Medium")
    t_meta(b, "JPG, PNG, SVG or PDF up to 10 MB", drop, C["textMuted"])

    toolbar(b, body, "Search assets", filters=["Type: All"])

    grid = b.frame("asset grid", parent=body, layout="vertical", gap=16,
                   crossAlign="min", sizingH="fill", sizingV="hug",
                   fill=CLEAR)
    for rix in range(2):
        row = b.h(f"asset row {rix}", parent=grid,
                  gap=16, crossAlign="min", sizingH="fill", sizingV="hug",
                  fill=CLEAR)
        for name, size, dims, added in ASSETS[rix * 3:(rix + 1) * 3]:
            card = b.frame(f"asset {name}", parent=row, layout="vertical", gap=0, padding=0,
                           width=(BODY_W - 2 * 16) // 3, sizingH="fixed",
                           sizingV="hug", fill=C["surface"],
                           stroke=C["border"], strokeWeight=1,
                           strokeAlign="inside", cornerRadius=6, effects=S1,
                           clip=True)
            pv = b.frame("thumb", parent=card, height=112,
                         fill=C["subtle"], stroke=C["borderSubtle"],
                         strokeWeight=1, strokeAlign="inside",
                         cornerRadius=[6, 6, 0, 0], layout="horizontal",
                         mainAlign="center", crossAlign="center",
                         sizingH="fill", sizingV="fixed")
            t_meta(b, name, pv, C["textMuted"])
            meta = b.v("meta", parent=card, gap=2, padding=[12, 16],
                       sizingH="fill", sizingV="hug")
            t_body(b, name, meta, C["text"], "Medium")
            t_meta(b, f"{size}  ·  {dims}", meta, C["textMuted"])
    return root


# =====================================================================
# 05 · Team
# =====================================================================

MEMBERS = [
    ("Ada Nwosu", "ada@gracechapel.org", "Tenant admin", "info", "Now"),
    ("Chinedu Okafor", "chinedu@gracechapel.org", "Editor", "neutral",
     "3 hrs ago"),
    ("Bola Adeyemi", "bola@gracechapel.org", "Editor", "neutral",
     "Yesterday"),
    ("Fatima Yusuf", "fatima@gracechapel.org", "Editor", "neutral",
     "2 days ago"),
    ("Grace Mbeki", "grace@gracechapel.org", "Editor", "neutral",
     "4 days ago"),
    ("Ibrahim Sanni", "ibrahim@gracechapel.org", "Editor", "neutral",
     "1 week ago"),
]

MW = [352, 224, 176, 176]


def t_team(b):
    root, body = screen(b, STEP * 5, "06 — Team", "team",
                        ["Grace Chapel RCF", "Team"], "Team",
                        "Who can edit and publish your site.",
                        actions=[("Invite member", "primary")], **TENANT)

    warn = b.frame("notice", parent=body, layout="vertical", gap=4,
                   padding=[12, 16], fill=C["infoBg"], stroke=C["infoBd"],
                   strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                   sizingH="fill", sizingV="hug")
    t_body(b, "You can invite people here. Only platform administrators can "
              "add tenant admins.", warn, C["info"], "Medium")

    toolbar(b, body, "Search members", filters=["Role: All"])

    tbl = b.frame("table", parent=body, fill=C["surface"], stroke=C["border"],
                  strokeWeight=1, strokeAlign="inside", cornerRadius=6,
                  effects=S1, layout="vertical", gap=0, padding=0,
                  sizingH="fill", sizingV="hug", clip=True)
    heads = ["Member", "Role", "Last active", "Access"]
    hr = b.frame("table head", parent=tbl, height=40, crossAlign="center",
                 padding=[0, 20], sizingH="fill", sizingV="fixed",
                 fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                 strokeSides=sides("b"), strokeAlign="inside")
    for name, w in zip(heads, MW):
        cell(b, name, hr, w, size=11, weight="SemiBold", color=C["textMuted"])
    spacer(b, hr)
    cell(b, "ACTIONS", hr, 64, size=11, weight="SemiBold",
         color=C["textMuted"], align="right")

    for i, (name, email, role, rtn, last) in enumerate(MEMBERS):
        r = row_shell(b, tbl, MW)
        uc = b.h("user cell", parent=r, width=MW[0], gap=10,
                 crossAlign="center", fill=CLEAR, sizingH="fixed",
                 sizingV="hug")
        av = b.frame("avatar", parent=uc, width=32, height=32,
                     fill=C["subtle"], stroke=C["border"], strokeWeight=1,
                     strokeAlign="inside", cornerRadius=999,
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", sizingH="fixed", sizingV="fixed")
        b.text("".join(p[0] for p in name.split()[:2]), parent=av,
               fontFamily=UI, fontSize=12, fontStyle="SemiBold",
               lineHeight="32px", fill=C["textSec"],
               textAutoResize="widthAndHeight")
        cell_stack(b, [(name, 13, "Medium", C["text"]),
                       (email, 12, "Regular", C["textMuted"])], uc,
                   MW[0] - 42)
        rw = b.frame("role cell", parent=r, width=MW[1], fill=CLEAR,
                     layout="horizontal", crossAlign="center",
                     sizingH="fixed", sizingV="hug")
        badge(b, role, rw, t=rtn)
        cell(b, last, r, MW[2], color=C["textMuted"])
        aw = b.frame("access cell", parent=r, width=MW[3], fill=CLEAR,
                     layout="horizontal", crossAlign="center",
                     sizingH="fixed", sizingV="hug")
        t_body(b, "Edit and publish" if role == "Editor" else "Full access",
               aw, C["textSec"])
        cell(b, "⋯", r, 64, size=16, color=C["textMuted"],
             align="right")
    pagination(b, tbl, "Showing 1–6 of 12", 12,
               pages=("‹", "1", "2", "›"))
    return root


# =====================================================================
# 06 · Domain
# =====================================================================

def t_domain(b):
    root, body = screen(b, STEP * 6, "07 — Domain", "domain",
                        ["Grace Chapel RCF", "Domain"], "Domain",
                        "Where your site lives on the internet.",
                        **TENANT)

    ok = b.frame("domain status", parent=body,gap=12,
                 crossAlign="center", padding=[16, 20], fill="#ECFDF3",
                 stroke=C["successBd"], strokeWeight=1, strokeAlign="inside",
                 cornerRadius=6, sizingH="fill", sizingV="fixed")
    b.ell(parent=ok, width=10, height=10, fill=C["success"], cornerRadius=999)
    okc = b.v("status text", parent=ok, gap=2, sizingH="fill")
    t_body(b, "gracechapel.org is live and secured", okc, C["success"],
           "Medium")
    t_meta(b, "Certificate issued 4 March 2026 · renews automatically · "
              "expires 4 June 2026", okc, C["success"])
    spacer(b, ok)
    btn(b, "Visit site", ok, kind="secondary", size="sm")

    half = (BODY_W - 24) // 2
    mid = b.frame("mid row", parent=body,gap=24,
                  crossAlign="min", sizingH="fill", sizingV="hug", fill=CLEAR)
    left = b.v("left", parent=mid, gap=24, width=half, fill=CLEAR,
               sizingH="fixed", sizingV="hug")
    right = b.v("right", parent=mid, gap=24, sizingH="fill", sizingV="hug",
                fill=CLEAR)

    c1 = content_card(b, left, "DNS records",
                      actions=["Check records"])
    t_meta(b, "These records are managed by the platform. You only need them "
              "if you move hosting.", c1, C["textMuted"], wrap=440)
    dns = b.v("records", parent=c1, gap=8, sizingH="fill")
    for kind, name, target, tn in (
            ("CNAME", "www", "cname.platform.church", "Verified"),
            ("A", "gracechapel.org", "203.0.113.24", "Verified"),
            ("TXT", "_rcf-verify", "rcf-verify=8f2a1c…", "Verified")):
        rec = b.h(f"dns {name}", parent=dns, gap=12,
                  crossAlign="center", padding=[0, 12], fill=C["subtle"],
                  stroke=C["borderSubtle"], strokeWeight=1,
                  strokeAlign="inside", cornerRadius=6, sizingH="fill",
                  sizingV="fixed", height=48)
        b.text(kind, parent=rec, fontFamily=UI, fontSize=12,
               fontStyle="SemiBold", lineHeight="20px",
               fill=C["textMuted"], textAutoResize="widthAndHeight")
        cell(b, name, rec, 120, weight="Medium")
        cell(b, target, rec, 200, color=C["textSec"])
        spacer(b, rec)
        badge(b, tn, rec, t="success", dot=True)

    c2 = content_card(b, right, "Subdomain fallback")
    t_body(b, "Your site is also reachable at", c2, C["textMuted"])
    fb = b.h("fallback url", parent=c2, gap=8, crossAlign="center",
             height=40, padding=[0, 14], fill=C["subtle"],
             stroke=C["border"], strokeWeight=1, strokeAlign="inside",
             cornerRadius=6, sizingH="fill", sizingV="fixed")
    b.text("https://grace-chapel.church", parent=fb, fontFamily=UI,
           fontSize=13, fontStyle="Medium", lineHeight="40px",
           fill=C["accent"], textAutoResize="widthAndHeight")
    t_meta(b, "Use this if your custom domain ever stops resolving.", c2,
           C["textMuted"], wrap=440)

    c3 = content_card(b, right, "Certificate")
    for k, v in (("Issuer", "Let's Encrypt"), ("Type", "DV"),
                 ("Issued", "4 March 2026"), ("Expires", "4 June 2026"),
                 ("Renewal", "Automatic, 30 days before expiry")):
        kv = b.h(f"kv {k}", parent=c3, gap=16, sizingH="fill",
                 sizingV="hug")
        cell(b, k, kv, 180, color=C["textMuted"])
        cell(b, v, kv, 260)
    return root


# =====================================================================
# 07 · Settings
# =====================================================================

def t_settings(b):
    root, body = screen(b, STEP * 7, "08 — Settings", "settings",
                        ["Grace Chapel RCF", "Settings"], "Settings",
                        "How your fellowship presents itself.", **TENANT)

    split = b.frame("split", parent=body,gap=48,
                    crossAlign="min", sizingH="fill", sizingV="hug",
                    fill=CLEAR)
    nav = b.v("settings nav", parent=split, gap=4, width=240, fill=CLEAR,
              sizingH="fixed", sizingV="hug")
    for i, item in enumerate(["Fellowship profile", "Logo & colours",
                              "Publishing", "Email & notifications",
                              "Danger zone"]):
        on = i == 0
        it = b.h(f"setnav {item}", parent=nav, gap=0,
                 height=36, crossAlign="center", padding=[0, 12],
                 fill="#EFF4FF" if on else CLEAR, cornerRadius=4,
                 sizingH="fill", sizingV="fixed")
        t_body(b, item, it, C["text"] if on else C["textSec"],
               "Medium" if on else "Regular")

    main = b.v("settings body", parent=split, gap=24, sizingH="fill",
               sizingV="hug", fill=CLEAR)

    cd = content_card(b, main, "Fellowship profile")
    grid = b.frame("field grid", parent=cd, layout="vertical", gap=16,
                   crossAlign="min", sizingH="fill", sizingV="hug",
                   fill=CLEAR)
    r1 = b.h("row", parent=grid, gap=16,
             crossAlign="min", sizingH="fill", sizingV="hug")
    field(b, "Fellowship name", "Grace Chapel RCF", r1, w=300)
    field(b, "Contact email", "hello@gracechapel.org", r1, w=300)
    r2 = b.h("row", parent=grid, gap=16,
             crossAlign="min", sizingH="fill", sizingV="hug")
    field(b, "Location", "Ikeja, Lagos", r2, w=300)
    field(b, "Phone", "+234 802 000 0000", r2, w=300)
    r3 = b.h("row", parent=grid, gap=16,
             crossAlign="min", sizingH="fill", sizingV="hug")
    field(b, "Short description", "A redeemed community since 1998.", r3,
          w=300, note="Shown in search results and social previews.")
    field(b, "Service times", "Sunday 9:00 · Wednesday 17:30", r3, w=300)
    save = b.h("save row", parent=cd, gap=12,
               crossAlign="center", sizingH="fill", sizingV="hug")
    spacer(b, save)
    btn(b, "Discard", save, kind="ghost")
    btn(b, "Save changes", save, kind="primary")

    cd2 = content_card(b, main, "Publishing")
    for lbl, desc in (("Require review before publishing",
                       "Off — editors publish immediately"),
                      ("Notify on publish", "Email the team when you publish"),
                      ("Show draft badge", "Mark unpublished changes")):
        r = b.h(f"pref {lbl}", parent=cd2, gap=16,
                crossAlign="center", sizingH="fill", sizingV="fixed",
                height=52)
        col = b.v("pref text", parent=r, gap=2, sizingH="fill")
        t_body(b, lbl, col, C["text"], "Medium")
        t_meta(b, desc, col, C["textMuted"])
        spacer(b, r)
        sw = b.frame("switch", parent=r, width=40, height=22,
                     fill=C["accent"], cornerRadius=999,
                     layout="horizontal", mainAlign="center",
                     crossAlign="center", padding=[0, 2], sizingH="fixed",
                     sizingV="fixed")
        b.ell(parent=sw, width=18, height=18, fill=C["surface"],
              cornerRadius=999)
    return root


SCREENS = [("t_sign_in", 0), ("t_dashboard", 1), ("t_pages", 2),
           ("t_theme", 3), ("t_assets", 4), ("t_team", 5), ("t_domain", 6),
           ("t_settings", 7)]