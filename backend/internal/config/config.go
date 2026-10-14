package config

import (
	"errors"
	"fmt"
	"os"
	"time"
)

// Config holds runtime configuration read from environment variables.
type Config struct {
	DatabaseURL    string
	JWTSecret      string
	Addr           string
	UploadDir      string
	MinIOEndpoint  string
	MinIOAccessKey string
	MinIOSecretKey string
	MinIOBucket    string
}

// Load reads configuration from the environment. It returns an error if a
// required field is missing.
func Load() (*Config, error) {
	c := &Config{
		DatabaseURL:    os.Getenv("RCF_DATABASE_URL"),
		JWTSecret:      os.Getenv("RCF_JWT_SECRET"),
		Addr:           envOrDefault("RCF_ADDR", ":8080"),
		UploadDir:      envOrDefault("RCF_UPLOAD_DIR", "./uploads"),
		MinIOEndpoint:  envOrDefault("RCF_MINIO_ENDPOINT", ""),
		MinIOAccessKey: envOrDefault("RCF_MINIO_ACCESS_KEY", ""),
		MinIOSecretKey: envOrDefault("RCF_MINIO_SECRET_KEY", ""),
		MinIOBucket:    envOrDefault("RCF_MINIO_BUCKET", "rcf"),
	}
	if c.DatabaseURL == "" {
		return nil, errors.New("RCF_DATABASE_URL is required")
	}
	if c.JWTSecret == "" {
		return nil, errors.New("RCF_JWT_SECRET is required")
	}
	if len(c.JWTSecret) < 16 {
		return nil, errors.New("RCF_JWT_SECRET must be at least 16 characters")
	}
	return c, nil
}

// TokenTTL is the access-token lifetime.
func (c *Config) TokenTTL() time.Duration { return 15 * time.Minute }

func envOrDefault(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

// Format returns a human-readable summary of the config (secrets masked).
func (c *Config) Format() string {
	return fmt.Sprintf("addr=%s upload_dir=%s minio=%s bucket=%s", c.Addr, c.UploadDir, c.MinIOEndpoint, c.MinIOBucket)
}
