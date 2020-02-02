package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
)

type Server struct {
	logger *log.Logger
	mux    *http.ServeMux
}

func NewServer(options ...func(*Server)) *Server {
	s := &Server{
		logger: log.New(os.Stdout, "", 0),
		mux:    http.NewServeMux(),
	}

	for _, f := range options {
		f(s)
	}

	s.mux.HandleFunc("/", s.index)

	return s
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.mux.ServeHTTP(w, r)
}

func (s *Server) index(w http.ResponseWriter, r *http.Request) {
	s.logger.Println("GET /")
	q := r.URL.Query()
	_, _ = w.Write([]byte(WaitResponse(fmt.Sprint(q["wait"][0]))))
}

func WaitResponse(w string) string {
	if wait, err := time.ParseDuration(w); err == nil {
		time.Sleep(wait)
		return fmt.Sprintf("You waited for %s", w)
	} else {
		return "Invalid wait parameter example 500ms"
	}
}

func main() {
	stop := make(chan os.Signal, 1)

	signal.Notify(stop, os.Interrupt)

	logger := log.New(os.Stdout, "", 0)

	addr := ":" + os.Getenv("PORT")
	if addr == ":" {
		addr = ":2017"
	}

	s := NewServer(func(s *Server) { s.logger = logger })

	h := &http.Server{Addr: addr, Handler: s}

	go func() {
		logger.Printf("Listening on http://0.0.0.0%s\n", addr)

		if err := h.ListenAndServe(); err != nil {
			logger.Fatal(err)
		}
	}()

	<-stop

	logger.Println("\nShutting down the server...")

	ctx, _ := context.WithTimeout(context.Background(), 5*time.Second)

	_ = h.Shutdown(ctx)

	logger.Println("Server gracefully stopped")
}
