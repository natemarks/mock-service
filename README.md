# mock-service

The purpose of the mock service is to give devops the simplest possible service that is kubernetes ready so we can test deployment automation, logging etc.:
 - It has liveness and readiness probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
 - It logs startup and graceful vs timeout shutdown
 - It responds to simple request that waits for an arbitrary duration before finishing
 - The service would be run in a container after the preflight check so we have a simple way of testing deploymen
 
 
 # Usage
 
 When I run the mock-service locally, it listens on port 8080 with a graceful shutdown timout htat is either the deafult or a parseable string in the environment variable 'SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT'  example "5000ms".  Any string that is valid for ParseDuration works here (https://golang.org/pkg/time/#example_ParseDuration).
 
 
 
The service should invoke a graceful shutdonw letting eerything finish when a sigterm is caught.  We play with this by killing he service with ctrl-c while tasls are running.  There is a hardcoded  shutdown timeout of 5 seconds :
```text
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
```

this means that if you run a  3 second request and then hit ctrl-c on the server, the client should see  that the request wats for 3 seconds then succeeds
```shell script
curl -X GET 'http://localhost:8080/?wait=3000ms'
You waited for 3000%
```

On the server logs  you should see tsomething like:
```text
2020/02/02 08:32:23 Server Started
^C2020/02/02 08:40:02 Server Stopped
2020/02/02 08:40:02 Server Exited Properly

```

By contrast, if you run a really long request then switch to the server and hist ctrl-c:, the client should see a failed request
```shell script
curl -X GET 'http://localhost:8080/?wait=50000ms'
curl: (52) Empty reply from server
```
 and the server log should look something like:
 ```text

2020/02/02 08:45:17 Server Started
^C2020/02/02 08:45:22 Server Stopped
2020/02/02 08:45:27 Server Shutdown Failed:context deadline exceeded

```

## Usage
curl -X GET 'http://localhost:8080/?wait=5000ms'

(the response takes 5000 milliseconds)
You waited for 5000ms%

if you create a long running requests (say 50 seconds)
