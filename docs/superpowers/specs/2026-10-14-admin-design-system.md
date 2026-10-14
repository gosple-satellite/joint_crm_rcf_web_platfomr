# Design System & Admin UI — Institutional Slate

Date: 2026-10-14
Status: Approved for implementation
Companion design file: `figcraft/UIDESIGN.figcraft`
Depends on: `docs/superpowers/specs/2026-10-14-phase-0-foundation-design.md`

## Scope

This document specifies the design system and the **Super-Admin** admin UI for
the RCF multi-tenant platform. It is the visual and token contract that the
Vite + React (JSX) + Tailwind frontend will implement.

It covers 12 Super-Admin screens. The Tenant (RCF) admin surface reuses the
identical tokens, shell, and roughly 90% of the components; it is designed in a
second pass and is out of scope here except where noted.

### Goals

1. A token set complete enough to build both admin surfaces without inventing
   values mid-screen.
2. A component inventory with defined states, so every screen draws from one
   source.
3. One app-shell anatomy that both surfaces share.
4. Twelve Super-Admin screens specified at mockup fidelity: layout, real
   content, and empty/loading/error treatment noted.

### Non-goals

- No public storefront or tenant-facing website design. That is the theme
  system's output (Phase 2), not admin chrome.
- No GrapesJS canvas internals. The page editor (Phase 2) gets its own spec.
- No dark mode. See "Dark mode" below.
- No motion or interaction specification beyond hover/focus/active/disabled
  states.
- No mobile or tablet layouts. Desktop 1440 is the design target; responsive
  rules are an implementation concern.

## Direction: Institutional Slate

Chosen over a warm/gold ministry palette and an airy modern palette. Rationale:
the Super-Admin console is data-dense and must stay legible across 34 tenants;
a cool neutral ground with a single navy primary and one blue accent maximises
contrast budget for status colour, which carries real meaning on these screens
(active/suspended, domain verified/unverified, role).

Mood words: institutional, calm, precise, trustworthy. Not playful, not
luxurious. The user who lands on this screen is a platform operator checking
that 34 fellowships are healthy.

## Design tokens

Light mode only. Tokens are named by role, never by colour, so that adding a
dark palette is a token-value swap rather than a redesign.

### Colour

```
bg.canvas        #F7F8FA
bg.surface       #FFFFFF
bg.subtle        #F1F3F6      table headers, inset panels
bg.inverse       #101828

border.subtle    #EDEFF3      hairlines, internal dividers
border.default   #E4E7EC      card edges, inputs
border.strong    #CDD3DC      hover edges, focused-adjacent

text.primary     #101828
text.secondary   #475467
text.muted       #667085      helper text, placeholders, disabled
text.inverse     #FFFFFF

action.primary        #1B3A5C   navy — primary buttons, sidebar active
action.primary.hover  #14293F
action.accent         #2E6BE6   links, focus ring, secondary emphasis
action.accent.hover   #2559C4
focus.ring            #2E6BE6 @ 24%   3px ring, 2px offset
```

Status tokens ship as a triplet (text / background / border). They are the
only saturated colour allowed to appear outside `action.*`.

```
status.success     #067647 / #ECFDF3 / #ABEFC6
status.warning     #B54708 / #FFFAEB / #FEDF89
status.danger      #B42318 / #FEF3F2 / #FECDCA
status.info        #175CD3 / #EFF8FF / #B2DDFF
status.neutral     #475467 / #F2F4F7 / #E4E7EC
```

Usage mapping is fixed so the same meaning always takes the same colour:
tenant `active` → success, `suspended` → danger, `pending` → warning.
Domain `verified` → success, `pending` → warning, `failed` → danger.
Role `super_admin` → info, `tenant_admin` → neutral, `editor` → neutral muted.

### Typography

Two families, strictly divided.

- **Inter** — all UI: navigation, tables, forms, buttons, body copy, labels.
- **Source Serif 4** — reserved for three contexts only: the sign-in brand
  panel, empty-state headlines, and the wizard's review step headline. Never
  used in navigation, tables, or anywhere a datum is displayed.

