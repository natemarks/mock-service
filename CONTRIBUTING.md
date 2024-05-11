

## automation

run all the local static checks
```bash
make static
```

build the executable
```bash

# make build  builds the executable
# make docker-build builds the docker image
make docker-release # runs make build and make docker-build, then pushes the docker image to ECR
```

run the docker container locally
```bash
make docker-run
```