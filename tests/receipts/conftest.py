import pickle
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import delete

from src.storage.models import NalogSessionORM

BASE_DIR = Path(__file__).parent.parent


@pytest.fixture
def not_nalog_authorized(session):
    with session:
        session.execute(delete(NalogSessionORM))
        session.commit()


@pytest.fixture
def nalog_authorized(session):
    with session:
        obj = NalogSessionORM(session_id='session_id',
                              refresh_token='refresh_token')
        session.add(obj)
        session.commit()


@pytest.fixture(scope='session')
def valid_image() -> str:
    return str(BASE_DIR / "data/valid_qr_code.jpeg")


@pytest.fixture(scope='session')
def invalid_image() -> str:
    return str(BASE_DIR / "data/invalid_qr_code.jpeg")


@pytest.fixture(scope='session')
def qr_code() -> str:
    return 't=20240215T1156&s=967.00&fn=7281440500961252&i=29686&fp=1281831186&n=1'


@pytest.fixture(scope='session')
def after_parser(ticket_json) -> str:
    return ticket_json


@pytest.fixture(scope='session')
def before_parser() -> dict[str, Any]:
    with open(BASE_DIR / "data/before_parser.pickle", "rb") as file:
        return pickle.load(file)
