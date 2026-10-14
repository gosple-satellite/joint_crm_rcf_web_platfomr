package repository

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"strings"

	"github.com/google/uuid"

	"rcf/internal/domain"
)

// ErrNotFound is returned when a read finds no rows.
var ErrNotFound = errors.New("repository: not found")

// TenantRepo is the global (non-tenant-scoped) repository for tenants.
// Tenant-scoped reads must go through a tenant-scoped wrapper that injects tid.
type TenantRepo struct{ db *sql.DB }

func NewTenantRepo(db *sql.DB) *TenantRepo { return &TenantRepo{db: db} }

// DB returns the underlying connection so other repos can be constructed
// lazily (e.g. for per-request tenant user lookups).
func (r *TenantRepo) DB() *sql.DB { return r.db }

// Create inserts a tenant. Returns ErrAlreadyExists on slug conflict.
func (r *TenantRepo) Create(ctx context.Context, t domain.Tenant) error {
	_, err := r.db.ExecContext(ctx,
		`INSERT INTO tenants (id, name, slug, custom_domain, status, created_at)
		 VALUES ($1, $2, $3, $4, $5, now())`,
		t.ID, t.Name, t.Slug, t.CustomDomain, t.Status,
	)
	if err != nil {
		return fmt.Errorf("insert tenant: %w", err)
	}
	return nil
}

// GetByID returns a tenant by id. Returns ErrNotFound if absent.
func (r *TenantRepo) GetByID(ctx context.Context, id uuid.UUID) (domain.Tenant, error) {
	row := r.db.QueryRowContext(ctx,
		`SELECT id, name, slug, custom_domain, status, created_at FROM tenants WHERE id = $1`,
		id,
	)
	t, err := scanTenant(row)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return domain.Tenant{}, ErrNotFound
		}
		return domain.Tenant{}, err
	}
	return t, nil
}

// GetBySlug returns a tenant by slug. Returns ErrNotFound if absent.
func (r *TenantRepo) GetBySlug(ctx context.Context, slug string) (domain.Tenant, error) {
	row := r.db.QueryRowContext(ctx,
		`SELECT id, name, slug, custom_domain, status, created_at FROM tenants WHERE slug = $1`,
		slug,
	)
	t, err := scanTenant(row)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return domain.Tenant{}, ErrNotFound
		}
		return domain.Tenant{}, err
	}
	return t, nil
}

// GetBySlugOrID resolves a tenant by slug or uuid. Returns ErrNotFound if absent.
func (r *TenantRepo) GetBySlugOrID(ctx context.Context, slugOrID string) (domain.Tenant, error) {
	slugOrID = strings.TrimSpace(slugOrID)
	if id, err := uuid.Parse(slugOrID); err == nil {
		return r.GetByID(ctx, id)
	}
	return r.GetBySlug(ctx, slugOrID)
}

// List returns all tenants ordered by name.
func (r *TenantRepo) List(ctx context.Context) ([]domain.Tenant, error) {
	rows, err := r.db.QueryContext(ctx,
		`SELECT id, name, slug, custom_domain, status, created_at FROM tenants ORDER BY name`,
	)
	if err != nil {
		return nil, fmt.Errorf("list tenants: %w", err)
	}
	defer rows.Close()

	var out []domain.Tenant
	for rows.Next() {
		t, err := scanTenant(rows)
		if err != nil {
			return nil, err
		}
		out = append(out, t)
	}
	return out, rows.Err()
}

// SetStatus updates a tenant's status. Returns ErrNotFound if absent.
func (r *TenantRepo) SetStatus(ctx context.Context, id uuid.UUID, status domain.Status) error {
	res, err := r.db.ExecContext(ctx,
		`UPDATE tenants SET status = $1 WHERE id = $2`, status, id,
	)
	if err != nil {
		return fmt.Errorf("set status: %w", err)
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return ErrNotFound
	}
	return nil
}

func scanTenant(row rowScanner) (domain.Tenant, error) {
	var t domain.Tenant
	err := row.Scan(
		&t.ID, &t.Name, &t.Slug, &t.CustomDomain, &t.Status, &t.CreatedAt,
	)
	if err != nil {
		return domain.Tenant{}, fmt.Errorf("scan tenant: %w", err)
	}
	return t, nil
}

// rowScanner covers *sql.Row and *sql.Rows.
type rowScanner interface {
	Scan(...interface{}) error
}
