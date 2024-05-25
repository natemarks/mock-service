# mock-service

The purpose of the mock service is to test deployment methods. It includes the following handy features:
 - a readiness http endpoint. This can also double as a liveness check. For more information about liveness and readiness checks, see https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

```bash
curl -X GET 'http://localhost:8080/ping'
.
```
 - it logs the invocation of a shutdown request AND the successful completion of a graceful shutdown. If the service is killed by a timeout the graceful shutdown success log message will be missing.
 - the 'application' simple waits for teh requested period of time which helps testing graceful shutdown.  If I invoke a 2-minute wait then request a graceful shutdown , I expect to see the log for teh gracfeul shutdown request but NOT the graceful shutdown completion.

```bash
curl -X GET 'http://localhost:8080/?wait=3000ms'
You waited for 3000ms
```

 - logging includes container information where available

 
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


## Logging

mock-service sends JSON logs to the console. An example document looks like this:
```json
{
    "timestamp": "2024-05-13T11:49:47.398851689Z",
    "level": "ERROR",
    "message": "msg here",
    "service": "httplog-example",
    "httpRequest": {
        "url": "http://aeauhjthkf.us-east-1.awsapprunner.com/err",
        "method": "GET",
        "path": "/err",
        "remoteIP": "169.254.175.249:47282",
        "proto": "HTTP/1.1",
        "requestID": "8308f616-ded7-4ccc-89f9-73be375d7714",
        "scheme": "http",
        "header": {
            "x-envoy-expected-rq-timeout-ms": "120000",
            "accept-encoding": "gzip",
            "user-agent": "curl/7.68.0",
            "accept": "*/*",
            "x-envoy-external-address": "73.114.80.122",
            "x-forwarded-for": "73.114.80.122",
            "x-forwarded-proto": "https",
            "x-request-id": "8308f616-ded7-4ccc-89f9-73be375d7714"
        }
    },
    "user": "user1",
    "err": "err here"
}
```

If these logs go to cloudwatch, you can query in cloudwatch logs insights for requests where the path = '/err' like this:
```text
fields @timestamp, @message
| filter httpRequest.path='/err'
```