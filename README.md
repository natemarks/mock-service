# mock-service

The service should invoke a graceful shutdonw letting eerything finish when a sigterm is caught

## Usage
curl -X GET 'http://localhost:2017/?wait=5000ms'

(the response takes 5000 milliseconds)
You waited for 5000ms%

