from __future__ import annotations

__all__ = []  # type: ignore

import json
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field
from pydantic.functional_validators import (BeforeValidator,
                                            WrapValidator,
                                            model_validator)
from pydantic_core import ValidationError
from pydantic_core.core_schema import ValidatorFunctionWrapHandler, ValidationInfo
from typing_extensions import Annotated


class QRCodeParser(BaseModel):
    qr: str
    json_: str


class StorageParser(BaseModel):
    name: str = Field(alias="user")
    inn: Annotated[int, WrapValidator(StorageParser.remove_spaces)] = Field(alias="userInn")
    place: str | None = Field(alias="retailPlace", default=None)
    address: str | None = Field(alias="retailPlaceAddress", default=None)

    @classmethod
    def remove_spaces(cls,
                      v: Any,
                      handler: ValidatorFunctionWrapHandler,
                      info: ValidationInfo) -> int:
        if info.mode == 'json':
            assert isinstance(v, str), 'In JSON mode the input must be a string!'
            # you can call the handler multiple times
            try:
                return handler(v)
            except ValidationError:
                return handler(v.strip())
        assert info.mode == 'python'
        assert isinstance(v, int), 'In Python mode the input must be an int!'
        # do no further validation
        return v


class ProductParser(BaseModel):
    name: str
    provider_inn: int | None


class PurchaseParser(BaseModel):
    product: ProductParser
    price: int
    quantity: Decimal
    sum: int

    @model_validator(mode='before')
    @classmethod
    def get_product(cls, data: Any) -> ProductParser | dict[str, Any]:
        product = {
            'name': data.get("name"),
            'provider_inn': data.get("providerInn")
        }
        data['product'] = product
        return data


class TicketParser(BaseModel):
    id: str
    qr_code: QRCodeParser
    storage: Annotated[StorageParser, BeforeValidator(TicketParser.get_storage),] = Field(alias="ticket")
    date_time: Annotated[int, BeforeValidator(TicketParser.get_date)] = Field(alias="ticket")
    purchases: Annotated[list[PurchaseParser], BeforeValidator(TicketParser.get_purchases)] = Field(alias="ticket")
    total_sum: Annotated[int, BeforeValidator(TicketParser.get_total_sum)] = Field(alias="ticket")

    @model_validator(mode='before')
    @classmethod
    def get_qr(cls, data: Any) -> QRCodeParser | dict[str, Any]:
        qr_code = {
            'qr': data['qr'],
            'json_': json.dumps(data, ensure_ascii=False)
        }
        data['qr_code'] = qr_code
        return data

    @staticmethod
    def get_date(v: dict[str, Any]) -> int:
        return v['document']['receipt']['dateTime']

    @staticmethod
    def get_purchases(v: dict[str, Any]) -> list[dict[str, Any]]:
        return v['document']['receipt']['items']

    @staticmethod
    def get_storage(v: dict[str, Any]) -> dict[str, Any]:
        return v['document']['receipt']

    @staticmethod
    def get_total_sum(v: dict[str, Any]) -> int:
        return v['document']['receipt']['totalSum']
