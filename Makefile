.DEFAULT_GOAL := help

# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
SHELL := $(shell which bash)
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
AWS_ACCOUNT_NUMBER := 709310380790
AWS_REGION := us-east-1
#ARTIFACT_BUCKET := com.imprivata.$(AWS_ACCOUNT_NUMBER).$(AWS_REGION).devops-artifacts
#ARTIFACT_PREFIX := lambda-mock-service
CDK := $(CDIR)/node_modules/.bin/cdk

CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
DEFAULT_BRANCH := main

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

clean-venv: ## re-create virtual env
	[[ -e .venv ]] && rm -rf .venv; \
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python3 -m venv .venv; \
       source .venv/bin/activate; \
       pip install --upgrade pip setuptools; \
       pip install -r requirements.txt; \
    )

.venv: ## create venv if it doesnt exist
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python3 -m venv .venv; \
       source .venv/bin/activate; \
       pip install --upgrade pip setuptools; \
       pip install -r requirements.txt; \
    )

update_cdk_libs: ## install the latest version of aws cdk node and python packages
	bash scripts/update_cdk_libs.sh
	$(MAKE) clean-venv

install_cdk_libs: ## install the project version of aws cdk node and python packages
	bash scripts/update_cdk_libs.sh $(CDK_VERSION)
	$(MAKE) clean-venv

pylint: ## run pylint on python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' | xargs pylint --max-line-length=90; \
    )

black: ## use black to format python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --line-length=79; \
    )

black-check: ## use black to format python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --check --line-length=79; \
    )

${EXECUTABLES}:
	@for o in $(GOOS); do \
	  for a in $(GOARCH); do \
        echo "$(COMMIT)/$${o}/$${a}" ; \
        mkdir -p build/$(COMMIT)/$${o}/$${a}/$@ ; \
        echo "COMMIT: $(COMMIT)" >> build/$(COMMIT)/$${o}/$${a}/$@/version.txt ; \
        env GOOS=$${o} GOARCH=$${a} \
        go build  -v -o build/$(COMMIT)/$${o}/$${a}/$@/bootstrap \
				-ldflags="-X github.com/natemarks/mock-service/version.Version=${COMMIT}" ${PKG}/cmd/$@; \
	  done \
    done ; \

${IMAGES}:
	@for o in $(GOOS); do \
	  for a in $(GOARCH); do \
        echo "$(COMMIT)/$${o}/$${a}" ; \
        mkdir -p build/$(COMMIT)/$${o}/$${a}/$@ ; \
        echo "COMMIT: $(COMMIT)" >> build/$(COMMIT)/$${o}/$${a}/$@/version.txt ; \
        env GOOS=$${o} GOARCH=$${a} \
        go build  -v -o build/$(COMMIT)/$${o}/$${a}/$@/bootstrap \
				-ldflags="-X github.com/natemarks/mock-service/version.Version=${COMMIT}" ${PKG}/cmd/$@; \
	  done \
    done ; \

build: git-status ${EXECUTABLES} ## build the executables
	rm -rf build/current
	cp -R $(CDIR)/build/$(COMMIT) $(CDIR)/build/current

docker-build: build ## build docker images to run the executables
	@for e in ${EXECUTABLES}; do \
	  docker build --no-cache \
		-t $${e}:$(COMMIT) \
		-t $${e}:latest \
		--build-arg COMMIT=$(COMMIT) \
		-f docker/$${e}/Dockerfile .; \
    done ; \

docker-release: docker-build ## push the docker images to ECR
	@for e in ${EXECUTABLES}; do \
  	   aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com; \
	   docker tag $${e}:$(COMMIT) $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/$${e}:$(COMMIT); \
	   docker push $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/$${e}:$(COMMIT); \
	   docker tag $${e}:latest $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/$${e}:latest; \
	   docker push $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/$${e}:latest; \
    done ; \

gotest: ## fgo tests
	@go test -v ${PKG_LIST}
#	@go test -short ${PKG_LIST}

pytest: ## python cdk  tests
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/; \
    )

pytest_update_golden: ## update pytest golden files
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/ --update_golden; \
    )

vet:
	@go vet ${PKG_LIST}

goimports: ## check imports
	find node_modules/ -type f -name "*.go" -exec rm -f {} \;
	go install golang.org/x/tools/cmd/goimports@latest
	goimports -w .

lint:  ##  run golint
	go install golang.org/x/lint/golint@latest
	@for file in ${GO_FILES} ;  do \
		golint $$file ; \
	done

fmt: ## run gofmt
	@go fmt ${PKG_LIST}

gocyclo: # run cyclomatic complexity check
	go install github.com/fzipp/gocyclo/cmd/gocyclo@latest
	gocyclo -over 25 .


godeadcode: # run cyclomatic complexity check
	go install golang.org/x/tools/cmd/deadcode@latest
	deadcode -test github.com/natemarks/mock-service/cmd/...

govulncheck: # run cyclomatic complexity check
	go install golang.org/x/vuln/cmd/govulncheck@latest
	govulncheck ./...

static: node_modules fmt vet lint gocyclo godeadcode govulncheck black pylint shellcheck gotest pytest ## run static checks
clean:
	-@rm ${OUT} ${OUT}-v*


git-status: ## require status is clean so we can use undo_edits to put things back
	@status=$$(git status --porcelain); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - working directory is dirty. Commit those changes!"; \
		exit 1; \
	fi

shellcheck: ## use black to format python files
	( \
       git ls-files '*.sh' |  xargs shellcheck --format=gcc; \
    )

#docker-build: build ## create docker image with commit tag
#	( \
#	   docker build --no-cache \
#       	-t mock-service:$(COMMIT) \
#       	-t mock-service:latest \
#       	-f docker/mock-service/Dockerfile .; \
#	   docker build --no-cache \
#       	-t mock-service:$(COMMIT) \
#       	-t mock-service:latest \
#       	-f docker/mock-service/Dockerfile .; \
#	)

#docker-release: docker-build ## upload the latest docker image to ECR
#	( \
#	   aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com; \
#	   docker tag mock-service:latest $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/mock-service:latest; \
#	   docker push $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/mock-service:latest; \
#	)

docker-push: docker-build ## upload the latest docker image to ECR
	( \
	   aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com; \
	   docker tag ecs_with_cw_logs:latest $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/ecs_with_cw_logs:latest; \
	   docker push $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(AWS_REGION).amazonaws.com/ecs_with_cw_logs:latest; \
	)

docker-run: ## run docker image
	docker run --rm -p 8080:8080 mock-service:$(COMMIT)

node_modules:
	bash scripts/update_cdk_libs.sh $(CDK_VERSION); \
	find node_modules -name "*.go" -exec rm -f {} \; ; \
	$(MAKE) clean-venv

cdk-ls: node_modules ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       cd deployments/cdk ; \
       $(CDK) ls; \
    )

cdk-diff: node_modules ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       cd deployments/cdk ; \
       $(CDK) diff --all; \
    )

cdk-deploy: node_modules ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       cd deployments/cdk ; \
       $(CDK) deploy --all; \
    )

cdk-destroy: node_modules ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       cd deployments/cdk ; \
       $(CDK) destroy $(stack); \
    )


.PHONY: build release static upload vet lint fmt gocyclo goimports test