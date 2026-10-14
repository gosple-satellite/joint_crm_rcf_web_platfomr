package handler

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/require"

	"rcf/internal/auth"
	"rcf/internal/config"
	"rcf/internal/domain"
	"rcf/internal/repository"
	"rcf/internal/service"
	"rcf/internal/testutil"
)

// TestTenantIsolation_HTTP proves tenant A cannot touch tenant B's resources.
func TestTenantIsolation_HTTP(t *testing.T) {
	// Set up a fresh DB and services.
	db := testutil.ResetTestDB(t)
	tenRepo := repository.NewTenantRepo(db)
	tenUserRepo := repository.NewTenantUserRepo(db)
	userRepo := repository.NewUserRepo(db)
	svc := service.NewTenantService(tenRepo, tenUserRepo, userRepo, auth.NewHasher())

	// Create two tenants with their admins.
	ta, ua, err := svc.CreateTenant(context.Background(), "Grace", "grace", "admin@grace.example", "password123")
	require.NoError(t, err)
	tb, ub, err := svc.CreateTenant(context.Background(), "Hope", "hope", "admin@hope.example", "password123")
	require.NoError(t, err)

	// Create an editor in tenant A.
	uc := domain.User{ID: uuid.New(), Email: "editor@grace.example", PasswordHash: mustHash(t), Role: domain.RoleEditor}
	require.NoError(t, userRepo.Create(context.Background(), uc))
	require.NoError(t, tenUserRepo.Add(context.Background(), ta.ID, uc.ID, domain.RoleTEditor))

	// Issue tokens.
	issuer := auth.NewJWTIssuer("test-secret").SetTTL(15 * time.Minute)
	uaToken, _ := issuer.Issue(ua.ID, ta.ID, domain.RoleTenantAdmin, 15*time.Minute)
	ubToken, _ := issuer.Issue(ub.ID, tb.ID, domain.RoleTenantAdmin, 15*time.Minute)
	ucToken, _ := issuer.Issue(uc.ID, ta.ID, domain.RoleEditor, 15*time.Minute)
	saToken, _ := issuer.IssueSuperAdmin(uuid.New(), 15*time.Minute)

	// Build router using the same DB.
	cfg := &config.Config{Addr: ":0", JWTSecret: "test-secret"}
	r := NewRouterWithDB(cfg, db)

	// Super admin can list both tenants.
	req := httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants", nil)
	req.Header.Set("Authorization", "Bearer "+saToken)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusOK, w.Code)
	var listResp struct {
		Tenants []tenantDTO `json:"tenants"`
	}
	require.NoError(t, json.NewDecoder(w.Body).Decode(&listResp))
	require.Len(t, listResp.Tenants, 2) // super admin sees both

	// Tenant A admin cannot list all tenants (forbidden).
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants", nil)
	req.Header.Set("Authorization", "Bearer "+uaToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusForbidden, w.Code)

	// Tenant A admin tries to GET tenant B by ID via admin endpoint — should fail (forbidden).
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants/"+tb.ID.String(), nil)
	req.Header.Set("Authorization", "Bearer "+uaToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusForbidden, w.Code) // tenant A cannot see tenant B

	// Tenant A admin cannot GET tenant A by ID via admin endpoint (only super_admin can).
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants/"+ta.ID.String(), nil)
	req.Header.Set("Authorization", "Bearer "+uaToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusForbidden, w.Code)

	// Tenant B admin cannot see tenant A.
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants/"+ta.ID.String(), nil)
	req.Header.Set("Authorization", "Bearer "+ubToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusForbidden, w.Code)

	// Tenant A editor token cannot list tenants (no super_admin role).
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants", nil)
	req.Header.Set("Authorization", "Bearer "+ucToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusForbidden, w.Code)
}

