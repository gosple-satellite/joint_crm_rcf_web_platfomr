package repository

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"rcf/internal/domain"
	"rcf/internal/testutil"
)

func TestTenantRepo(t *testing.T) {
	ctx := context.Background()
	db := testutil.ResetTestDB(t)
	defer db.Close()

	repo := NewTenantRepo(db)

	// Create.
	ta := testutil.NewTenant(t, "Grace", "grace")
	require.NoError(t, repo.Create(ctx, ta))

	// Duplicate slug must fail.
	dup := testutil.NewTenant(t, "Grace2", "grace")
	require.Error(t, repo.Create(ctx, dup), "duplicate slug must be rejected")

	// GetByID.
	got, err := repo.GetByID(ctx, ta.ID)
	require.NoError(t, err)
	require.Equal(t, "Grace", got.Name)
	require.Equal(t, "grace", got.Slug)
	require.Equal(t, domain.StatusActive, got.Status)

	// GetBySlug.
	got, err = repo.GetBySlug(ctx, "grace")
	require.NoError(t, err)
	require.Equal(t, ta.ID, got.ID)

	// Missing returns ErrNotFound.
	_, err = repo.GetByID(ctx, uuid.New())
	require.ErrorIs(t, err, ErrNotFound)
	_, err = repo.GetBySlug(ctx, "nope")
	require.ErrorIs(t, err, ErrNotFound)

	// List.
	tb := testutil.NewTenant(t, "Hope", "hope")
	require.NoError(t, repo.Create(ctx, tb))
	list, err := repo.List(ctx)
	require.NoError(t, err)
	require.Len(t, list, 2)

	// SetStatus.
	require.NoError(t, repo.SetStatus(ctx, ta.ID, domain.StatusSuspended))
	got, err = repo.GetByID(ctx, ta.ID)
	require.NoError(t, err)
	require.Equal(t, domain.StatusSuspended, got.Status)

	// SetStatus on missing tenant returns ErrNotFound.
	require.ErrorIs(t, repo.SetStatus(ctx, uuid.New(), domain.StatusActive), ErrNotFound)
}

func TestUserRepo(t *testing.T) {
	ctx := context.Background()
	db := testutil.ResetTestDB(t)
	defer db.Close()

	repo := NewUserRepo(db)

	u := testutil.NewUser(t, "ada@example.com", domain.RoleTenantAdmin)
	require.NoError(t, repo.Create(ctx, u))

	// Duplicate email must fail.
	dup := testutil.NewUser(t, "ada@example.com", domain.RoleEditor)
	require.Error(t, repo.Create(ctx, dup), "duplicate email must be rejected")

	// GetByID.
	got, err := repo.GetByID(ctx, u.ID)
	require.NoError(t, err)
	require.Equal(t, "ada@example.com", got.Email)
	require.Equal(t, domain.RoleTenantAdmin, got.Role)

	// GetByEmail.
	got, err = repo.GetByEmail(ctx, "ada@example.com")
	require.NoError(t, err)
	require.Equal(t, u.ID, got.ID)

	// Missing returns ErrNotFound.
	_, err = repo.GetByID(ctx, uuid.New())
	require.ErrorIs(t, err, ErrNotFound)
	_, err = repo.GetByEmail(ctx, "nope@example.com")
	require.ErrorIs(t, err, ErrNotFound)

	// ExistsByEmail.
	exists, err := repo.ExistsByEmail(ctx, "ada@example.com")
	require.NoError(t, err)
	require.True(t, exists)
	exists, err = repo.ExistsByEmail(ctx, "nope@example.com")
	require.NoError(t, err)
	require.False(t, exists)
}
