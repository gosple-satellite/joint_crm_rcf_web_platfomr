package db

import (
	"context"
	"database/sql"
	"fmt"
	"io/fs"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/stdlib"

	"rcf/internal/migrate"
)

// Open opens a *sql.DB for the given Postgres URL, runs migrations, and pings.
func Open(url string) (*sql.DB, error) {
	cfg, err := pgx.ParseConfig(url)
	if err != nil {
		return nil, fmt.Errorf("parse config: %w", err)
	}
	database := stdlib.OpenDB(*cfg)
	database.SetMaxOpenConns(25)
	database.SetMaxIdleConns(5)
	database.SetConnMaxLifetime(5 * time.Minute)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := database.Ping(); err != nil {
		return nil, fmt.Errorf("ping: %w", err)
	}

	// Run migrations idempotently.
	mfs := migrate.Sub()
	files, err := fs.ReadDir(mfs, ".")
	if err != nil {
		return nil, fmt.Errorf("read migrations: %w", err)
	}
	for _, f := range files {
		if f.IsDir() {
			continue
		}
		b, err := fs.ReadFile(mfs, f.Name())
		if err != nil {
			return nil, fmt.Errorf("read %s: %w", f.Name(), err)
		}
		if _, err := database.ExecContext(ctx, string(b)); err != nil {
			return nil, fmt.Errorf("apply %s: %w", f.Name(), err)
		}
	}
	return database, nil
}