// TestTenantCRUD_HTTP exercises the full tenant lifecycle via super_admin.
func TestTenantCRUD_HTTP(t *testing.T) {
	// Set up a fresh DB and services.
	db := testutil.ResetTestDB(t)
	userRepo := repository.NewUserRepo(db)

	// Create super admin token for these tests.
	su := domain.User{ID: uuid.New(), Email: "sa@example.com", PasswordHash: mustHash(t), Role: domain.RoleSuperAdmin}
	require.NoError(t, userRepo.Create(context.Background(), su))
	issuer := auth.NewJWTIssuer("test-secret").SetTTL(15 * time.Minute)
	saToken, _ := issuer.Issue(su.ID, uuid.Nil, domain.RoleSuperAdmin, 15*time.Minute)

	cfg := &config.Config{Addr: ":0", JWTSecret: "test-secret"}
	r := NewRouterWithDB(cfg, db)

	// Create a tenant.
	createReq := map[string]string{
		"name":           "Voyage",
		"slug":           "voyage",
		"admin_email":    "captain@voyage.example",
		"admin_password": "secret123",
	}
	b, _ := json.Marshal(createReq)
	req := httptest.NewRequest(http.MethodPost, "/api/v1/admin/tenants", bytes.NewReader(b))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+saToken)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)
	var createResp struct {
		Tenant tenantDTO `json:"tenant"`
		User   userDTO   `json:"admin"`
		Token  string    `json:"token"`
	}
	require.NoError(t, json.NewDecoder(w.Body).Decode(&createResp))
	require.Equal(t, "Voyage", createResp.Tenant.Name)
	require.Equal(t, "voyage", createResp.Tenant.Slug)
	require.Equal(t, domain.RoleTenantAdmin, domain.RoleGlobal(createResp.User.Role))
	tenantVoyageID := createResp.Tenant.ID

	// List tenants — should now see exactly one (the voyage tenant we just created).
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants", nil)
	req.Header.Set("Authorization", "Bearer "+saToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusOK, w.Code)
	var listResp struct {
		Tenants []tenantDTO `json:"tenants"`
	}
	require.NoError(t, json.NewDecoder(w.Body).Decode(&listResp))
	require.Len(t, listResp.Tenants, 1)
	require.Equal(t, "Voyage", listResp.Tenants[0].Name)

	// Get the newly created tenant by id.
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants/"+tenantVoyageID, nil)
	req.Header.Set("Authorization", "Bearer "+saToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusOK, w.Code)
	var getResp tenantDTO
	require.NoError(t, json.NewDecoder(w.Body).Decode(&getResp))
	require.Equal(t, tenantVoyageID, getResp.ID)

	// Suspend the tenant.
	req = httptest.NewRequest(http.MethodPatch, "/api/v1/admin/tenants/"+tenantVoyageID+"/status", strings.NewReader(`{"status":"suspended"}`))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+saToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusOK, w.Code)
	var statusResp struct {
		Status string `json:"status"`
	}
	require.NoError(t, json.NewDecoder(w.Body).Decode(&statusResp))
	require.Equal(t, "suspended", statusResp.Status)

	// Confirm it's suspended.
	req = httptest.NewRequest(http.MethodGet, "/api/v1/admin/tenants/"+tenantVoyageID, nil)
	req.Header.Set("Authorization", "Bearer "+saToken)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	require.Equal(t, http.StatusOK, w.Code)
	require.NoError(t, json.NewDecoder(w.Body).Decode(&getResp))
	require.Equal(t, "suspended", getResp.Status)
}

func mustHash(t *testing.T) []byte {
	t.Helper()
	h, err := auth.NewHasher().Hash("password123")
	require.NoError(t, err)
	return h
}

// NewRouterWithDB builds a router from an existing *sql.DB. Used by tests.
func NewRouterWithDB(cfg *config.Config, database *sql.DB) *gin.Engine {
	g := gin.New()
	g.Use(gin.Recovery(), gin.Logger())

	tenRepo := repository.NewTenantRepo(database)
	tenUserRepo := repository.NewTenantUserRepo(database)
	userRepo := repository.NewUserRepo(database)

	issuer := auth.NewJWTIssuer(cfg.JWTSecret).SetTTL(cfg.TokenTTL())
	mw := NewMiddleware(issuer)

	svc := service.NewTenantService(tenRepo, tenUserRepo, userRepo, auth.NewHasher())
	tenantH := NewTenantHandler(svc, issuer, cfg.TokenTTL())

	g.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	authGroup := g.Group("/api/v1/auth")
	{
		authGroup.POST("/login", hLogin(tenRepo, userRepo, issuer, cfg.TokenTTL()))
	}

	sa := g.Group("/api/v1/admin")
	sa.Use(mw.RequireAuth(), mw.RequireRole(domain.RoleSuperAdmin))
	{
		sa.POST("/tenants", tenantH.CreateTenant)
		sa.GET("/tenants", tenantH.ListTenants)
		sa.GET("/tenants/:id", tenantH.GetTenant)
		sa.PATCH("/tenants/:id/status", tenantH.SetStatus)
	}

	ten := g.Group("/api/v1/t")
	ten.Use(mw.RequireAuth(), mw.RequireTenant())
	{
		// TODO: theme, page, asset endpoints (Phase 2).
	}

	return g
}
