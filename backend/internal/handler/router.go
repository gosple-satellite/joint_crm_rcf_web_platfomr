package handler

import (
	"database/sql"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"

	"rcf/internal/auth"
	"rcf/internal/config"
	"rcf/internal/db"
	"rcf/internal/domain"
	"rcf/internal/repository"
	"rcf/internal/service"
)

// Router wires up all HTTP routes.
type Router struct {
	gin *gin.Engine
	cfg *config.Config
}

// NewRouter constructs a fully wired router from config.
func NewRouter(cfg *config.Config) *Router {
	database, err := db.Open(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("open database: %v", err)
	}
	return newRouterWithDB(cfg, database)
}

// newRouterWithDB builds a router from an existing *sql.DB. Used by tests.
func newRouterWithDB(cfg *config.Config, database *sql.DB) *Router {
	g := gin.New()
	g.Use(gin.Recovery(), gin.Logger())

	tenRepo := repository.NewTenantRepo(database)
	tenUserRepo := repository.NewTenantUserRepo(database)
	userRepo := repository.NewUserRepo(database)

	issuer := auth.NewJWTIssuer(cfg.JWTSecret).SetTTL(cfg.TokenTTL())
	mw := NewMiddleware(issuer)

	svc := service.NewTenantService(tenRepo, tenUserRepo, userRepo, auth.NewHasher())
	tenantH := NewTenantHandler(svc, issuer, cfg.TokenTTL())

	r := &Router{gin: g, cfg: cfg}

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

	return r
}

// Engine returns the underlying gin engine.
func (r *Router) Engine() *gin.Engine { return r.gin }

// Run starts the HTTP server.
func (r *Router) Run() error {
	return r.gin.Run(r.cfg.Addr)
}
