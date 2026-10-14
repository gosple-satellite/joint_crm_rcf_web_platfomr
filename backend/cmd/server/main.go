package main

import (
	"log"

	"rcf/internal/config"
	"rcf/internal/handler"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config: %v", err)
	}
	log.Printf("rcf starting: %s", cfg.Format())

	r := handler.NewRouter(cfg)
	if err := r.Run(); err != nil {
		log.Fatalf("server: %v", err)
	}
}
