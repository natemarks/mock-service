.DEFAULT_GOAL := help

# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
DEFAULT_BRANCH := main
THIS_FILE := $(lastword $(MAKEFILE_LIST))
PKG := github.com/natemarks/mock-service
COMMIT := $(shell git rev-parse HEAD)
PKG_LIST := $(shell go list ${PKG}/... | grep -v /vendor/)
GO_FILES := $(shell find . -name '*.go' | grep -v /vendor/)
CDIR = $(shell pwd)
EXECUTABLES := mock-service
GOOS := linux
GOARCH := amd64

CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
DEFAULT_BRANCH := main

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

${EXECUTABLES}:
	@for o in $(GOOS); do \
	  for a in $(GOARCH); do \
        echo "$(COMMIT)/$${o}/$${a}" ; \
        mkdir -p build/$(COMMIT)/$${o}/$${a} ; \
        echo "COMMIT: $(COMMIT)" >> build/$(COMMIT)/$${o}/$${a}/version.txt ; \
        env GOOS=$${o} GOARCH=$${a} \
        go build  -v -o build/$(COMMIT)/$${o}/$${a}/$@ \
				-ldflags="-X github.com/natemarks/mock-service/version.Version=${COMMIT}" ${PKG}/cmd/$@; \
	  done \
    done ; \

build: git-status ${EXECUTABLES}
	rm -f build/current
	ln -s $(CDIR)/build/$(COMMIT) $(CDIR)/build/current


ecr-login: ## login to ecr
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 709310380790.dkr.ecr.us-east-1.amazonaws.com

docker-build: git-status build ecr-login ## create docker image with commit tag
	( \
	   docker build \
	    --build-arg="COMMIT=$(COMMIT)" \
       	-t mock-service:$(COMMIT) \
       	-t 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service \
       	-t 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service:$(COMMIT) \
       	-t 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service:latest \
       	-f Dockerfile .; \
       	docker push 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service:$(COMMIT); \
       	docker push 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service:latest; \
	)
docker-run: ## run the docker container
	docker run -it --rm --publish 8080:8080 709310380790.dkr.ecr.us-east-1.amazonaws.com/mock-service:latest

test:
	@go test -v ${PKG_LIST}
#	@go test -short ${PKG_LIST}

vet:
	@go vet ${PKG_LIST}

goimports: ## check imports
	go install golang.org/x/tools/cmd/goimports@latest
	goimports -w .

lint:  ##  run golint
	go install golang.org/x/lint/golint@latest
	@for file in ${GO_FILES} ;  do \
		golint $$file ; \
	done

fmt: ## run gofmt
	@go fmt ${PKG_LIST}

gocyclo: ## run cyclomatic complexity check
	go install github.com/fzipp/gocyclo/cmd/gocyclo@latest
	gocyclo -over 25 .

godeadcode: ## unreachable code check
	go install golang.org/x/tools/cmd/deadcode@latest
	deadcode -test github.com/natemarks/mock-service/...

govulncheck: # run cyclomatic complexity check
	go install golang.org/x/vuln/cmd/govulncheck@latest
	govulncheck ./...
static: goimports fmt vet lint gocyclo godeadcode govulncheck test

clean:
	-@rm ${OUT} ${OUT}-v*


git-status: ## require status is clean so we can use undo_edits to put things back
	@status=$$(git status --porcelain); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - working directory is dirty. Commit those changes!"; \
		exit 1; \
	fi

.PHONY: build release static vet lint fmt gocyclo goimports test