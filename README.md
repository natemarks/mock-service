# mock-service

The purpose of the mock service is to test deployment methods. It includes the following handy features:

 - a readiness http endpoint. This can also double as a liveness check. For more information about liveness and readiness checks, see https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

```bash
curl -X GET 'http://localhost:8080/ping'
.
```

 - a version endpoint. This is useful to confirm the version of the service that is running after a deployment.

```bash
curl -X GET 'http://localhost:8080/version'
version: 1c06d9400c27e035cc53fa598a9a150dd838ca02
```

- graceful shutdown logging: logs the invocation of OS interrupt, SIGINT or SIGTERM AND logs the result of the graceful shutdown request. The service will wait for the SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT before forcing a shutdown and throwing a deadline exceeded error.  If the service gracefully shuts down before the timeout, the log message will indicate graceful shutdown success.  This is useful in guaging whether the service is waiting for all transactions to complete before shutting down.

 - the application waits for a requested period of time. This is useful for testing graceful shutdown because it synthesizes a long-running request.  If I invoke a 2-minute wait then request a graceful shutdown, the logs should show the graceful shutdown request and the deadline exceeded error log message for the graceful shutdown. If the wait is short enough, the graceful shutdown will succeed.

```bash
curl -X GET 'http://localhost:8080/?wait=3000ms'
You waited for 3000ms
```

 # Usage
If you just run the service and hit CTRL-C right awayyou should see the service start and graceful shutdown messages. Note that the app caught the os.interrupt  and invoked the graceful shutdown.  In the next message , the graceful shutdown succeeded.

```bash
./build/current/linux/amd64/mock-service/bootstrap 
{"timestamp":"2024-05-25T09:08:33.225023318-04:00","level":"INFO","message":"starting server (1c06d9400c27e035cc53fa598a9a150dd838ca02) on port 8080","service":"mock-service"}
{"timestamp":"2024-05-25T09:08:33.225119143-04:00","level":"INFO","message":"SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5s","service":"mock-service"}
^C{"timestamp":"2024-05-25T09:08:35.103887287-04:00","level":"INFO","message":"Received signal: interrupt. Shutting down gracefully...","service":"mock-service"}
{"timestamp":"2024-05-25T09:08:35.104055853-04:00","level":"INFO","message":"Server shutdown successful","service":"mock-service"}
```


If I run the service in one window:
```bash
./build/current/linux/amd64/mock-service/bootstrap 
{"timestamp":"2024-05-25T09:11:31.342163452-04:00","level":"INFO","message":"starting server (1c06d9400c27e035cc53fa598a9a150dd838ca02) on port 8080","service":"mock-service"}
{"timestamp":"2024-05-25T09:11:31.342271604-04:00","level":"INFO","message":"SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5s","service":"mock-service"}
```

I see the startup messages.  Now I run a long app request (20 seconds) in another window:
```bash
curl -X GET 'http://localhost:8080/?wait=20000ms'
curl: (52) Empty reply from server
```

Then I hit CTRL-C in the first window:
```bash
./build/current/linux/amd64/mock-service/bootstrap 
{"timestamp":"2024-05-25T09:11:31.342163452-04:00","level":"INFO","message":"starting server (1c06d9400c27e035cc53fa598a9a150dd838ca02) on port 8080","service":"mock-service"}
{"timestamp":"2024-05-25T09:11:31.342271604-04:00","level":"INFO","message":"SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 5s","service":"mock-service"}
^C{"timestamp":"2024-05-25T09:12:10.603757366-04:00","level":"INFO","message":"Received signal: interrupt. Shutting down gracefully...","service":"mock-service"}
{"timestamp":"2024-05-25T09:12:15.604280845-04:00","level":"ERROR","message":"Server shutdown error: context deadline exceeded","service":"mock-service"}
```
The service waited for the graceful shutdown timeout (5 seconds), then it shut down before the 20-second request could finish.  The log message indicates that the shutdown was by timeout rather than graceful shutdown.  This is important because it tells us that one or more transactions may have failed because of the service shutting down.


While the server is executing a graceful shutdown, it should not accept new requests. 

In window 1, I give myself 30 seconds for the graceful shutdown because I'm slow :D

```bash
SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT=30000ms ./build/current/linux/amd64/mock-service/bootstrap 
{"timestamp":"2024-05-25T09:15:36.472362667-04:00","level":"INFO","message":"starting server (1c06d9400c27e035cc53fa598a9a150dd838ca02) on port 8080","service":"mock-service"}
{"timestamp":"2024-05-25T09:15:36.472453234-04:00","level":"INFO","message":"SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 30s","service":"mock-service"}
```
In window 2, I run a 20-second request to hold open the graceful shutdown period. This will succeed because of the 30 seconds graceful shutdown in window 1
```bash
curl -X GET 'http://localhost:8080/?wait=20000ms'
You waited for 20000ms
```

In window 1, I hit CTRL-C. now the service is in a graceful shutdown period.  It will wait for 30 seconds before shutting down.  The 20-second request will complete before the service shuts down.
```bash
^C{"timestamp":"2024-05-25T09:16:19.404623659-04:00","level":"INFO","message":"Received signal: interrupt. Shutting down gracefully...","service":"mock-service"}
```

In window 3 I test the server response while it is in the graceful shutdown period.  It should be refused.
```bash
curl -X GET 'http://localhost:8080/?wait=2000ms'
curl: (7) Failed to connect to localhost port 8080: Connection refused
```

Finally, the 20-second request completes and the service shuts down.
```bash
SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT=30000ms ./build/current/linux/amd64/mock-service/bootstrap 
{"timestamp":"2024-05-25T09:15:36.472362667-04:00","level":"INFO","message":"starting server (1c06d9400c27e035cc53fa598a9a150dd838ca02) on port 8080","service":"mock-service"}
{"timestamp":"2024-05-25T09:15:36.472453234-04:00","level":"INFO","message":"SERVICE_GRACEFUL_SHUTDOWN_TIMEOUT is set to 30s","service":"mock-service"}
{"timestamp":"2024-05-25T09:16:14.874567511-04:00","level":"INFO","message":"Response: 200 OK","service":"mock-service","httpRequest":{"url":"http://localhost:8080/?wait=2000ms","method":"GET","path":"/","remoteIP":"127.0.0.1:41900","proto":"HTTP/1.1","requestID":"nmarks-lenovo/Zv7ai8mSzM-000001","scheme":"http","header":{"user-agent":"curl/7.68.0","accept":"*/*"}},"user":"user1","httpResponse":{"status":200,"bytes":21,"elapsed":2001.109461}}
^C{"timestamp":"2024-05-25T09:16:19.404623659-04:00","level":"INFO","message":"Received signal: interrupt. Shutting down gracefully...","service":"mock-service"}
{"timestamp":"2024-05-25T09:16:37.28731131-04:00","level":"INFO","message":"Server shutdown successful","service":"mock-service"}
```


If these logs go to cloudwatch, you can query in cloudwatch logs insights for requests where the path = '/ping' like this:
```text
fields @timestamp, @message
| filter httpRequest.path='/ping'
```


## App Runner deployment

Cloudwatch log insights query for /ping requests
```text
fields @timestamp, @message, @logStream, @log
| filter httpRequest.path="/ping"
| sort @timestamp desc
| limit 100
```