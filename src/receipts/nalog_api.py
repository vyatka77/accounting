# https://leftjoin.ru/all/nalog-ru-client/
# https://github.com/valiotti/get-receipts
# https://ofd.ru/razrabotchikam/cheki-i-kkt?ysclid=lsnehegx2j884168438
import logging
from typing import Callable, NamedTuple

import requests
from pydantic import validate_call

from .exceptions import NalogAuthError, NalogAPIError

logger = logging.getLogger(__name__)

DEVICE_OS = 'iOS'
CLIENT_VERSION = '2.9.0'
DEVICE_ID = '7C82010F-16CC-446B-8F66-FC4080C66521'
ACCEPT = '*/*'
USER_AGENT = 'billchecker/2.9.0 (iPhone; iOS 13.6; Scale/2.00)'
ACCEPT_LANGUAGE = 'ru-RU;q=1, en-US;q=0.9'
OS = 'Android'

# API 'rkkt_nalog' service
HOST = 'irkkt-mobile.nalog.ru:8888'
INN_AUTH_URL = f"https://{HOST}/v2/mobile/users/lkfl/auth"
SMS_AUTH_URL = f"https://{HOST}/v2/auth/phone/request"
SMS_VERIFY_AUTH_URL = f"https://{HOST}/v2/auth/phone/verify"
TICKET_ID_URL = f"https://{HOST}/v2/ticket"
TICKET_DETAILS_URL = f"https://{HOST}/v2/tickets/%s"
REFRESH_AUTHORIZATION_URL = f"https://{HOST}/v2/mobile/users/refresh"

headers = {
    'Host': HOST,
    'Accept': ACCEPT,
    'Device-OS': DEVICE_OS,
    'Device-Id': DEVICE_ID,
    'clientVersion': CLIENT_VERSION,
    'Accept-Language': ACCEPT_LANGUAGE,
    'User-Agent': USER_AGENT,
}

auth_methods = {}


class SessionTokens(NamedTuple):
    session_id: str
    refresh_token: str


def register(func: Callable) -> Callable:
    auth_methods[func.__name__] = func
    return func


@register
@validate_call
def inn(inn: str, password: str, client_secret: str) -> SessionTokens:
    payload = {
        'inn': inn,
        'client_secret': client_secret,
        'password': password
    }

    resp = requests.post(INN_AUTH_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise NalogAuthError(resp)

    return SessionTokens(session_id=resp.json()['sessionId'],
                         refresh_token=resp.json()['refresh_token'])


@register
@validate_call
def sms(phone: str, input_interface: Callable[[str], str], client_secret: str) -> SessionTokens:
    payload = {
        'phone': phone,
        'client_secret': client_secret,
        'os': OS
    }

    resp = requests.post(SMS_AUTH_URL, json=payload, headers=headers)

    if resp.status_code != 204:
        raise NalogAuthError(resp)

    payload['code'] = input_interface("СМС код:")
    resp = requests.post(SMS_VERIFY_AUTH_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise NalogAuthError(resp)

    return SessionTokens(session_id=resp.json()['sessionId'],
                         refresh_token=resp.json()['refresh_token'])


def authorization(method: str, *args, **kwargs) -> SessionTokens | None:
    if method not in auth_methods:
        raise ValueError(f"Authorization method {method!r} not implementation")
    try:
        return auth_methods[method](*args, **kwargs)
    except Exception:
        logger.exception("")


@validate_call
def refresh_session(*, session_id: str,
                    refresh_token: str,
                    client_secret: str) -> SessionTokens | None:
    payload = {
        'refresh_token': refresh_token,
        'client_secret': client_secret
    }
    headers['sessionId'] = session_id

    try:
        resp = requests.post(REFRESH_AUTHORIZATION_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            raise NalogAuthError(resp)
        return SessionTokens(session_id=resp.json()['sessionId'],
                             refresh_token=resp.json()['refresh_token'])
    except Exception:
        logger.exception("")


def _get_ticket_id(qr: str, session_id: str) -> str:
    """
    Get ticket id by info from qr code
    :param qr: text from qr code. Example "t=20200727T174700&s=746.00&fn=9285000100206366&i=34929&fp=3951774668&n=1"
    :return: ticket id. Example "5f3bc6b953d5cb4f4e43a06c"
    """
    payload = {'qr': qr}
    headers['sessionId'] = session_id

    resp = requests.post(TICKET_ID_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise NalogAPIError(resp, qr=qr)

    return resp.json()['id']


@validate_call
def get_ticket_api(qr: str, session_id: str) -> str | None:
    try:
        ticket_id = _get_ticket_id(qr, session_id)
        url = TICKET_DETAILS_URL % ticket_id

        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            raise NalogAPIError(resp, qr=qr)

        return resp.text
    except Exception:
        logger.exception("")
