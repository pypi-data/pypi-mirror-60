from __future__ import annotations
import sys
import requests
from urllib.parse import urljoin, urlencode

import jigu.version
from jigu.error import ClientError, TerraAPIError
from jigu.util import serialize_to_json

pv = sys.version_info

CLIENT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": f"jigu v{jigu.version.JIGU_VERSION} (Python {pv[0]}.{pv[1]}.{pv[2]})",
}


def check_4xx_errors(response: requests.Response):
    if str(response.status_code).startswith("4"):
        try:
            res = response.json()
            error = res["error"]
        except ValueError:
            error = f"status code {response.status_code}"
        raise ClientError(f"{response.status_code}: {error}")
    return response


class HTTPClient(object):
    def __init__(self, api_base: str = "", chain_id: str = "", timeout: int = 10):
        self.api_base = api_base
        self.chain_id = chain_id
        self.session = self._init_session()
        self.timeout = timeout

    def _init_session(self):
        session = requests.session()
        session.headers.update(CLIENT_HEADERS)
        return session

    def _request(self, method, path, **kwargs):
        uri = self._create_uri(path)
        kwargs = self._get_request_kwargs(method, **kwargs)
        response = getattr(self.session, method)(uri, **kwargs)
        return response

    def _create_uri(self, path):
        return urljoin(self.api_base, path)

    def _get_request_kwargs(self, method, **kwargs):
        # set default requests timeout
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)

        kwargs["data"] = kwargs.get("data", None)
        kwargs["headers"] = kwargs.get("headers", {})

        if kwargs["data"] and method == "get":
            kwargs["params"] = kwargs["data"]
            del kwargs["data"]

        if method == "post":
            kwargs["headers"]["content-type"] = "application/json"
            kwargs["data"] = serialize_to_json(
                kwargs["data"]
            )  # apply custom serialization
        return kwargs

    def get(self, path, **kwargs):
        return check_4xx_errors(self._request("get", path, **kwargs))

    def post(self, path, **kwargs):
        return check_4xx_errors(self._request("post", path, **kwargs))

