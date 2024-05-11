from pathlib import Path

import pytest

from src.settings import settings
from src.storage.base import Base
from src.storage.base import engine, session_factory

BASE_DIR = Path(__file__).parent


@pytest.fixture(scope='session', autouse=True)
def setup_db():
    assert settings.MODE == 'TEST'
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session():
    with  session_factory() as session:
        yield session


@pytest.fixture(scope='session')
def ticket_json() -> str:
    with open(BASE_DIR / "data/after_parser.json", encoding='utf-8') as file:
        return file.read()
