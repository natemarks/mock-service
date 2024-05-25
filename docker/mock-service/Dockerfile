FROM ubuntu:22.04
ARG COMMIT
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y git
COPY ../../build/${COMMIT}/linux/amd64/mock-service/bootstrap .
# NOTE: CMD /bootstrap will start the app BUT SIGTERM freom docker stop will not make it to the app
#  use CMD exec /bootstrap OR CMD ["/bootstrap"] to make sure the signal is passed to the app
CMD ["/bootstrap"]
