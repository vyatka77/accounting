from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent


@pytest.fixture(scope='session')
def ticket_json() -> str:
    with open(BASE_DIR / "data/after_parser.json", encoding='utf-8') as file:
        return file.read()
