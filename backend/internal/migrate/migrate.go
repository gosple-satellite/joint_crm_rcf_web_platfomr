package migrate

import (
	"embed"
	"io/fs"
)

// FS holds the embedded SQL migrations.
//
//go:embed migrations/*.sql
var FS embed.FS

// Sub returns the migrations sub-filesystem rooted at "migrations".
func Sub() fs.FS {
	s, err := fs.Sub(FS, "migrations")
	if err != nil {
		panic(err)
	}
	return s
}
