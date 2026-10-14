package handler

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"

	"rcf/internal/auth"
	"rcf/internal/domain"
)

// Middleware wires auth into the gin router.
type Middleware struct {
	issuer *auth.JWTIssuer
}

func NewMiddleware(issuer *auth.JWTIssuer) *Middleware {
	return &Middleware{issuer: issuer}
}

// RequireAuth rejects requests without a valid bearer token.
func (m *Middleware) RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := bearerToken(c)
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing bearer token"})
			return
		}
		claims, err := m.issuer.Verify(token)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid or expired token"})
			return
		}
		c.Request = c.Request.WithContext(auth.WithClaims(c.Request.Context(), claims))
		c.Next()
	}
}

// RequireRole rejects requests whose claims lack the given global role.
func (m *Middleware) RequireRole(role domain.RoleGlobal) gin.HandlerFunc {
	return func(c *gin.Context) {
		claims, ok := auth.ClaimsFromContext(c.Request.Context())
		if !ok || !claims.HasRole(role) {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "insufficient role"})
			return
		}
		c.Next()
	}
}

// RequireTenant ensures the request is bound to a tenant and attaches the
// tenant id to the context. Super-admin requests (no tenant) are rejected
// by this middleware — they must use super-admin-specific routes.
func (m *Middleware) RequireTenant() gin.HandlerFunc {
	return func(c *gin.Context) {
		tid, ok := auth.TenantIDFromContext(c.Request.Context())
		if !ok {
			c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": "request is not bound to a tenant"})
			return
		}
		c.Set("tenant_id", tid)
		c.Next()
	}
}

// RequireTenantAdmin rejects requests whose per-tenant role is not tenant_admin.
func (m *Middleware) RequireTenantAdmin() gin.HandlerFunc {
	return func(c *gin.Context) {
		claims, ok := auth.ClaimsFromContext(c.Request.Context())
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
			return
		}
		// Super admins bypass per-tenant role checks.
		if claims.IsSuperAdmin() {
			c.Next()
			return
		}
		if claims.Role != domain.RoleTenantAdmin {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "tenant_admin role required"})
			return
		}
		c.Next()
	}
}

func bearerToken(c *gin.Context) string {
	h := c.GetHeader("Authorization")
	const prefix = "Bearer "
	if !strings.HasPrefix(h, prefix) {
		return ""
	}
	return strings.TrimPrefix(h, prefix)
}
