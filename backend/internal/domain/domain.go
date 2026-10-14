package domain

import (
	"database/sql"
	"time"

	"github.com/google/uuid"
)

// RoleGlobal is the platform-wide role stored on users.role.
type RoleGlobal string

const (
	RoleSuperAdmin  RoleGlobal = "super_admin"
	RoleTenantAdmin RoleGlobal = "tenant_admin"
	RoleEditor      RoleGlobal = "editor"
)

// RoleTenant is the per-tenant role stored on tenant_users.role.
type RoleTenant string

const (
	RoleTAdmin  RoleTenant = "tenant_admin"
	RoleTEditor RoleTenant = "editor"
)

// Status tracks the lifecycle of a tenant.
type Status string

const (
	StatusActive    Status = "active"
	StatusSuspended Status = "suspended"
)

// Tenant is a fellowship (RCF) on the platform.
type Tenant struct {
	ID           uuid.UUID
	Name         string
	Slug         string
	CustomDomain sql.NullString
	Status       Status
	CreatedAt    time.Time
}

// User is a platform user. role is global.
type User struct {
	ID           uuid.UUID
	Email        string
	PasswordHash []byte
	Role         RoleGlobal
	CreatedAt    time.Time
}

// TenantUser links a user to a tenant with a per-tenant role.
type TenantUser struct {
	TenantID  uuid.UUID
	UserID    uuid.UUID
	Role      RoleTenant
	CreatedAt time.Time
}

// NewUUID wraps uuid.New for convenience in tests and handlers.
func NewUUID() uuid.UUID { return uuid.New() }
