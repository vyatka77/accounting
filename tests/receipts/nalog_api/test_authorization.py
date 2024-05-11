import os
from itertools import cycle
from unittest.mock import patch, Mock, PropertyMock, call

import pytest
from pydantic import ValidationError

from src.receipts.exceptions import NalogAuthError
from src.receipts.nalog_api import inn, sms, authorization
from src.settings import NALOG_LOG_FILE as log_file


@patch('src.receipts.nalog_api.requests')
class TestAuthNalogApi:

    def test_inn(self, mock_requests, headers):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {
            "sessionId": "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1",
            "refresh_token": "3b4378cb-cfa0-4ab6-a07e-dc9095822106",
        }
        mock_requests.post.return_value = mock

        resp = inn('inn', 'password', client_secret='test')

        assert resp.session_id == "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1"
        assert resp.refresh_token == "3b4378cb-cfa0-4ab6-a07e-dc9095822106"
        assert mock_requests.post.call_args == call(
            'https://irkkt-mobile.nalog.ru:8888/v2/mobile/users/lkfl/auth',
            json={'inn': 'inn', 'client_secret': 'test', 'password': 'password'},
            headers=headers
        )

    def test_inn_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        with pytest.raises(NalogAuthError):
            inn('inn', 'password', client_secret='test')

    def test_inn_invalid_args(self, mock_requests):
        not_str_inn = 1
        not_str_password = 1
        not_str_client_secret = 1

        with pytest.raises(ValidationError):
            inn(not_str_inn, 'password', client_secret='test')

        with pytest.raises(ValidationError):
            inn('inn', not_str_password, client_secret='test')

        with pytest.raises(ValidationError):
            inn('inn', 'password', client_secret=not_str_client_secret)

    def test_sms(self, mock_requests, headers):
        mock = Mock()
        type(mock).status_code = PropertyMock(side_effect=cycle([204, 200]))
        mock.json.return_value = {
            "sessionId": "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1",
            "refresh_token": "3b4378cb-cfa0-4ab6-a07e-dc9095822106",
        }
        mock_requests.post.return_value = mock

        resp = sms('phone',
                   input_interface=lambda *args: '5432',
                   client_secret='test')

        assert resp.session_id == "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1"
        assert resp.refresh_token == "3b4378cb-cfa0-4ab6-a07e-dc9095822106"
        assert mock_requests.post.call_count == 2
        assert mock_requests.post.call_args_list[0] == call(
            'https://irkkt-mobile.nalog.ru:8888/v2/auth/phone/request',
            json={'phone': 'phone', 'client_secret': 'test',
                  'os': 'Android', 'code': '5432'},
            headers=headers
        )
        assert mock_requests.post.call_args_list[1] == call(
            'https://irkkt-mobile.nalog.ru:8888/v2/auth/phone/verify',
            json={'phone': 'phone', 'client_secret': 'test',
                  'os': 'Android', 'code': '5432'},
            headers={'Host': 'irkkt-mobile.nalog.ru:8888',
                     'Accept': '*/*', 'Device-OS': 'iOS',
                     'Device-Id': '7C82010F-16CC-446B-8F66-FC4080C66521',
                     'clientVersion': '2.9.0',
                     'Accept-Language': 'ru-RU;q=1, en-US;q=0.9',
                     'User-Agent': 'billchecker/2.9.0 (iPhone; iOS 13.6; Scale/2.00)'}
        )

    def test_sms_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        with pytest.raises(NalogAuthError):
            sms('phone',
                lambda *args: '5432',
                client_secret='test')

    # def test_sms_negative_two_part(self, mock_requests):
    #     mock = Mock()
    #     type(mock).status_code = PropertyMock(side_effect=cycle([204, 'test']))
    #     mock_requests.post.return_value = mock
    #
    #     with pytest.raises(NalogAuthError):
    #         sms('phone',
    #             lambda *args: '5432',
    #             client_secret='test')

    def test_sms_invalid_args(self, mock_requests):
        not_str_phone = 1
        not_str_client_secret = 1

        with pytest.raises(ValidationError):
            sms(not_str_phone,
                lambda *args: '5432',
                client_secret='test')

        with pytest.raises(ValidationError):
            sms('phone',
                'not_callable_argument',
                client_secret='test')

        with pytest.raises(ValidationError):
            sms('phone',
                lambda *args: '5432',
                client_secret=not_str_client_secret)

    def test_authorization(self, mock_requests):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {
            "sessionId": "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1",
            "refresh_token": "3b4378cb-cfa0-4ab6-a07e-dc9095822106",
        }
        mock_requests.post.return_value = mock

        resp = authorization('inn', 'inn', 'password', client_secret='test')

        assert resp.session_id == "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1"
        assert resp.refresh_token == "3b4378cb-cfa0-4ab6-a07e-dc9095822106"

    def test_authorization_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert authorization('inn', 'inn', 'password') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_authorization_raise_exception(self, mock_requests):
        mock = Mock()
        mock.status_code = 200
        mock.json = Mock(side_effect=Exception)
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert authorization('inn', 'inn', 'password', client_secret='test') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_authorization_invalid_method(self, mock_requests):
        with pytest.raises(ValueError):
            authorization('test')
