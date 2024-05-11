import pytest


@pytest.fixture
def headers() -> dict:
    return {'Host': 'irkkt-mobile.nalog.ru:8888', 'Accept': '*/*', 'Device-OS': 'iOS',
            'Device-Id': '7C82010F-16CC-446B-8F66-FC4080C66521', 'clientVersion': '2.9.0',
            'Accept-Language': 'ru-RU;q=1, en-US;q=0.9',
            'User-Agent': 'billchecker/2.9.0 (iPhone; iOS 13.6; Scale/2.00)'}
