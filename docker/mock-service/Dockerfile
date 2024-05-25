FROM ubuntu:22.04
ARG COMMIT
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y git
COPY ../../build/${COMMIT}/linux/amd64/mock-service/bootstrap .
CMD ["/bootstrap"]
