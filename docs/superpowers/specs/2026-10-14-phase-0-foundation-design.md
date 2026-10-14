# Phase 0 — Foundation Design

Date: 2026-10-14
Status: Approved for implementation

## Scope

Phase 0 establishes the buildable, testable foundation for the RCF multi-tenant
platform. It is deliberately narrow: nothing here touches the visual editor,
themes, or public storefront. Its job is to make tenant isolation *provable*
before anything else is built on top.

## Goals

1. A Go module that compiles and runs.
2. A PostgreSQL schema with the core tenant/user tables and migrations.
3. A repository layer that **always** injects `tenant_id` — tenant isolation
   is enforced by the data layer, not remembered by callers.
4. JWT auth with three roles: `super_admin`, `tenant_admin`, `editor`.
5. Docker Compose wiring Go + Postgres + MinIO + Caddy so the whole stack
   starts with one command.
6. Tests that prove isolation: tenant A cannot read or write tenant B's rows.

## Non-goals (out of scope for Phase 0)

- No theme system, no GrapesJS, no visual editor.
- No public storefront, no custom domain routing, no Caddy TLS logic.
- No MinIO asset upload endpoints (MinIO is provisioned only).
- No React frontend.

## Stack (locked from the spec)

| Layer | Choice |
|---|---|
| Language | Go 1.26 |
| HTTP | Gin |
| DB driver | pgx (stdlib) |
| DB | PostgreSQL 16 |
| Auth | Custom JWT (HS256) + cookie/session |
| Container | Docker Compose |
| Testing | Go built-in `testing` + testify; integration tests against real Postgres |

## Module layout

```
rcf/
├── cmd/server/main.go
├── internal/
│   ├── config/      # env vars, validation
│   ├── domain/      # Tenant, User, TenantUser, Role enums
│   ├── repository/  # Postgres repos (tenant-scoped)
│   ├── service/     # pure business logic
│   ├── handler/     # HTTP layer (gin)
│   ├── auth/        # JWT issue/verify + middleware
│   ├── migrate/     # embedded SQL migrations (go:embed)
│   └── testutil/    # shared test helpers (test DB, fixtures)
├── docker-compose.yml
├── go.mod
└── go.sum
```

## Data model

```sql
tenants
  id            uuid primary key
  name          text not null
  slug          text unique not null
  custom_domain text
  status        text not null default 'active'   -- active | suspended
  created_at    timestamptz not null default now()

users
  id             uuid primary key
  email          text unique not null
  password_hash  bytea not null
  role           text not null                    -- super_admin | tenant_admin | editor
  created_at     timestamptz not null default now()

tenant_users
  tenant_id  uuid references tenants(id) on delete cascade
  user_id    uuid references users(id) on delete cascade
  role       text not null                    -- tenant_admin | editor (within tenant)
  created_at timestamptz not null default now()
  primary key (tenant_id, user_id)
```

`tenant_users.role` is the *per-tenant* role. `users.role` is the global role
(`super_admin` bypasses tenant scoping). This matches the spec's
`super_admin | tenant_admin | editor` model.

## Isolation contract

Every tenant-scoped repository method takes a `tenant_id` and the caller is
responsible for passing it. The repository **never** reads tenant context from
a global — it is an explicit parameter. Super-admin paths use separate
methods/queries that intentionally omit the filter.

The highest-value test: a `tenant_admin` for tenant A, authenticated, must get
a 404 (not 403, not 200-with-empty) when requesting tenant B's resource, and
must not be able to create a row attributed to tenant B.

## Auth

- JWT HS256, short-lived access token (15 min) + refresh token.
- Claims: `sub` (user id), `role` (global), `tid` (tenant id, null for super_admin).
- Middleware `RequireTenant` injects `tid` into the request context; routes that
  need it read it back. Super-admin routes use `RequireRole(super_admin)`.

## TDD approach

1. Write the test first for each unit.
2. Run, watch it fail (red).
3. Implement minimal code (green).
4. Refactor only where a test exposes a real smell.

Integration tests spin up a real Postgres (docker-compose test profile),
run migrations, and exercise the HTTP layer end-to-end.