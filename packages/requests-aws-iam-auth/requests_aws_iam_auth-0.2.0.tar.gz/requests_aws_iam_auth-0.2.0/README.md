# Requests AWS IAM Auth
An AWS IAM authentication package for Requests. Supported services: API Gateway v1. This is intended for use in production environments at the 1.0 release.

## Example

### API Gateway v1
```python
import requests
import requests_aws_iam_auth

# Provide AWS creds and config per Boto3 specs: https://tknk.io/ri3v
auth = requests_aws_iam_auth.ApiGateway()

requests.get("https://p7xw90rcx4.execute-api.us-east-1.amazonaws.com/s/", auth=auth)
```

## Developer Information

### Dependencies
Botocore

### Headers
authorization, and x-amz-content-sha256 are directly modified in the signing protocal and will be set.

Expect for authorization, connection, expect, user-agent, x-amz-content-sha256, x-amz-security-token and x-amzn-trace-id all user set headers are signed.

If the user does not specify host it is derived and signed. 

If the method is not GET, HEAD, or OPTIONS, has a payload, and the user does not provide a content-length header it is derived and signed.

If there's a Date header, we set the date header. Otherwise, we set the X-Amz-Date header.

The underlying http.client will derive an unsigned accept-encoding header if not user specified.

If using STS x-amz-security-token will be set by this library.

### Payload
The payload is always signed using SHA 256.

### Protocols
HTTP and HTTPS 1.1 are supported.

### Python
Latest three minor versions of python will be supported.

## Contributor Notes
This library uses botocore for signing. 

Requests uses urllib3 which uses http.client.

Botocore relies on http.client deriving the host when absent. Botocore replacates this deravation and signs with it but does not append the header to the sent request. This has the potential for a mismatch error. There is a TODO in botocore to set the host header in the request.

### Maintainers
#### Core
Mateus Amin and Benton Drew
#### API Gateway v1
Mateus Amin and Benton Drew
#### Some Other Service
????

### References
- https://docs.python.org/3/library/http.client.html#module-http.client
- https://hg.python.org/cpython/file/3.2/Lib/http/client.py
- https://github.com/urllib3/urllib3/blob/063d888bc247eb6bd7aedcd32412bbb53c3c6ffb/src/urllib3/connection.py#L195
- https://github.com/psf/requests/blob/7b565d886c852609a849e79e4ad8f3f8fa8d8c23/requests/adapters.py#L166

### TODO
- Add testing of three most recent python versions. Use docker not tox. No reason to bloat the stack.
- Add fuzzing?
- Add CI build. Keep it portable and deterministic.
- Support AWS API Gateway v2 if it adds IAM Auth as a feature. Same for HTTP2.
- Add Requests v3 support.
- connection header. The connection header is set to blank between post auth and the server signing (inclusive). Could be a AWS, Requests, urllib3, botocore, or http.client. Have ruled out botocore. Can rule out the urllib3 and http.client by reading the sent request on the wire. As a temporary workaround we do not sign it.