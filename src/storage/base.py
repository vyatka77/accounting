from typing import Type

from pydantic import BaseModel
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import MappedAsDataclass, Session
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.relationships import RelationshipProperty

from ..settings import settings

engine = create_engine(settings.db.URL, echo=settings.DEBUG)
session_factory = sessionmaker(bind=engine)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=true")
    cursor.close()


class Base(MappedAsDataclass, DeclarativeBase, init=False):

    def save(self, session: Session | None = None):
        if session is None:
            with session_factory() as session:
                session.add(self)
                session.commit()
        else:
            session.add(self)

    @classmethod
    def from_pydantic[BaseSubclass](cls: Type[BaseSubclass], dto: BaseModel) -> BaseSubclass:  # type: ignore
        exclude = set()
        for field in dto.model_fields:
            comparator = cls._sa_class_manager[field].comparator
            if isinstance(comparator, RelationshipProperty.Comparator):
                exclude.add(field)

        obj = cls(**dto.model_dump(exclude=exclude))

        instrumented_list = [f for f in dto.model_fields
                             if isinstance(getattr(obj, f), InstrumentedList)]

        for field in exclude:
            if field not in instrumented_list:
                comparator = cls._sa_class_manager[field].comparator
                ref = comparator.entity.class_.from_pydantic(getattr(dto, field))
                setattr(obj, field, ref)

        for field in instrumented_list:
            for item in getattr(dto, field):
                comparator = cls._sa_class_manager[field].comparator
                ref = comparator.entity.class_.from_pydantic(item)
                getattr(obj, field).append(ref)

        return obj
