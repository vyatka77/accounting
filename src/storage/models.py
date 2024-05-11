from decimal import Decimal

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from typing_extensions import Annotated

from .base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
strpk = Annotated[str, mapped_column(primary_key=True)]
text = Annotated[str, mapped_column(Text)]


class NalogSessionORM(Base):
    __tablename__ = 'nalog_session'

    session_id: Mapped[strpk]
    refresh_token: Mapped[str]


class CategoryORM(Base):
    __tablename__ = 'categories'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[text | None] = mapped_column(deferred=True, repr=False)
    img: Mapped[text | None] = mapped_column(deferred=True, repr=False)

    products: Mapped[list['ProductORM']] = relationship(back_populates='category',
                                                        order_by='-ProductORM.id',
                                                        repr=False)


class ProductORM(Base):
    __tablename__ = 'products'

    id: Mapped[intpk]
    name: Mapped[text] = mapped_column(unique=True,
                                       sqlite_on_conflict_primary_key='IGNORE',
                                       sqlite_on_conflict_unique='IGNORE')
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'), nullable=False)
    provider_inn: Mapped[int | None]

    category: Mapped['CategoryORM'] = relationship(back_populates='products', lazy='joined')
    purchases: Mapped[list['PurchaseORM']] = relationship(back_populates='product', repr=False)


class StorageORM(Base):
    __tablename__ = 'storages'

    inn: Mapped[intpk] = mapped_column(sqlite_on_conflict_primary_key='IGNORE')
    name: Mapped[str]
    place: Mapped[text | None]
    address: Mapped[text | None]

    tickets: Mapped[list['TicketORM']] = relationship(back_populates='storage')


class QRCodeORM(Base):
    __tablename__ = 'qrcodes'

    qr: Mapped[strpk] = mapped_column(sqlite_on_conflict_primary_key='REPLACE')
    json_: Mapped[text | None]

    ticket: Mapped['TicketORM'] = relationship(back_populates='qr_code', repr=False)


class TicketORM(Base):
    __tablename__ = 'tickets'

    id: Mapped[strpk]
    date_time: Mapped[int]
    total_sum: Mapped[int]
    qr = mapped_column(ForeignKey('qrcodes.qr'), unique=True)
    storage_inn = mapped_column(ForeignKey('storages.inn'))

    qr_code: Mapped['QRCodeORM'] = relationship(back_populates='ticket', repr=False)
    storage: Mapped['StorageORM'] = relationship(back_populates='tickets', repr=False)
    purchases: Mapped[list['PurchaseORM']] = relationship(back_populates='ticket',
                                                          cascade="all, delete-orphan",
                                                          repr=False)


class PurchaseORM(Base):
    __tablename__ = 'purchases'

    id: Mapped[intpk]
    ticket_id = mapped_column(ForeignKey('tickets.id', ondelete='CASCADE'))
    product_id = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))
    price: Mapped[int]
    quantity: Mapped[Decimal]
    sum: Mapped[int]

    ticket: Mapped['TicketORM'] = relationship(back_populates='purchases', repr=False)
    product: Mapped['ProductORM'] = relationship(back_populates='purchases',
                                                 lazy='selectin',
                                                 repr=False)

    @validates('quantity')
    def validate_quantity(self, key: str, value: float):
        if value <= 0:
            raise ValueError(f"{key} must be greater than 0")
        return value
