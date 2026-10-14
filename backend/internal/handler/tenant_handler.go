package handler

import (
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"rcf/internal/auth"
	"rcf/internal/domain"
	"rcf/internal/service"
)

// TenantHandler exposes tenant HTTP endpoints.
type TenantHandler struct {
	svc    *service.TenantService
	issuer *auth.JWTIssuer
	ttl    time.Duration
}

func NewTenantHandler(svc *service.TenantService, issuer *auth.JWTIssuer, ttl time.Duration) *TenantHandler {
	return &TenantHandler{svc: svc, issuer: issuer, ttl: ttl}
}

// CreateTenant handles POST /api/v1/tenants (super_admin only).
func (h *TenantHandler) CreateTenant(c *gin.Context) {
	var req struct {
		Name          string `json:"name" binding:"required"`
		Slug          string `json:"slug" binding:"required"`
		AdminEmail    string `json:"admin_email" binding:"required,email"`
		AdminPassword string `json:"admin_password" binding:"required,min=8"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	req.Slug = strings.ToLower(strings.TrimSpace(req.Slug))

	ten, admin, err := h.svc.CreateTenant(c.Request.Context(), req.Name, req.Slug, req.AdminEmail, req.AdminPassword)
	if err != nil {
		if err == service.ErrSlugTaken {
			c.JSON(http.StatusConflict, gin.H{"error": "slug already taken"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
		return
	}

	// Issue a token for the newly created tenant admin so they can start
	// using the platform immediately.
	tok, err := h.issuer.Issue(admin.ID, ten.ID, domain.RoleTenantAdmin, h.issuer.TTL())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"tenant": toTenantDTO(ten),
		"admin":  toUserDTO(admin),
		"token":  tok,
	})
}

// ListTenants handles GET /api/v1/tenants (super_admin only).
func (h *TenantHandler) ListTenants(c *gin.Context) {
	tenants, err := h.svc.ListTenants(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
		return
	}
	out := make([]tenantDTO, 0, len(tenants))
	for _, t := range tenants {
		out = append(out, toTenantDTO(t))
	}
	c.JSON(http.StatusOK, gin.H{"tenants": out})
}

// GetTenant handles GET /api/v1/tenants/:id (super_admin only).
func (h *TenantHandler) GetTenant(c *gin.Context) {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid tenant id"})
		return
	}
	t, err := h.svc.GetTenant(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "tenant not found"})
		return
	}
	c.JSON(http.StatusOK, toTenantDTO(t))
}

// SetStatus handles PATCH /api/v1/tenants/:id/status (super_admin only).
func (h *TenantHandler) SetStatus(c *gin.Context) {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid tenant id"})
		return
	}
	var req struct {
		Status string `json:"status" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	status := domain.Status(req.Status)
	if status != domain.StatusActive && status != domain.StatusSuspended {
		c.JSON(http.StatusBadRequest, gin.H{"error": "status must be active or suspended"})
		return
	}
	if err := h.svc.SetStatus(c.Request.Context(), id, status); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "tenant not found"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": string(status)})
}

type tenantDTO struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Slug         string `json:"slug"`
	CustomDomain string `json:"custom_domain,omitempty"`
	Status       string `json:"status"`
}

type userDTO struct {
	ID    string `json:"id"`
	Email string `json:"email"`
	Role  string `json:"role"`
}

func toTenantDTO(t domain.Tenant) tenantDTO {
	cd := ""
	if t.CustomDomain.Valid {
		cd = t.CustomDomain.String
	}
	return tenantDTO{
		ID:           t.ID.String(),
		Name:         t.Name,
		Slug:         t.Slug,
		CustomDomain: cd,
		Status:       string(t.Status),
	}
}

func toUserDTO(u domain.User) userDTO {
	return userDTO{ID: u.ID.String(), Email: u.Email, Role: string(u.Role)}
}
