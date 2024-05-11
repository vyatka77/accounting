__all__ = []  # type: ignore

from requests import Response


class NalogAPIError(Exception):
    msg = "%s, status code: %s, message response: %s"

    def __init__(self, resp: Response, **kwargs):
        self.args = (self.msg % (resp.url, resp.status_code, resp.text) +
                     f"\n\tData: {kwargs}\n",)


class NalogAuthError(NalogAPIError): ...
