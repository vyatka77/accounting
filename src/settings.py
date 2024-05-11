from __future__ import annotations

import logging.config
import sys
from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, BeforeValidator, ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
PhoneNumber.phone_format = "E164"


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True,
                                      env_file=BASE_DIR / '.env',
                                      env_prefix='db_',
                                      extra='ignore', )
    NAME: str

    @property
    def URL(self):
        if self.NAME:
            return f"sqlite:///{BASE_DIR / self.NAME}"
        return "sqlite://"  # To use a SQLite :memory: database


class NalogAPISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      secrets_dir=BASE_DIR / "data-project/secrets",
                                      extra='ignore')

    CLIENT_SECRET: str
    PHONE_NUMBER: PhoneNumber | None = Field(None)
    INN: Annotated[str, BeforeValidator(inn_validate)] | None = None
    PASSWORD: SecretStr | None = Field(None, alias='nalog_password')
    USE_NALOG_AUTHORIZATION: str = 'inn'

    @staticmethod
    def inn_validate(inn: str) -> str:
        if len(inn) != 12 and not inn.isdigit():
            raise ValidationError(f"INN must contain only 12 digits")
        return inn


class NalogSession(BaseSettings):
    model_config = SettingsConfigDict(from_attributes=True)

    session_id: str
    refresh_token: str


class GUISettings(BaseSettings):
    GUI_THEME_PATH: str | Path = BASE_DIR / "data-project/themes/awthemes-10.4.0"
    NAME_THEME: str = 'awdark'
    QR_IMAGES_DIR: str | Path | None = BASE_DIR / "data/receipts"


class Settings(GUISettings,
               NalogAPISettings,
               validate_assignment=True):
    MODE: str
    DEBUG: bool = False
    TICKET_QR_FILTER: str = r"t=[0-9]{8}T[0-9]+&s=[0-9]+.[0-9]{2}&fn=[0-9]{16}&i=[0-9]+&fp=[0-9]+&n=[0-9]"
    db: DBSettings = DBSettings()
    auth_nalog: NalogSession | None = None


NALOG_LOG_FILE = BASE_DIR / 'logs/nalog.log'
GUI_LOG_FILE = BASE_DIR / 'logs/gui.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'exception': {
            'format': "%(levelname)s - %(name)s: %(message)s",
        },
    },
    'handlers': {
        'console': {
            'class': logging.StreamHandler,
            'stream': sys.stderr,
            'level': 'WARNING',
        },
        'gui': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'filename': GUI_LOG_FILE,
            'formatter': 'exception',
            'encoding': 'utf-8',
        },
        'nalog': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'filename': NALOG_LOG_FILE,
            'formatter': 'exception',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'src.gui': {
            'level': 'WARNING',
            'handlers': ['gui', 'console'],
            'propagate': True,
            'encoding': 'utf-8',
        },
        'src.receipts.nalog_api': {
            'level': 'WARNING',
            'handlers': ['nalog', 'console'],
            'propagate': True,
            'encoding': 'utf-8',
        },
    },
}

settings = Settings()
logging.config.dictConfig(LOGGING)
