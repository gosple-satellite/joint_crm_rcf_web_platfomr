package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"

	"rcf/internal/domain"
)

// TenantUserRepo is tenant-scoped: every method takes a tenant_id and the
// caller is responsible for passing it. The repo never reads tenant context
// from a global — isolation is enforced by an explicit parameter.
type TenantUserRepo struct{ db *sql.DB }

func NewTenantUserRepo(db *sql.DB) *TenantUserRepo { return &TenantUserRepo{db: db} }

// Add links a user to a tenant with a per-tenant role.
// Returns a unique-violation error on duplicate (tenant_id, user_id).
func (r *TenantUserRepo) Add(ctx context.Context, tenantID, userID uuid.UUID, role domain.RoleTenant) error {
	_, err := r.db.ExecContext(ctx,
		`INSERT INTO tenant_users (tenant_id, user_id, role, created_at)
		 VALUES ($1, $2, $3, now())`,
		tenantID, userID, role,
	)
	if err != nil {
		return fmt.Errorf("add tenant_user: %w", err)
	}
	return nil
}

// ListByTenant returns all tenant_users for a tenant, ordered by email.
func (r *TenantUserRepo) ListByTenant(ctx context.Context, tenantID uuid.UUID) ([]domain.TenantUser, error) {
	rows, err := r.db.QueryContext(ctx,
		`SELECT tu.tenant_id, tu.user_id, tu.role, tu.created_at
		 FROM tenant_users tu
		 JOIN users u ON u.id = tu.user_id
		 WHERE tu.tenant_id = $1
		 ORDER BY u.email`, tenantID,
	)
	if err != nil {
		return nil, fmt.Errorf("list tenant_users: %w", err)
	}
	defer rows.Close()

	var out []domain.TenantUser
	for rows.Next() {
		var tu domain.TenantUser
		if err := rows.Scan(&tu.TenantID, &tu.UserID, &tu.Role, &tu.CreatedAt); err != nil {
			return nil, fmt.Errorf("scan tenant_user: %w", err)
		}
		out = append(out, tu)
	}
	return out, rows.Err()
}

// IsMember reports whether userID is linked to tenantID.
func (r *TenantUserRepo) IsMember(ctx context.Context, tenantID, userID uuid.UUID) (bool, error) {
	var exists bool
	err := r.db.QueryRowContext(ctx,
		`SELECT EXISTS(
			SELECT 1 FROM tenant_users
			WHERE tenant_id = $1 AND user_id = $2
		)`, tenantID, userID,
	).Scan(&exists)
	return exists, err
}

// Remove unlinks a user from a tenant.
func (r *TenantUserRepo) Remove(ctx context.Context, tenantID, userID uuid.UUID) error {
	res, err := r.db.ExecContext(ctx,
		`DELETE FROM tenant_users WHERE tenant_id = $1 AND user_id = $2`,
		tenantID, userID,
	)
	if err != nil {
		return fmt.Errorf("remove tenant_user: %w", err)
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return sql.ErrNoRows
	}
	return nil
}
