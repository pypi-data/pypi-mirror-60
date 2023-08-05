from oidcendpoint.client_authn import CLIENT_AUTHN_METHOD
from oidcendpoint.util import build_endpoints


class EndpointCollection:
    def __init__(self, conf, **kwargs):
        self.endpoint = build_endpoints(
            conf["endpoint"],
            endpoint_context=self,
            client_authn_method=CLIENT_AUTHN_METHOD,
            issuer=conf["issuer"],
        )
