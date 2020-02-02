package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func WaitResponse(w string) string {
	if wait, err := time.ParseDuration(w); err == nil {
		time.Sleep(wait)
		return fmt.Sprintf("You waited for %s", w)
	} else {
		return "Invalid wait parameter example 500ms"
	}
}
func TestEndpoint(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(200)
	q := r.URL.Query()
	_, _ = w.Write([]byte(WaitResponse(fmt.Sprint(q["wait"][0]))))
}

func main() {
	m := http.NewServeMux()

	srv := http.Server{Addr: ":8080", Handler: m}
	m.HandleFunc("/", TestEndpoint)

	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()
	log.Print("Server Started")

	<-done
	log.Print("Server Stopped")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer func() {
		// extra handling here
		cancel()
	}()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server Shutdown Failed:%+v", err)
	}
	log.Print("Server Exited Properly")
}