| Token | Size / line | Weight | Tracking | Use |
|---|---|---|---|---|
| `type.micro` | 11 / 16 | 600 | +0.04em, uppercase | column headers, group labels, overlines |
| `type.meta` | 12 / 16 | 400–600 | 0 | table secondary cells, badges, timestamps |
| `type.body` | 13 / 20 | 400 | 0 | **default admin body**, table primary cells |
| `type.ui` | 14 / 20 | 400–600 | 0 | form labels, buttons, nav items, card body |
| `type.card` | 16 / 24 | 600 | −0.01em | card titles |
| `type.page` | 20 / 28 | 600 | −0.02em | page title |
| `type.stat` | 24 / 32 | 700 | −0.02em | KPI numbers |
| `type.display` | 32 / 40 | 600 | −0.02em | empty states, auth panel, serif only |

13px is the default body size. This is denser than typical SaaS and
deliberate: the tenant table carries name, slug, status, domain, theme, pages,
users, and date, and must show ~20 rows without scrolling at 1024 height.

Weights: 400 body, 500 nav-active and form labels, 600 page titles and
buttons, 700 stat numbers only.

### Spacing

4px base grid. Permitted values: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.

Screen padding is 32. Card internal padding is 20 for stat tiles, 24 for
content cards. Table cell padding is 12 vertical / 16 horizontal.

### Radii

| Token | Value | Use |
|---|---|---|
| `radius.control` | 4 | buttons, inputs, badges, table cell focus |
| `radius.card` | 6 | cards, panels, list rows |
| `radius.overlay` | 8 | modals, drawers, dropdowns, tooltips |
| `radius.pill` | 999 | status badges, avatars, filter chips |

### Elevation

```
shadow.s1   0 1px 2px rgba(16,24,40,0.06)                 cards at rest
shadow.s2   0 4px 8px -2px rgba(16,24,40,0.10),
            0 2px 4px -2px rgba(16,24,40,0.06)          dropdowns, popovers
shadow.s3   0 20px 24px -4px rgba(16,24,40,0.14)         modals, drawers
```

Cards use `s1` plus a `border.default` edge. Elevation is never used alone to
define a surface — a shadow without a border reads as unfinished on this
canvas.

### Dark mode

Out of scope for this pass. Because tokens are semantic, a dark palette is
additive. Application stakeholders work in the admin during business hours and
need accurate colour; if dark mode is requested later, it ships as a full
second review cycle rather than a token swap, since contrast pairings must be
re-derived.

## App shell

One shell, shared by both admin surfaces.

```
┌────────────┬──────────────────────────────────────────────┐
│            │ topbar 56                                    │
│  sidebar   ├──────────────────────────────────────────────┤
│  248       │ page header  title + description + actions   │
│            ├──────────────────────────────────────────────┤
│            │ content  max-width 1440, padding 32           │
└────────────┴──────────────────────────────────────────────┘
```

**Sidebar, 248px fixed, full height.**
- Brand block 64px: monogram 28 + product name + environment tag. On the
  tenant surface the monogram is replaced by the RCF's logo and the name is
  the RCF's name, with a "Back to platform" affordance in the footer.
- Nav groups: `micro` uppercase group label, then items at 16/20 with 8px
  gap; items are 36px tall, `radius.control`, `action.primary` at 8% opacity
  plus `text.primary` when active; `text.muted` when idle.
- Footer: user chip — 28px avatar, name, role, chevron — opening an account
  menu.

**Topbar, 56px.**
- Left: breadcrumb (`Platform / Tenants / Grace Chapel`), `type.ui`.
- Centre: global search, 320px, `⌘K` hint, opens a command palette.
- Right: notification bell with unread dot, help link, 28px avatar.

**Page header.**
- Title `type.page`, description `type.body` in `text.muted` beneath.
- Actions right-aligned in the header, primary action last (rightmost).
- Optional 40px tab row beneath for tabbed screens (tenant detail, settings).

## Component inventory

Every screen draws from this list. States listed here are the required states.

**Buttons** — variants `primary` (`action.primary` fill), `secondary` (surface
+ `border.default`), `ghost` (surface, no border), `danger` (`status.danger`
text, `#FEF3F2` fill). Sizes `sm` 32 / `md` 36 / `lg` 40, horizontal padding
16 (sm) / 20 (md, lg), `radius.control`, `type.ui` 600. States: default,
hover, active (1px down, shadow removed), focus (focus ring), disabled
(48% opacity, no pointer), loading (spinner replaces label, width locked).

**Inputs** — `text`, `textarea`, `select`, `checkbox`, `radio`, `switch`,
`search`, `fileDrop`. Text inputs are 36px (`sm` 32), `radius.control`,
`border.default`, `bg.surface`, padding 0 12, placeholder `text.muted`.
States: default, hover (`border.strong`), focus (`border.accent` + focus
ring), error (`status.danger` border + `status.danger` helper text beneath,
always 12/16), disabled (`bg.subtle`, `text.muted`), loading (trailing
spinner). Label always sits above the control, `type.ui` 500, 6px gap.
Helper text beneath, `type.meta` `text.muted`, 4px gap.

