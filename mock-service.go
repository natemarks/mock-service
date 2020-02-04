package main

// example from
// https://github.com/gin-gonic/examples/blob/master/graceful-shutdown/graceful-shutdown/server.go

import (
	"context"
	"fmt"
	log "github.com/sirupsen/logrus"
	"github.com/toorop/gin-logrus"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	gin "github.com/gin-gonic/gin"
)

const version string = "v0.0.2"

func WaitResponse(w string) string {
	if wait, err := time.ParseDuration(w); err == nil {
		time.Sleep(wait)
		return fmt.Sprintf("You waited for %s", w)
	} else {
		return "Invalid wait parameter example 500ms"
	}
}

func main() {
	grace, err := time.ParseDuration(os.Getenv("SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT"))
	if err != nil {
		grace, _ = time.ParseDuration("5000ms")
	}

	logger := log.New()
	formatter := &log.TextFormatter{
		FullTimestamp: true,
	}
	logger.SetFormatter(formatter)

	// Only log the info severity or above.
	logger.SetLevel(log.InfoLevel)

	// I tried to move this to init() but it doesn't work there
	logger.SetOutput(os.Stdout)
	logger.Info(fmt.Sprintf("mock-service version: %s", version))
	logger.Info(fmt.Sprintf("SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to %s", grace))

	router := gin.Default()
	router.Use(ginlogrus.Logger(logger), gin.Recovery())
	router.GET("/", func(c *gin.Context) {
		q := c.Request.URL.Query()
		c.String(http.StatusOK, WaitResponse(fmt.Sprint(q["wait"][0])))
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	hb_router := gin.Default()
	hb_router.Use(ginlogrus.Logger(logger), gin.Recovery())

	hb_router.GET("/heartbeat", func(c *gin.Context) {
		c.Data(200, "text/plain", []byte("."))
	})

	hb_srv := &http.Server{
		Addr:    ":8786",
		Handler: hb_router,
	}

	go func() {
		// service connections
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("listen: %s\n", err)
		}
	}()

	go func() {
		// service connections
		if err := hb_srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("listen: %s\n", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server with
	// a timeout of 5 seconds.
	quit := make(chan os.Signal, 1)
	// kill (no param) default send syscall.SIGTERM
	// kill -2 is syscall.SIGINT
	// kill -9 is syscall.SIGKILL but can't be catch, so don't need add it
	signal.Notify(quit, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logger.Info("Shutdown Server ...")

	ctx, cancel := context.WithTimeout(context.Background(), grace)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server Shutdown: ", err)
	}
	if err := hb_srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server Shutdown: ", err)
	}

	logger.Info("Graceful shutdown complete")
}
