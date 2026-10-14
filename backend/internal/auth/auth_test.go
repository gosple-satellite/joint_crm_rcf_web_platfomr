package auth

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"rcf/internal/domain"
)

func TestPasswordHashRoundTrip(t *testing.T) {
	h := NewHasher()
	hash, err := h.Hash("hunter2")
	require.NoError(t, err)
	require.NotEqual(t, "hunter2", string(hash))

	require.NoError(t, h.Verify(hash, []byte("hunter2")))
	require.Error(t, h.Verify(hash, []byte("wrong")))
}

func TestPasswordHashRejectsEmpty(t *testing.T) {
	h := NewHasher()
	_, err := h.Hash("")
	require.Error(t, err)
}

func TestJWTIssueVerify(t *testing.T) {
	issuer := NewJWTIssuer("test-secret")
	uid := uuid.New()
	tid := uuid.New()

	tok, err := issuer.Issue(uid, tid, domain.RoleTenantAdmin, time.Minute)
	require.NoError(t, err)
	require.NotEmpty(t, tok)

	claims, err := issuer.Verify(tok)
	require.NoError(t, err)
	require.Equal(t, uid, claims.UserID)
	require.Equal(t, tid, claims.TenantID)
	require.Equal(t, domain.RoleTenantAdmin, claims.Role)
}

func TestJWTVerifyRejectsTampered(t *testing.T) {
	issuer := NewJWTIssuer("test-secret")
	uid := uuid.New()
	tid := uuid.New()

	tok, err := issuer.Issue(uid, tid, domain.RoleTenantAdmin, time.Minute)
	require.NoError(t, err)

	// Tamper with the signature segment.
	tampered := tok[:len(tok)-5] + "xxxxx"
	_, err = issuer.Verify(tampered)
	require.Error(t, err, "tampered token must be rejected")

	// Wrong secret.
	bad := NewJWTIssuer("other-secret")
	_, err = bad.Verify(tok)
	require.Error(t, err, "token signed with different secret must be rejected")
}

func TestJWTVerifyRejectsExpired(t *testing.T) {
	issuer := NewJWTIssuer("test-secret")
	uid := uuid.New()
	tid := uuid.New()

	tok, err := issuer.IssueExpired(uid, tid, domain.RoleTenantAdmin)
	require.NoError(t, err)

	_, err = issuer.Verify(tok)
	require.Error(t, err, "expired token must be rejected")
}

func TestJWTSuperAdminHasNoTenant(t *testing.T) {
	issuer := NewJWTIssuer("test-secret")
	uid := uuid.New()

	tok, err := issuer.IssueSuperAdmin(uid, time.Minute)
	require.NoError(t, err)

	claims, err := issuer.Verify(tok)
	require.NoError(t, err)
	require.Equal(t, uid, claims.UserID)
	require.Equal(t, domain.RoleSuperAdmin, claims.Role)
	require.Zero(t, claims.TenantID, "super_admin has no tenant")
}

func TestRequireRole(t *testing.T) {
	uid := uuid.New()
	tid := uuid.New()
	claims := &Claims{
		UserID:   uid,
		TenantID: tid,
		Role:     domain.RoleTenantAdmin,
	}

	require.True(t, claims.HasRole(domain.RoleTenantAdmin))
	require.False(t, claims.HasRole(domain.RoleEditor))
	require.False(t, claims.HasRole(domain.RoleSuperAdmin))
	require.True(t, claims.IsSuperAdmin() == false)

	sa := &Claims{UserID: uid, Role: domain.RoleSuperAdmin}
	require.True(t, sa.IsSuperAdmin())
	require.True(t, sa.HasRole(domain.RoleSuperAdmin))
}

func TestRequireTenantContext(t *testing.T) {
	ctx := context.Background()
	uid := uuid.New()
	tid := uuid.New()

	// No claims -> no tenant.
	_, ok := TenantIDFromContext(ctx)
	require.False(t, ok)

	// With claims -> tenant present.
	ctx = WithClaims(ctx, &Claims{UserID: uid, TenantID: tid, Role: domain.RoleTenantAdmin})
	got, ok := TenantIDFromContext(ctx)
	require.True(t, ok)
	require.Equal(t, tid, got)

	// Super-admin claims -> no tenant (zero UUID).
	ctx = WithClaims(ctx, &Claims{UserID: uid, Role: domain.RoleSuperAdmin})
	_, ok = TenantIDFromContext(ctx)
	require.False(t, ok, "super_admin has no tenant context")
}
