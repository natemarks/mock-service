package main

import (
	"context"
	"errors"
	"fmt"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/httplog/v2"
	"github.com/natemarks/mock-service/version"
	"log"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	port = 8080
)

// WaitResponse waits for a specified duration and returns a string
func WaitResponse(w string) (response string, err error) {
	if wait, err := time.ParseDuration(w); err == nil {
		time.Sleep(wait)
		return fmt.Sprintf("You waited for %s", w), err
	}
	return fmt.Sprintf("invalid input: %s. try /?wait=200ms", w), err

}

func main() {

	// Listen for SIGINT signal
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)

	grace, err := time.ParseDuration(os.Getenv("SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT"))
	if err != nil {
		grace, _ = time.ParseDuration("5000ms")
	}

	// Logger
	logger := httplog.NewLogger("mock-service", httplog.Options{
		JSON:             true,
		LogLevel:         slog.LevelDebug,
		Concise:          true,
		RequestHeaders:   true,
		MessageFieldName: "message",
		// TimeFieldFormat: time.RFC850,
		Tags: map[string]string{
			"version": version.Version,
			"env":     "dev",
		},
		QuietDownRoutes: []string{
			"/",
			"/ping",
		},
		QuietDownPeriod: 10 * time.Second,
		// SourceFieldName: "source",
	})

	// Service
	r := chi.NewRouter()
	r.Use(httplog.RequestLogger(logger))
	r.Use(middleware.Heartbeat("/ping"))

	r.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ctx := r.Context()
			httplog.LogEntrySetField(ctx, "user", slog.StringValue("user1"))
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	})

	r.Get("/", func(w http.ResponseWriter, r *http.Request) {
		waitParam := r.URL.Query().Get("wait")
		waitResponse, err := WaitResponse(waitParam)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte(waitResponse))
			return
		}
		w.Write([]byte(waitResponse))
	})

	r.Get("/version", func(w http.ResponseWriter, r *http.Request) {
		response := fmt.Sprintf("version: %s", version.Version)
		oplog := httplog.LogEntry(r.Context())
		w.Header().Add("Content-Type", "text/plain")
		oplog.Info(response)
		w.Write([]byte(response))
	})

	// Create a server with custom settings
	srv := &http.Server{
		Addr:    ":8080",
		Handler: r,
	}

	go func() {
		logger.Info(fmt.Sprintf("starting server (%s) on port %d", version.Version, port))
		logger.Info(fmt.Sprintf("SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to %s", grace))

		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("Could not listen on :%d: %v\n", port, err)
		}
	}()
	// Block until a signal is received
	sig := <-stop
	logger.Info(fmt.Sprintf("Received signal: %s. Shutting down gracefully...", sig))

	// Create a context with a timeout
	ctx, cancel := context.WithTimeout(context.Background(), grace)
	defer cancel()

	// Shutdown the server
	if err := srv.Shutdown(ctx); err != nil {
		logger.Error(fmt.Sprintf("Server shutdown error: %v", err))
	} else {
		logger.Info("Server shutdown successful")
	}

}
