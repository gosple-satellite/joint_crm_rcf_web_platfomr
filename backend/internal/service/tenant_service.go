package service

import (
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"

	"rcf/internal/domain"
	"rcf/internal/repository"
)

// hasher abstracts password hashing so the service is testable without a
// real bcrypt cost. In production the concrete auth.Hasher is passed in.
type hasher interface {
	Hash(password string) ([]byte, error)
}

// TenantService orchestrates tenant operations. It is pure: no HTTP, no
// context extraction — callers pass explicit ids.
type TenantService struct {
	tenRepo  *repository.TenantRepo
	tenUser  *repository.TenantUserRepo
	userRepo *repository.UserRepo
	hasher   hasher
}

func NewTenantService(
	tenRepo *repository.TenantRepo,
	tenUser *repository.TenantUserRepo,
	userRepo *repository.UserRepo,
	h hasher,
) *TenantService {
	return &TenantService{tenRepo: tenRepo, tenUser: tenUser, userRepo: userRepo, hasher: h}
}

// CreateTenant creates a tenant and an admin user for it.
// Returns ErrSlugTaken if the slug is already used.
func (s *TenantService) CreateTenant(ctx context.Context, name, slug, adminEmail, adminPassword string) (domain.Tenant, domain.User, error) {
	var zero domain.Tenant
	var zu domain.User
	if name == "" || slug == "" {
		return zero, zu, errors.New("service: name and slug are required")
	}
	if adminEmail == "" || adminPassword == "" {
		return zero, zu, errors.New("service: admin email and password are required")
	}

	// Pre-check slug so we can return a clean sentinel error instead of a
	// wrapped postgres unique-violation.
	if _, err := s.tenRepo.GetBySlug(ctx, slug); err == nil {
		return zero, zu, ErrSlugTaken
	} else if !errors.Is(err, repository.ErrNotFound) {
		return zero, zu, fmt.Errorf("check slug: %w", err)
	}

	ten := domain.Tenant{
		ID:     uuid.New(),
		Name:   name,
		Slug:   slug,
		Status: domain.StatusActive,
	}
	if err := s.tenRepo.Create(ctx, ten); err != nil {
		return zero, zu, fmt.Errorf("create tenant: %w", err)
	}

	hash, err := s.hasher.Hash(adminPassword)
	if err != nil {
		return zero, zu, fmt.Errorf("hash admin password: %w", err)
	}
	admin := domain.User{
		ID:           uuid.New(),
		Email:        adminEmail,
		PasswordHash: hash,
		Role:         domain.RoleTenantAdmin,
	}
	if err := s.userRepo.Create(ctx, admin); err != nil {
		return zero, zu, fmt.Errorf("create admin user: %w", err)
	}

	if err := s.tenUser.Add(ctx, ten.ID, admin.ID, domain.RoleTAdmin); err != nil {
		return zero, zu, fmt.Errorf("link admin to tenant: %w", err)
	}

	return ten, admin, nil
}

// ListTenants returns all tenants.
func (s *TenantService) ListTenants(ctx context.Context) ([]domain.Tenant, error) {
	return s.tenRepo.List(ctx)
}

// GetTenant returns a tenant by id.
func (s *TenantService) GetTenant(ctx context.Context, id uuid.UUID) (domain.Tenant, error) {
	t, err := s.tenRepo.GetByID(ctx, id)
	if err != nil {
		return domain.Tenant{}, fmt.Errorf("get tenant: %w", err)
	}
	return t, nil
}

// SetStatus updates a tenant's status.
func (s *TenantService) SetStatus(ctx context.Context, id uuid.UUID, status domain.Status) error {
	return s.tenRepo.SetStatus(ctx, id, status)
}

// ErrSlugTaken is returned when a slug is already in use.
var ErrSlugTaken = errors.New("service: slug is already taken")
