import os
from unittest.mock import patch, MagicMock, Mock, call

import pytest
from pydantic import ValidationError

from src.receipts.exceptions import NalogAPIError
from src.receipts.nalog_api import get_ticket_api, _get_ticket_id
from src.settings import NALOG_LOG_FILE as log_file


@patch('src.receipts.nalog_api.requests')
class TestNalogApi:

    def test_get_ticket_id(self, mock_requests, headers):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {"kind": "kkt", "id": "65ce3280ae17240837feb2c1", "status": 2, "statusReal": 2}
        mock_requests.post.return_value = mock
        headers['sessionId'] = 'session_id'

        assert _get_ticket_id('qr_code', 'session_id') == "65ce3280ae17240837feb2c1"
        assert mock_requests.post.call_args == call(
            'https://irkkt-mobile.nalog.ru:8888/v2/ticket',
            json={'qr': 'qr_code'},
            headers=headers
        )

    def test_get_ticket_id_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        with pytest.raises(NalogAPIError):
            _get_ticket_id('qr_code', 'session_id')

    def test_get_ticket_api(self, mock_requests, ticket_json, headers):
        mock = MagicMock()
        mock.status_code = 200
        mock.text = ticket_json
        mock.json.return_value = {"kind": "kkt", "id": "65ce3280ae17240837feb2c1", "status": 2, "statusReal": 2}
        mock_requests.get.return_value = mock
        mock_requests.post.return_value = mock
        headers['sessionId'] = 'session_id'

        assert get_ticket_api('qr_code', 'session_id') == ticket_json
        assert mock_requests.get.call_args == call(
            "https://irkkt-mobile.nalog.ru:8888/v2/tickets/65ce3280ae17240837feb2c1",
            headers=headers
        )

    def test_get_ticket_api_negative(self, mock_requests):
        mock = Mock()
        mock.status_code = 'test'
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert get_ticket_api('qr_code', 'session_id') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_get_ticket_api_raise_exception(self, mock_requests):
        mock = Mock()
        mock.status_code = 200
        mock.json = Mock(side_effect=Exception)
        mock_requests.get.return_value = mock
        mock_requests.post.return_value = mock

        old_log_file_size = os.path.getsize(log_file)

        assert get_ticket_api('qr_code', 'session_id') is None

        new_log_file_size = os.path.getsize(log_file)

        assert old_log_file_size < new_log_file_size

    def test_get_ticket_api_invalid_args(self, mock_requests):
        not_str_qr = 1
        not_str_session_id = 1

        with pytest.raises(ValidationError):
            get_ticket_api(not_str_qr, 'session_id')

        with pytest.raises(ValidationError):
            get_ticket_api('qr', not_str_session_id)
