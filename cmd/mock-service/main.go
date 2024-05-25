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
	port = "8080"
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

	// Graceful shutdown timeout
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

	// Configure Web Server
	r := chi.NewRouter()
	r.Use(httplog.RequestLogger(logger))

	// curl -X GET 'http://localhost:8080/ping'
	r.Use(middleware.Heartbeat("/ping"))

	// Add a version field to the log entry
	r.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ctx := r.Context()
			httplog.LogEntrySetField(ctx, "version", slog.StringValue(version.Version))
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	})

	// curl -X GET 'http://localhost:8080/?wait=20000ms'
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

	// curl -X GET 'http://localhost:8080/version
	r.Get("/version", func(w http.ResponseWriter, r *http.Request) {
		response := fmt.Sprintf("version: %s", version.Version)
		oplog := httplog.LogEntry(r.Context())
		w.Header().Add("Content-Type", "text/plain")
		oplog.Info(response)
		w.Write([]byte(response))
	})

	// Create a server with custom settings
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%s", port),
		Handler: r,
	}

	// Listen for SIGINT signal
	// NOTE: Dockerfile CMD MUST use the correct form of the command to send the SIGTERM to the process
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)

	// Start the server in a goroutine
	go func() {
		logger.Info(fmt.Sprintf("starting server (%s) on port %s", version.Version, port))
		logger.Info(fmt.Sprintf("SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to %s", grace))

		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("Could not listen on :%s: %v\n", port, err)
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
