package repository

import (
	"context"
	"database/sql"
	"errors"
	"fmt"

	"github.com/google/uuid"

	"rcf/internal/domain"
)

type UserRepo struct{ db *sql.DB }

func NewUserRepo(db *sql.DB) *UserRepo { return &UserRepo{db: db} }

// Create inserts a user. Returns ErrAlreadyExists on email conflict.
func (r *UserRepo) Create(ctx context.Context, u domain.User) error {
	_, err := r.db.ExecContext(ctx,
		`INSERT INTO users (id, email, password_hash, role, created_at)
		 VALUES ($1, $2, $3, $4, now())`,
		u.ID, u.Email, u.PasswordHash, u.Role,
	)
	if err != nil {
		return fmt.Errorf("insert user: %w", err)
	}
	return nil
}

// GetByID returns a user by id. Returns ErrNotFound if absent.
func (r *UserRepo) GetByID(ctx context.Context, id uuid.UUID) (domain.User, error) {
	row := r.db.QueryRowContext(ctx,
		`SELECT id, email, password_hash, role, created_at FROM users WHERE id = $1`,
		id,
	)
	u, err := scanUser(row)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return domain.User{}, ErrNotFound
		}
		return domain.User{}, err
	}
	return u, nil
}

// GetByEmail returns a user by email (used at login). Returns ErrNotFound if absent.
func (r *UserRepo) GetByEmail(ctx context.Context, email string) (domain.User, error) {
	row := r.db.QueryRowContext(ctx,
		`SELECT id, email, password_hash, role, created_at FROM users WHERE email = $1`,
		email,
	)
	u, err := scanUser(row)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return domain.User{}, ErrNotFound
		}
		return domain.User{}, err
	}
	return u, nil
}

// ExistsByEmail reports whether the email is already taken.
func (r *UserRepo) ExistsByEmail(ctx context.Context, email string) (bool, error) {
	var exists bool
	err := r.db.QueryRowContext(ctx,
		`SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)`, email,
	).Scan(&exists)
	return exists, err
}

func scanUser(row rowScanner) (domain.User, error) {
	var u domain.User
	err := row.Scan(&u.ID, &u.Email, &u.PasswordHash, &u.Role, &u.CreatedAt)
	if err != nil {
		return domain.User{}, fmt.Errorf("scan user: %w", err)
	}
	return u, nil
}
