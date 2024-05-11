from typing import Any, Sequence

from sqlalchemy import delete, func, select, update, insert
from sqlalchemy.orm import InstrumentedAttribute

from .base import session_factory
from .models import TicketORM, ProductORM, CategoryORM, NalogSessionORM, QRCodeORM


class Repository:
    model: Any
    pk: InstrumentedAttribute

    @classmethod
    def add(cls, values: dict[str, Any] | list[dict[str, Any]]) -> Sequence[Any]:
        stmt = insert(cls.model).returning(cls.model)
        if isinstance(values, dict):
            values = [values]
        with session_factory() as session:
            new = session.execute(stmt, values)
            session.commit()
            return new.scalars().all()

    @classmethod
    def get(cls, pk: Any, *, map: bool = False) -> Any | dict[str, Any]:
        with session_factory() as session:
            if map:
                stmt = select(cls.model.__table__.columns).where(cls.pk == pk)
                return session.execute(stmt).mappings().one()
            return session.get_one(cls.model, pk)

    @classmethod
    def list(cls, *, filter_by: dict[str, Any] | None = None) -> Sequence[Any]:
        if filter_by is None:
            filter_by = {}
        stmt = select(cls.model).filter_by(**filter_by)
        with session_factory() as session:
            return session.scalars(stmt).all()

    @classmethod
    def count(cls) -> int:
        stmt = select(func.count()).select_from(cls.model)
        with session_factory() as session:
            res = session.execute(stmt).scalar()
            if res is None:
                return 0
            return res

    @classmethod
    def update(cls, pk: Any, values: dict[str, Any]):
        stmt = update(cls.model).where(cls.pk == pk).values(**values)
        with session_factory() as session:
            session.execute(stmt)
            session.commit()

    @classmethod
    def delete(cls, pk: Any):
        stmt = delete(cls.model).where(cls.pk == pk)
        with session_factory() as session:
            session.execute(stmt)
            session.commit()

    @classmethod
    def delete_all(cls):
        stmt = delete(cls.model)
        with session_factory() as session:
            session.execute(stmt)
            session.commit()


class NalogSessionStorage(Repository):
    model = NalogSessionORM
    pk = NalogSessionORM.session_id


class QRCodeStorage(Repository):
    model = QRCodeORM
    pk = QRCodeORM.qr


class TicketStorage(Repository):
    model = TicketORM
    pk = TicketORM.id


class ProductStorage(Repository):
    model = ProductORM
    pk = ProductORM.id


class CategoryStorage(Repository):
    model = CategoryORM
    pk = CategoryORM.id
