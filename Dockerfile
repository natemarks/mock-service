FROM ubuntu:22.04
ARG COMMIT=38bf5f001335b47c662de233ed648ba0e403a698
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y git
COPY build/38bf5f001335b47c662de233ed648ba0e403a698/linux/amd64/mock-service .
CMD /mock-service
