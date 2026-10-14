package testutil

import (
	"context"
	"database/sql"
	"fmt"
	"io/fs"
	"os"
	"strings"
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/stdlib"

	"rcf/internal/domain"
	"rcf/internal/migrate"
)

// ConnStr returns a Postgres connection string for the test database.
// It reads RCF_TEST_DATABASE_URL; falls back to a local default.
func ConnStr(t *testing.T) string {
	t.Helper()
	url := os.Getenv("RCF_TEST_DATABASE_URL")
	if url == "" {
		url = "postgres://postgres:postgres@localhost:5432/rcf_test?sslmode=disable"
	}
	return url
}

// RunMigrations applies every migration under internal/migrate in order.
func RunMigrations(ctx context.Context, db *sql.DB) error {
	mfs := migrate.Sub()
	files, err := fs.ReadDir(mfs, ".")
	if err != nil {
		return fmt.Errorf("read migrations: %w", err)
	}
	for _, f := range files {
		if f.IsDir() {
			continue
		}
		b, err := fs.ReadFile(mfs, f.Name())
		if err != nil {
			return fmt.Errorf("read %s: %w", f.Name(), err)
		}
		if _, err := db.ExecContext(ctx, string(b)); err != nil {
			return fmt.Errorf("apply %s: %w", f.Name(), err)
		}
	}
	return nil
}

// NewTenant creates a tenant row for tests and returns it.
func NewTenant(t *testing.T, name, slug string) domain.Tenant {
	t.Helper()
	return domain.Tenant{
		ID:           uuid.New(),
		Name:         name,
		Slug:         slug,
		CustomDomain: sql.NullString{Valid: false},
		Status:       domain.StatusActive,
	}
}

// TruncateAll wipes tenant-scoped tables so each test starts clean.
func TruncateAll(ctx context.Context, db *sql.DB) error {
	_, err := db.ExecContext(ctx,
		`TRUNCATE tenant_users, users, tenants CASCADE`,
	)
	return err
}

// NewUser creates a user row for tests and returns it.
func NewUser(t *testing.T, email string, role domain.RoleGlobal) domain.User {
	t.Helper()
	return domain.User{
		ID:           uuid.New(),
		Email:        email,
		PasswordHash: []byte("test-hash"),
		Role:         role,
	}
}

// ResetTestDB gives the calling test its own schema, applies migrations into
// it, and drops it on cleanup.
//
// One shared database does not work: go test runs packages in parallel, so
// repository, service and handler would truncate each other mid-test. A
// per-test schema isolates across packages and across tests at once.
func ResetTestDB(t *testing.T) *sql.DB {
	t.Helper()
	schema := "test_" + strings.ReplaceAll(uuid.NewString(), "-", "")

	cfg, err := pgx.ParseConfig(ConnStr(t))
	if err != nil {
		t.Fatalf("parse test db config: %v", err)
	}
	cfg.RuntimeParams["search_path"] = schema

	db := stdlib.OpenDB(*cfg)
	ctx := context.Background()
	if _, err := db.ExecContext(ctx, `CREATE SCHEMA IF NOT EXISTS `+schema); err != nil {
		db.Close()
		t.Fatalf("create schema: %v", err)
	}
	if err := db.Ping(); err != nil {
		db.Close()
		t.Fatalf("ping test db: %v", err)
	}

	t.Cleanup(func() {
		// Drop on a bare connection: this pool has search_path set to the
		// schema we are about to remove.
		drop, err := pgx.Connect(context.Background(), ConnStr(t))
		if err == nil {
			_, _ = drop.Exec(context.Background(), `DROP SCHEMA IF EXISTS `+schema+` CASCADE`)
			_ = drop.Close(context.Background())
		}
		db.Close()
	})

	if err := RunMigrations(ctx, db); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	return db
}

// OpenTestDB opens the shared test database with no schema isolation. Only
// for tests that genuinely need it; prefer ResetTestDB.
func OpenTestDB(t *testing.T) *sql.DB {
	t.Helper()
	cfg, err := pgx.ParseConfig(ConnStr(t))
	if err != nil {
		t.Fatalf("parse test db config: %v", err)
	}
	db := stdlib.OpenDB(*cfg)
	if err := db.Ping(); err != nil {
		t.Fatalf("ping test db: %v", err)
	}
	return db
}
