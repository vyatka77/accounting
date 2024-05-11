import os
from unittest.mock import patch, Mock, call

import pytest
from pydantic import ValidationError

from src.receipts.nalog_api import refresh_session
from src.settings import NALOG_LOG_FILE as log_file


@patch('src.receipts.nalog_api.requests')
class TestRefreshSession:

    def test_refresh_session(self, mock_requests, headers):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {
            "sessionId": "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1",
            "refresh_token": "3b4378cb-cfa0-4ab6-a07e-dc9095822106",
        }
        mock_requests.post.return_value = mock
        headers['sessionId'] = 'test'

        resp = refresh_session(session_id='test',
                               refresh_token='test',
                               client_secret='test')

        assert resp.session_id == "66054fd6ba091652868559ca:aa1b8336-af0b-4adc-bbc2-0e664692aff1"
        assert resp.refresh_token == "3b4378cb-cfa0-4ab6-a07e-dc9095822106"
        assert mock_requests.post.call_args == call(
            'https://irkkt-mobile.nalog.ru:8888/v2/mobile/users/refresh',
            json={'refresh_token': 'test', 'client_secret': 'test'},
            headers=headers
        )

    def test_refresh_session_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert refresh_session(session_id='test',
                               refresh_token='test',
                               client_secret='test') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_refresh_session_raise_exception(self, mock_requests):
        mock = Mock()
        mock.status_code = 200
        mock.json = Mock(side_effect=Exception)
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert refresh_session(session_id='test',
                               refresh_token='test',
                               client_secret='test') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_refresh_session_invalid_args(self, mock_requests):
        not_str_session_id = 1
        not_str_refresh_token = 1
        not_str_client_secret = 1

        with pytest.raises(ValidationError):
            refresh_session(session_id=not_str_session_id,
                            refresh_token='test',
                            client_secret='test')

        with pytest.raises(ValidationError):
            refresh_session(session_id='test',
                            refresh_token=not_str_refresh_token,
                            client_secret='test')

        with pytest.raises(ValidationError):
            refresh_session(session_id='test',
                            refresh_token='test',
                            client_secret=not_str_client_secret)
