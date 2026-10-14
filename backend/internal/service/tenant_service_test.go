package service

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"rcf/internal/auth"
	"rcf/internal/domain"
	"rcf/internal/repository"
	"rcf/internal/testutil"
)

func newTestService(t *testing.T) (*TenantService, *repository.TenantRepo, *repository.TenantUserRepo, *repository.UserRepo) {
	t.Helper()
	db := testutil.ResetTestDB(t)
	tenRepo := repository.NewTenantRepo(db)
	tenUser := repository.NewTenantUserRepo(db)
	userRepo := repository.NewUserRepo(db)
	svc := NewTenantService(tenRepo, tenUser, userRepo, auth.NewHasher())
	return svc, tenRepo, tenUser, userRepo
}

func TestTenantService_CreateTenant(t *testing.T) {
	ctx := context.Background()
	svc, _, _, _ := newTestService(t)

	ten, admin, err := svc.CreateTenant(ctx, "Grace", "grace", "admin@grace.example", "password123")
	require.NoError(t, err)
	require.Equal(t, "Grace", ten.Name)
	require.Equal(t, "grace", ten.Slug)
	require.Equal(t, domain.StatusActive, ten.Status)
	require.NotEqual(t, uuid.Nil, ten.ID)
	require.Equal(t, domain.RoleTenantAdmin, admin.Role)
	require.Equal(t, "admin@grace.example", admin.Email)
}

func TestTenantService_CreateTenantRejectsDuplicateSlug(t *testing.T) {
	ctx := context.Background()
	svc, _, _, _ := newTestService(t)

	_, _, err := svc.CreateTenant(ctx, "Grace", "grace", "a@example.com", "password123")
	require.NoError(t, err)
	_, _, err = svc.CreateTenant(ctx, "Grace2", "grace", "b@example.com", "password123")
	require.ErrorIs(t, err, ErrSlugTaken)
}

func TestTenantService_CreateTenantRejectsEmptyFields(t *testing.T) {
	ctx := context.Background()
	svc, _, _, _ := newTestService(t)

	for _, tc := range []struct {
		name, slug, email, pw string
	}{
		{"", "x", "a@e.com", "p"},
		{"n", "", "a@e.com", "p"},
		{"n", "s", "", "p"},
		{"n", "s", "a@e.com", ""},
	} {
		_, _, err := svc.CreateTenant(ctx, tc.name, tc.slug, tc.email, tc.pw)
		require.Error(t, err, "empty fields: %+v", tc)
	}
}

func TestTenantService_CreateTenantLinksAdminToTenant(t *testing.T) {
	ctx := context.Background()
	svc, _, tenUser, userRepo := newTestService(t)

	ten, admin, err := svc.CreateTenant(ctx, "Grace", "grace", "admin@grace.example", "password123")
	require.NoError(t, err)

	// Admin must be a member of the tenant.
	isMember, err := tenUser.IsMember(ctx, ten.ID, admin.ID)
	require.NoError(t, err)
	require.True(t, isMember)

	// Admin's per-tenant role must be tenant_admin.
	members, err := tenUser.ListByTenant(ctx, ten.ID)
	require.NoError(t, err)
	require.Len(t, members, 1)
	require.Equal(t, domain.RoleTAdmin, members[0].Role)

	// Admin password must verify.
	got, err := userRepo.GetByID(ctx, admin.ID)
	require.NoError(t, err)
	require.NoError(t, auth.NewHasher().Verify(got.PasswordHash, []byte("password123")))
}

func TestTenantService_ListAndSetStatus(t *testing.T) {
	ctx := context.Background()
	svc, _, _, _ := newTestService(t)

	_, _, err := svc.CreateTenant(ctx, "Grace", "grace", "a@example.com", "password123")
	require.NoError(t, err)
	_, _, err = svc.CreateTenant(ctx, "Hope", "hope", "b@example.com", "password123")
	require.NoError(t, err)

	list, err := svc.ListTenants(ctx)
	require.NoError(t, err)
	require.Len(t, list, 2)

	// Find Grace and suspend it.
	var graceID uuid.UUID
	for _, t := range list {
		if t.Slug == "grace" {
			graceID = t.ID
		}
	}
	require.NoError(t, svc.SetStatus(ctx, graceID, domain.StatusSuspended))

	got, err := svc.GetTenant(ctx, graceID)
	require.NoError(t, err)
	require.Equal(t, domain.StatusSuspended, got.Status)

	// SetStatus on missing tenant must fail.
	require.ErrorIs(t, svc.SetStatus(ctx, uuid.New(), domain.StatusActive), repository.ErrNotFound)
}
