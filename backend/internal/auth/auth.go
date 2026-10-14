package auth

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"

	"rcf/internal/domain"
)

// DefaultCost is the bcrypt cost used by Hasher.
const DefaultCost = bcrypt.DefaultCost

// contextKey is an unexported type so no other package can collide on context
// keys.
type contextKey string

const (
	claimsKey contextKey = "rcf_claims"
)

// Claims is the JWT payload.
type Claims struct {
	UserID   uuid.UUID         `json:"sub"`
	TenantID uuid.UUID         `json:"tid,omitempty"`
	Role     domain.RoleGlobal `json:"role"`
	jwt.RegisteredClaims
}

// HasRole reports whether the claims carry the given global role.
func (c *Claims) HasRole(r domain.RoleGlobal) bool {
	return c.Role == r
}

// IsSuperAdmin reports whether the user is a super_admin.
func (c *Claims) IsSuperAdmin() bool {
	return c.Role == domain.RoleSuperAdmin
}

// Hasher hashes and verifies passwords using bcrypt.
type Hasher struct {
	cost int
}

// NewHasher returns a Hasher at DefaultCost.
func NewHasher() *Hasher {
	return &Hasher{cost: DefaultCost}
}

// Hash returns a bcrypt hash of password. Empty input is rejected.
func (h *Hasher) Hash(password string) ([]byte, error) {
	if password == "" {
		return nil, errors.New("auth: empty password")
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(password), h.cost)
	if err != nil {
		return nil, fmt.Errorf("bcrypt hash: %w", err)
	}
	return hash, nil
}

// Verify reports whether password matches the stored hash.
func (h *Hasher) Verify(hash, password []byte) error {
	if err := bcrypt.CompareHashAndPassword(hash, password); err != nil {
		if errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
			return ErrMismatchedPassword
		}
		return fmt.Errorf("bcrypt verify: %w", err)
	}
	return nil
}

// ErrMismatchedPassword is returned when a password does not match its hash.
var ErrMismatchedPassword = errors.New("auth: password does not match hash")

// JWTIssuer issues and verifies access tokens.
type JWTIssuer struct {
	secret []byte
	ttl    time.Duration
}

// NewJWTIssuer returns an issuer signed with secret.
func NewJWTIssuer(secret string) *JWTIssuer {
	return &JWTIssuer{secret: []byte(secret), ttl: 15 * time.Minute}
}

// SetTTL configures the default token lifetime.
func (j *JWTIssuer) SetTTL(d time.Duration) *JWTIssuer {
	j.ttl = d
	return j
}

// TTL returns the configured token lifetime.
func (j *JWTIssuer) TTL() time.Duration { return j.ttl }

// Issue returns a token for a user attached to a tenant.
func (j *JWTIssuer) Issue(uid, tid uuid.UUID, role domain.RoleGlobal, ttl time.Duration) (string, error) {
	if ttl <= 0 {
		return "", errors.New("auth: non-positive ttl")
	}
	now := time.Now()
	claims := &Claims{
		UserID:   uid,
		TenantID: tid,
		Role:     role,
		RegisteredClaims: jwt.RegisteredClaims{
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(ttl)),
			Subject:   uid.String(),
		},
	}
	tok, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(j.secret)
	if err != nil {
		return "", fmt.Errorf("sign token: %w", err)
	}
	return tok, nil
}

// IssueSuperAdmin returns a token for a super_admin (no tenant).
func (j *JWTIssuer) IssueSuperAdmin(uid uuid.UUID, ttl time.Duration) (string, error) {
	return j.Issue(uid, uuid.Nil, domain.RoleSuperAdmin, ttl)
}

// IssueExpired returns a token whose expiry is in the past. Used by tests.
func (j *JWTIssuer) IssueExpired(uid, tid uuid.UUID, role domain.RoleGlobal) (string, error) {
	now := time.Now()
	claims := &Claims{
		UserID:   uid,
		TenantID: tid,
		Role:     role,
		RegisteredClaims: jwt.RegisteredClaims{
			IssuedAt:  jwt.NewNumericDate(now.Add(-2 * time.Minute)),
			ExpiresAt: jwt.NewNumericDate(now.Add(-time.Minute)),
		},
	}
	tok, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(j.secret)
	if err != nil {
		return "", fmt.Errorf("sign token: %w", err)
	}
	return tok, nil
}

// Verify parses and validates a token, returning its claims.
func (j *JWTIssuer) Verify(token string) (*Claims, error) {
	claims := &Claims{}
	tok, err := jwt.ParseWithClaims(token, claims, func(t *jwt.Token) (interface{}, error) {
		if t.Method != jwt.SigningMethodHS256 {
			return nil, fmt.Errorf("auth: unexpected signing method %v", t.Method)
		}
		return j.secret, nil
	})
	if err != nil {
		return nil, fmt.Errorf("verify token: %w", err)
	}
	if !tok.Valid {
		return nil, errors.New("auth: invalid token")
	}
	return claims, nil
}

// WithClaims attaches claims to the context.
func WithClaims(ctx context.Context, c *Claims) context.Context {
	return context.WithValue(ctx, claimsKey, c)
}

// ClaimsFromContext returns the claims attached to ctx, if any.
func ClaimsFromContext(ctx context.Context) (*Claims, bool) {
	c, ok := ctx.Value(claimsKey).(*Claims)
	return c, ok
}

// TenantIDFromContext returns the tenant id from ctx.
// Returns (zero, false) for super_admin claims (no tenant) or absent claims.
func TenantIDFromContext(ctx context.Context) (uuid.UUID, bool) {
	c, ok := ClaimsFromContext(ctx)
	if !ok || c.IsSuperAdmin() {
		return uuid.Nil, false
	}
	return c.TenantID, true
}

// UserIDFromContext returns the authenticated user's id from ctx.
func UserIDFromContext(ctx context.Context) (uuid.UUID, bool) {
	c, ok := ClaimsFromContext(ctx)
	if !ok {
		return uuid.Nil, false
	}
	return c.UserID, true
}
