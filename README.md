# mock-service

The purpose of the mock service is to give devops the simplest possible service that is kubernetes ready so we can test deployment automation, logging etc.:
 - It has liveness and readiness probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
 - It logs startup and graceful vs timeout shutdown
 - It responds to simple request that waits for an arbitrary duration before finishing
 
 
 # Usage
 
 When I run the mock-service locally, it listens on port 8080 with a graceful shutdown timout htat is either the default or a parsable string in the environment variable 'SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT'  example "5000ms".  Any string that is valid for ParseDuration works here (https://golang.org/pkg/time/#example_ParseDuration).
 
 Fomr a client, I can run:
 ```shell script
 curl -X GET 'http://localhost:8080/?wait=3000ms'
#  the service waits for 3000ms before responding
 You waited for 3000%
 ```
 This wait is important because it lets us test our graceful shutdown. If my SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5000ms and I initiate a 3000ms request, then CTRL-C th service immediately:
  - the service should stop taking new requests (this applies to / and to /heartbeat, so a load balancer could take it out of service right away)
  - the service would wait for the request to finish, which take 3000ms, then it would exit with a log message indicating that graceful shutdown had completed.  This is REALLY important for any service because we know that the lifecycle automation didn't kill the service, the service gracefully closed out.
  
  The service logs should look something like this. Note that you see the ^C BEFORE the 3000ms request completes and the Graceful Shutdown Complete message at the end
  ```text
./mock-service 
INFO[2020-02-03T04:48:46-05:00] SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5s 
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] GET    /                         --> main.main.func1 (5 handlers)
[GIN-debug] GET    /heartbeat                --> main.main.func2 (5 handlers)
^CINFO[2020-02-03T04:48:53-05:00] Shutdown Server ...                          
INFO[2020-02-03T04:48:55-05:00] ::1 - Nathans-MacBook-Pro.local [03/Feb/2020:04:48:55 -0500] "GET /" 200 21 "" "curl/7.54.0" (3003ms)  clientIP="::1" dataLength=21 hostname=Nathans-MacBook-Pro.local latency=3003 method=GET path=/ referer= statusCode=200 userAgent=curl/7.54.0
[GIN] 2020/02/03 - 04:48:55 | 200 |  3.002922732s |             ::1 | GET      /?wait=3000ms
INFO[2020-02-03T04:48:55-05:00] Graceful shutdown complete          
```
  

Alternatively, if I initiate a 50 second request and CTRL-C the service, it should wait for the 5 second SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT period , then forceitself closed.  Critically, it should log that it closed by timeout rather than gracefully because that tells us one or more transaction may have failed because of the service shutting down.
 
 The log should look something like this. NOTE the 'context deadline exceeded'  final message rather than the Graceful shutdown:
 ```text
 ./mock-service 
INFO[2020-02-03T04:50:42-05:00] SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5s 
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] GET    /                         --> main.main.func1 (5 handlers)
[GIN-debug] GET    /heartbeat                --> main.main.func2 (5 handlers)
^CINFO[2020-02-03T04:50:52-05:00] Shutdown Server ...                          
FATA[2020-02-03T04:50:57-05:00] Server Shutdown: context deadline exceeded 
```


## Heartbeat
This is an example of the heartbeat test. I should probably move this to a different port.  we usually us 8786
```shell script
curl -X GET 'http://localhost:8080/heartbeat'
.%
```

## Liveness

I like the idea of using a mock-service subcommand for this. I'll add it.:
https://medium.com/over-engineering/graceful-shutdown-with-go-http-servers-and-kubernetes-rolling-updates-6697e7db17cf