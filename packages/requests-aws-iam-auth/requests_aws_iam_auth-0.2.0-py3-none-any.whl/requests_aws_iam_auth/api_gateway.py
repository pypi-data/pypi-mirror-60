from botocore.awsrequest import AWSRequest  # type: ignore
from botocore.session import Session  # type: ignore
from botocore.auth import SigV4Auth  # type: ignore
from requests.auth import AuthBase
from requests import PreparedRequest


class ApiGateway(AuthBase):
    def __init__(self) -> None:
        botocore_session = Session()
        self.credentials = botocore_session.get_credentials()
        self.region_name = botocore_session.get_config_variable('region')

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        def getSignedRequest():
            signedRequest = AWSRequest(method=r.method.upper(),
                                       headers=r.headers,
                                       url=r.url,
                                       data=r.body)
            SigV4Auth(self.credentials, 'execute-api',
                      self.region_name).add_auth(signedRequest)
            return signedRequest

        if 'connection' in r.headers:
            connection = r.headers['connection']
            del r.headers['connection']
            signedRequest = getSignedRequest()
            r.headers['connection'] = connection
        else:
            signedRequest = getSignedRequest()

        r.headers.update(signedRequest.headers)

        return r