package handler

import (
	"errors"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"

	"rcf/internal/auth"
	"rcf/internal/domain"
	"rcf/internal/repository"
)

type loginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
	Tenant   string `json:"tenant" binding:"required"` // slug or id
}

// hLogin handles POST /api/v1/auth/login.
func hLogin(tenRepo *repository.TenantRepo, userRepo *repository.UserRepo, issuer *auth.JWTIssuer, ttl time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req loginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		req.Tenant = strings.ToLower(strings.TrimSpace(req.Tenant))

		// Resolve tenant by slug or uuid.
		tenant, err := tenRepo.GetBySlugOrID(c.Request.Context(), req.Tenant)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "tenant not found"})
			return
		}

		user, err := userRepo.GetByEmail(c.Request.Context(), req.Email)
		if err != nil {
			if errors.Is(err, repository.ErrNotFound) {
				c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		if err := auth.NewHasher().Verify(user.PasswordHash, []byte(req.Password)); err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
			return
		}

		// Confirm the user is actually a member of this tenant.
		tenUserRepo := repository.NewTenantUserRepo(tenRepo.DB())
		isMember, err := tenUserRepo.IsMember(c.Request.Context(), tenant.ID, user.ID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}
		if !isMember {
			c.JSON(http.StatusForbidden, gin.H{"error": "user is not a member of this tenant"})
			return
		}

		// Determine per-tenant role for the token.
		members, err := tenUserRepo.ListByTenant(c.Request.Context(), tenant.ID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}
		var role domain.RoleTenant
		for _, m := range members {
			if m.UserID == user.ID {
				role = m.Role
				break
			}
		}
		if role == "" {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		tok, err := issuer.Issue(user.ID, tenant.ID, roleToGlobal(role), ttl)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"token": tok,
			"user": gin.H{
				"id":    user.ID.String(),
				"email": user.Email,
				"role":  string(role),
			},
		})
	}
}

func roleToGlobal(r domain.RoleTenant) domain.RoleGlobal {
	switch r {
	case domain.RoleTAdmin:
		return domain.RoleTenantAdmin
	case domain.RoleTEditor:
		return domain.RoleEditor
	default:
		return domain.RoleEditor
	}
}
