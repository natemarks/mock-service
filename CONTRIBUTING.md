

## automation

run all the local static checks
```bash
make static
```

build the executable
```bash

make build
```


build the docker image and push it to ECR
```bash
make  docker-build
```

run the docker container locally
```bash
make docker-run
```