**Navigation** — sidebar item (default / active / disabled), group label,
breadcrumb (clickable segments `text.accent`, current segment
`text.primary`), tab row (underline `action.primary` 2px, inactive
`text.secondary`).

**Data** — data table (sortable column headers with caret, filterable via
toolbar, optional checkbox column for bulk selection, row hover
`bg.subtle`, selected row `action.accent` @ 8% + `border.accent` left 2px);
row action menu (kebab, right-aligned, `shadow.s2`); status badge (pill, 20px,
`type.meta` 600, triplet colours); avatar+name cell (28px avatar, name
`type.body` 500, supporting line `type.meta` `text.muted`); pagination
(page size selector, range text `Showing 1–20 of 34`, prev/next).

**Feedback** — toast (bottom-right, 400px, `shadow.s2`, `radius.overlay`,
4 tones, auto-dismiss 5s with a progress hairline); banner (full-width,
`radius.card`, 4 tones, optional title + dismiss); empty state (icon 48,
`type.display` serif headline, `type.body` supporting line, primary action);
skeleton (shimmer block matching the row it replaces); spinner (16px, 1.5px
stroke).

**Overlays** — modal (`sm` 480, `md` 640, `lg` 960; `shadow.s3`;
`radius.overlay`; header 64 with title + close, body 24 padding, footer 64
with actions right-aligned, primary rightmost); drawer (right, 480, full
height, `shadow.s3`); dropdown menu (min-width 200, item 32, `shadow.s2`);
tooltip (max-width 240, `radius.overlay`, 11/16, dark `text.inverse` on
`bg.inverse`); confirm dialog (`md` 400 variant, danger action, copy states
the consequence).

**Display** — KPI tile (`s1`, 20 padding, `type.meta` uppercase label,
`type.stat` number, delta chip `type.meta` in success/danger/neutral);
content card (`s1` + `border.default`, `radius.card`, optional header row
48 with title + actions); list row (56, avatar/icon 40, two lines, chevron);
activity timeline (20px spine, 8px node dots, actor + action + relative
timestamp); key-value list (two columns, `type.body`, 12px row gap);
progress bar (6px track `bg.subtle`, fill `action.accent`); token swatch
(colour chip 32 + name `type.meta` + hex `type.meta` muted).

## Super-Admin screen inventory

Frames are 1440 × 1024. Navigation is marked **[nav]** where a screen is
entered from the sidebar.

| # | Screen | Nav | Key contents |
|---|---|---|---|
| 01 | Sign in | — | Split layout: brand panel left (navy, Source Serif 4 headline, three trust bullets), card right centred at 400. Email + password, show/hide, remember me, inline error, forgot password, SSO placeholder divider. |
| 02 | Dashboard | Overview | Four KPI tiles; tenants-by-status donut; signups-over-time column chart; recent activity timeline (8 items); "tenants needing attention" list (3 rows: domain unverified, theme unpublished, zero pages). |
| 03 | Tenants | Tenants | Toolbar: search, status filter, sort, "New tenant". Table: RCF (avatar + name + slug), status badge, domain with verification dot, theme, pages, users, created, row kebab. Bulk-select bar on selection. Row click → 04. Empty state when filtered to zero. |
| 04 | Tenant detail | — | Header: avatar, name, slug, status badge, actions (View site, Edit, Suspend/Activate). Four stat tiles. Tabs: Overview · Users · Domains · Theme · Pages · Activity. Overview shows identity block, domain block with DNS instructions, theme block, team list, recent activity. |
| 05 | Provision tenant | — | Four-step wizard: Identity → Domain → Theme → Admin invite, plus a Review step. Vertical progress rail on the left (240), step body right. Per-step validation on Next. Final step summarises all entries with an Edit link per block; success state shows the created slug, domain, and a copy-to-clipboard admin URL. |
| 06 | Users | Users | Table: user (avatar + name + email), global role badge, tenants joined (count, expandable), last active, status. Actions: invite user, suspend. Invite opens a modal with email + global role + tenant assignment multi-select. |
| 07 | Theme library | Themes | Card grid, 3 across: preview image 16:10, name, author, installs, published toggle. Click opens a right drawer with large preview, section list, metadata, publish/unpublish. Header has "Upload theme". Empty state for a category with no themes. |
| 08 | Section library | Sections | Grouped by category: Hero, Testimonial, Events, Giving, Footer, Navigation. Card grid of block previews with name, category, usage count, author. Tenant submissions appear in a "Pending approval" group with approve/reject. |
| 09 | Domains | Domains | Table: domain, tenant, verification status badge, TLS status, DNS record, last checked, actions (Check now, Re-verify). Selecting a row expands a detail row with copyable DNS instructions (CNAME + verification TXT record) and a status timeline. |
| 10 | Analytics | Analytics | Date-range picker (30d/90d/12m custom) top right. Two large charts: page views and sessions over time (area). Below: top tenants bar chart (horizontal, 8 rows), device split, live visitors card. |
| 11 | Activity log | Activity | Filter bar: actor, action type, tenant, date range. Table: timestamp, actor avatar + name, action chip, target, tenant, IP. Severity chips for destructive actions. Paginated. |
| 12 | Platform settings | Settings | Sectioned form in a two-column layout (nav 240 + body). Sections: Platform identity, Branding, Domain defaults, Email/SMTP, Roles & permissions matrix (role × capability grid), Danger zone (separate bordered panel, danger styling, requires typed confirmation). |

