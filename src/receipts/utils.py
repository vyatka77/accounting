from pathlib import Path
from typing import Callable

from .nalog_api import get_ticket_api, refresh_session
from .qr_code import QRCReader
from ..settings import settings, NalogSession
from ..storage.repository import NalogSessionStorage, QRCodeStorage


def nalog_auth(auth_dialog: Callable, *args) -> bool:
    if settings.auth_nalog is None:
        tokens = NalogSessionStorage.list()
        if len(tokens) == 1:
            settings.auth_nalog = NalogSession.model_validate(tokens[0])

    if settings.auth_nalog is not None:
        return True

    NalogSessionStorage.delete_all()
    tokens = auth_dialog(*args).auth_tokens
    if tokens is not None:
        settings.auth_nalog = NalogSession.model_validate(tokens)
        NalogSessionStorage.add(settings.auth_nalog.model_dump())
        return True

    return False


def update_nalog_session() -> None:
    if settings.auth_nalog is None:
        raise RuntimeError("Need authorization and set settings.auth_nalog")
    tokens = settings.auth_nalog
    settings.auth_nalog = None
    NalogSessionStorage.delete_all()
    new_tokens = refresh_session(session_id=tokens.session_id,
                                 refresh_token=tokens.refresh_token,
                                 client_secret=settings.CLIENT_SECRET)
    if new_tokens is not None:
        NalogSessionStorage.add(
            {
                'session_id': new_tokens.session_id,
                'refresh_token': new_tokens.refresh_token
            }
        )
        settings.auth_nalog = NalogSession.model_validate(new_tokens)


def get_ticket(qr: str) -> str | None:
    if settings.auth_nalog is None:
        raise RuntimeError("Need authorization and set settings.auth_nalog")
    ticket_json = get_ticket_api(qr, settings.auth_nalog.session_id)
    if ticket_json is None:
        update_nalog_session()
        ticket_json = get_ticket_api(qr, settings.auth_nalog.session_id)

    return ticket_json


def get_qr_code(filename: str) -> str | None:
    qrs = QRCReader(filename).filter(settings.TICKET_QR_FILTER)
    if not qrs:
        return None

    for qr in qrs:
        QRCodeStorage.add({'qr': qr})

    return qrs[0]


def replace_file(filename: str | Path, new_path: str | Path) -> None:
    filepath = Path(filename)
    filename = filepath.name
    if not filepath.is_file():
        raise ValueError(f"{filename} is invalid name")

    if not filepath.is_absolute():
        filepath = Path(__file__).resolve().parent / filename

    new_path = Path(new_path)
    if new_path.is_absolute():
        new_name = new_path / filename
    else:
        new_name = filepath.resolve().parent / new_path / filename

    new_name.resolve().parent.mkdir(parents=True, exist_ok=True)
    filepath.replace(new_name)


def get_phone_number() -> str:
    if settings.PHONE_NUMBER is not None:
        return settings.PHONE_NUMBER[2:]
    else:
        return ''


def get_inn() -> str:
    if settings.INN is not None:
        return settings.INN
    else:
        return ''


def get_password() -> str:
    if settings.PASSWORD is not None:
        return settings.PASSWORD.get_secret_value()
    else:
        return ''


def get_default_nalog_auth() -> str | None:
    if hasattr(settings, 'USE_NALOG_AUTHORIZATION'):
        return settings.USE_NALOG_AUTHORIZATION


def get_client_secret() -> str:
    return settings.CLIENT_SECRET
