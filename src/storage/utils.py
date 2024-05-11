from .base import engine
from .models import Base
from .repository import CategoryStorage


def create_tables():
    data = [
        {'name': 'Продукты'},
        {'name': 'Одежда'},
        {'name': 'Авторасходы'},
    ]
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    CategoryStorage.add(data)


if __name__ == '__main__':
    create_tables()