## Tenant surface (second pass)

Named here so the system is not designed against the Super-Admin alone: the
tenant surface uses the same shell, the same tokens, and the same components,
with these screens — Dashboard, Pages, Theme library, Assets, Team, Domain,
Settings. The only additions the Super-Admin does not exercise are the
publishing flow (publish/unpublish button, autosave indicator) and the asset
manager (grid with upload dropzone). Both are built from existing components;
no new tokens are anticipated.

## Implementation contract

This design is the source of truth for the frontend. It maps to Tailwind as
follows: each token group becomes a theme extension, e.g. `bg.surface` →
`bg-surface`, `text.muted` → `text-muted`, `status.success.text` →
`text-status-success-text`. Component states become `data-` attributes or
variant classes. Type tokens become a `type` scale in the theme, not
per-call Tailwind font sizes.

## Schema gaps these screens require

The Phase 0 schema defines `tenants.status` as `active | suspended` and no
domain verification state at all. The screens below need more than that. These
are recorded here so the mockups are not silently designing around missing
fields, and so the Phase 1 and Phase 2 migrations can add them deliberately.

1. **`tenants.status` gains `pending`.** Used by the provisioning wizard's
   success state (created, awaiting domain verification) and by the
   "tenants needing attention" list. Requires no new column, only a widened
   `CHECK` constraint.
2. **`domains` as a table, not a column.** `tenants.custom_domain` in Phase 0
   holds one domain as free text with no verification state. Screens 09 and
   the tenant-detail domain block need a `domains` table with `tenant_id`,
   `hostname`, `verification_status`, `verification_token`, `tls_status`, and
   `last_checked_at`. Phase 3 of the roadmap already plans on-demand TLS and a
   `/check-domain` endpoint, which presupposes this table.
3. **`themes` gains `author_tenant_id`, `install_count`, `published_at`.**
   Screen 07's marketplace grid shows author and install count; a tenant
   submitting a theme needs an author reference and a publication state.
4. **`users` gains `last_active_at` and `suspended_at`.** Screen 06 sorts by
   last active and offers a suspend action, neither of which exists in Phase 0.
5. **`audit_log` table.** Screen 11 has no backing table in any phase of the
   roadmap. Cheapest version: `(id, actor_user_id, action, target_type,
   target_id, tenant_id, ip, created_at)`, written by the repository layer on
   every mutating call. Without it, screen 11 is unimplementable.

Gaps 2 and 5 are hard dependencies — those screens cannot ship without them.
Gaps 1, 3, and 4 are additive and can ride along with whatever migration their
phase already requires.

## Build order

1. Foundations frame: tokens, type scale, spacing, radius, elevation, full
   component sheet, and the three shell variants (sidebar collapsed, nav
   group expanded, tabbed header).
2. Screens 01 and 03 first — sign-in establishes the brand voice, the tenant
   table establishes the data-density target that every later screen must
   respect.
3. Screens 02, 04, 06.
4. Screens 05, 07, 08.
5. Screens 09, 10, 11, 12.
6. Tenant surface, second pass.

Each frame is committed to `figcraft/UIDESIGN.figcraft` after approval.