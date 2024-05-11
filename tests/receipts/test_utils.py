from unittest.mock import patch, Mock

import pytest

from src.receipts.nalog_api import SessionTokens
from src.receipts.utils import get_qr_code, get_ticket, update_nalog_session, nalog_auth, replace_file
from src.storage.models import NalogSessionORM
from src.storage.repository import QRCodeStorage


def test_get_qr_code(valid_image, invalid_image, qr_code):
    assert get_qr_code(valid_image) == qr_code
    assert get_qr_code(valid_image) == qr_code
    assert get_qr_code(invalid_image) == None
    assert QRCodeStorage.count() == 1
    assert QRCodeStorage.get(qr_code).qr == qr_code
    assert QRCodeStorage.get(qr_code).json_ == None


@patch('src.receipts.utils.settings')
@pytest.mark.usefixtures('not_nalog_authorized')
class TestNalogAuth:
    def test_nalog_auth_with_authorization(self,
                                           mock_settings,
                                           nalog_authorized,
                                           session):
        mock_settings.auth_nalog = None

        assert nalog_auth(lambda: None) is True
        assert session.query(NalogSessionORM).count() == 1
        assert session.query(NalogSessionORM).scalar().session_id == 'session_id'
        assert session.query(NalogSessionORM).scalar().refresh_token == 'refresh_token'
        assert mock_settings.auth_nalog.session_id == 'session_id'
        assert mock_settings.auth_nalog.refresh_token == 'refresh_token'

    def test_nalog_auth_without_authorization(self,
                                              mock_settings,
                                              session):
        mock_settings.auth_nalog = None
        mock = Mock()
        mock.auth_tokens = SessionTokens(session_id='new_session_id',
                                         refresh_token='new_refresh_token')

        assert nalog_auth(lambda: mock) is True
        assert session.query(NalogSessionORM).count() == 1
        assert session.query(NalogSessionORM).scalar().session_id == 'new_session_id'
        assert session.query(NalogSessionORM).scalar().refresh_token == 'new_refresh_token'
        assert mock_settings.auth_nalog.session_id == 'new_session_id'
        assert mock_settings.auth_nalog.refresh_token == 'new_refresh_token'

    def test_nalog_auth_negative(self,
                                 mock_settings,
                                 session):
        mock_settings.auth_nalog = None
        mock = Mock()
        mock.auth_tokens = None

        assert nalog_auth(lambda: mock) is False
        assert session.query(NalogSessionORM).count() == 0
        assert mock_settings.auth_nalog is None


@patch('src.receipts.utils.refresh_session')
@patch('src.receipts.utils.settings')
class TestUpdateNalogSession:
    def test_update_nalog_session(self,
                                  mock_settings,
                                  mock_refresh_session,
                                  session):
        mock_settings.auth_nalog = SessionTokens(session_id='old_session_id',
                                                 refresh_token='old_refresh_token')
        mock_refresh_session.return_value = SessionTokens(session_id='new_session_id',
                                                          refresh_token='new_refresh_token')
        assert mock_settings.auth_nalog.session_id == 'old_session_id'
        assert mock_settings.auth_nalog.refresh_token == 'old_refresh_token'

        update_nalog_session()

        assert mock_settings.auth_nalog.session_id == 'new_session_id'
        assert mock_settings.auth_nalog.refresh_token == 'new_refresh_token'
        assert session.query(NalogSessionORM).count() == 1
        assert session.query(NalogSessionORM).scalar().session_id == 'new_session_id'
        assert session.query(NalogSessionORM).scalar().refresh_token == 'new_refresh_token'

    def test_update_nalog_session_negative(self,
                                           mock_settings,
                                           mock_refresh_session,
                                           session):
        mock_settings.auth_nalog = SessionTokens(session_id='session_id',
                                                 refresh_token='refresh_token')
        mock_refresh_session.return_value = None

        update_nalog_session()

        assert mock_settings.auth_nalog == None
        assert session.query(NalogSessionORM).count() == 0

    def test_update_nalog_session_without_authorization(self,
                                                        mock_settings,
                                                        mock_refresh_session,
                                                        session):
        mock_settings.auth_nalog = None

        with pytest.raises(RuntimeError):
            update_nalog_session()

        assert mock_settings.auth_nalog == None
        assert session.query(NalogSessionORM).count() == 0


@patch('src.receipts.utils.update_nalog_session')
@patch('src.receipts.utils.get_ticket_api')
@patch('src.receipts.utils.settings')
class TestGetTicket:

    def test_get_ticket_with_fresh_tokens(self,
                                          mock_settings,
                                          mock_get_ticket_api,
                                          mock_update_nalog_session,
                                          ticket_json):
        mock_settings.auth_nalog = SessionTokens(session_id='session_id',
                                                 refresh_token='refresh_token')
        mock_get_ticket_api.return_value = ticket_json

        assert get_ticket('qr_code') == ticket_json
        assert mock_get_ticket_api.call_count == 1
        assert not mock_update_nalog_session.call_count

    def test_get_ticket_without_fresh_tokens(self,
                                             mock_settings,
                                             mock_get_ticket_api,
                                             mock_update_nalog_session,
                                             ticket_json):
        mock_settings.auth_nalog = SessionTokens(session_id='session_id',
                                                 refresh_token='refresh_token')
        mock_get_ticket_api.side_effect = [None, ticket_json]

        assert get_ticket('qr_code') == ticket_json
        assert mock_get_ticket_api.call_count == 2
        assert mock_update_nalog_session.call_count == 1

    def test_get_ticket_without_authorization(self, mock_settings, *args):
        mock_settings.auth_nalog = None

        with pytest.raises(RuntimeError):
            get_ticket('qr_code')

    def test_get_ticket_negative(self,
                                 mock_settings,
                                 mock_get_ticket_api,
                                 mock_update_nalog_session):
        mock_settings.auth_nalog = SessionTokens(session_id='session_id',
                                                 refresh_token='refresh_token')
        mock_get_ticket_api.return_value = None

        assert get_ticket('qr_code') is None
        assert mock_get_ticket_api.call_count == 2
        assert mock_update_nalog_session.call_count == 1


class TestReplaceFile:
    def test_replace_file_raise_exception(self):
        with pytest.raises(ValueError):
            replace_file('invalid_filename', 'test.py')
