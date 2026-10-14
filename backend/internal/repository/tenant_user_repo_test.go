package repository

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"rcf/internal/domain"
	"rcf/internal/testutil"
)

func TestTenantUserRepo_Isolation(t *testing.T) {
	ctx := context.Background()
	db := testutil.ResetTestDB(t)
	defer db.Close()

	repo := NewTenantUserRepo(db)
	tenRepo := NewTenantRepo(db)
	userRepo := NewUserRepo(db)

	// Two tenants, three users.
	ta := testutil.NewTenant(t, "A", "tenant-a")
	tb := testutil.NewTenant(t, "B", "tenant-b")
	require.NoError(t, tenRepo.Create(ctx, ta))
	require.NoError(t, tenRepo.Create(ctx, tb))

	ua := testutil.NewUser(t, "a@example.com", domain.RoleTenantAdmin)
	ub := testutil.NewUser(t, "b@example.com", domain.RoleTenantAdmin)
	uc := testutil.NewUser(t, "c@example.com", domain.RoleEditor)
	require.NoError(t, userRepo.Create(ctx, ua))
	require.NoError(t, userRepo.Create(ctx, ub))
	require.NoError(t, userRepo.Create(ctx, uc))

	// ua and uc belong to tenant A; ub belongs to tenant B.
	require.NoError(t, repo.Add(ctx, ta.ID, ua.ID, domain.RoleTAdmin))
	require.NoError(t, repo.Add(ctx, ta.ID, uc.ID, domain.RoleTEditor))
	require.NoError(t, repo.Add(ctx, tb.ID, ub.ID, domain.RoleTAdmin))

	// Tenant A's member list must contain ua and uc, and NOT ub.
	membersA, err := repo.ListByTenant(ctx, ta.ID)
	require.NoError(t, err)
	require.Len(t, membersA, 2)
	gotA := map[uuid.UUID]domain.RoleTenant{}
	for _, m := range membersA {
		gotA[m.UserID] = m.Role
	}
	require.Equal(t, domain.RoleTAdmin, gotA[ua.ID], "ua should be tenant_admin in A")
	require.Equal(t, domain.RoleTEditor, gotA[uc.ID], "uc should be editor in A")
	_, hasUB := gotA[ub.ID]
	require.False(t, hasUB, "tenant A must not see tenant B's user ub")

	// Tenant B's member list must contain only ub.
	membersB, err := repo.ListByTenant(ctx, tb.ID)
	require.NoError(t, err)
	require.Len(t, membersB, 1)
	require.Equal(t, ub.ID, membersB[0].UserID)

	// Duplicate add must be rejected (primary key).
	err = repo.Add(ctx, ta.ID, ua.ID, domain.RoleTAdmin)
	require.Error(t, err, "duplicate tenant_user row must be rejected")

	// IsMember checks.
	isMember, err := repo.IsMember(ctx, ta.ID, ua.ID)
	require.NoError(t, err)
	require.True(t, isMember)
	isMember, err = repo.IsMember(ctx, ta.ID, ub.ID)
	require.NoError(t, err)
	require.False(t, isMember, "ub is not a member of tenant A")
}

func TestTenantUserRepo_AddRejectsUnknownTenant(t *testing.T) {
	ctx := context.Background()
	db := testutil.ResetTestDB(t)
	defer db.Close()

	repo := NewTenantUserRepo(db)
	tenRepo := NewTenantRepo(db)
	userRepo := NewUserRepo(db)

	ten := testutil.NewTenant(t, "C", "tenant-c")
	require.NoError(t, tenRepo.Create(ctx, ten))
	u := testutil.NewUser(t, "c@example.com", domain.RoleTenantAdmin)
	require.NoError(t, userRepo.Create(ctx, u))

	// Linking to a non-existent tenant must fail (FK).
	require.Error(t, repo.Add(ctx, domain.NewUUID(), u.ID, domain.RoleTAdmin),
		"FK to unknown tenant must be rejected")

	// Linking a non-existent user must fail (FK).
	require.Error(t, repo.Add(ctx, ten.ID, domain.NewUUID(), domain.RoleTAdmin),
		"FK to unknown user must be rejected")
}
