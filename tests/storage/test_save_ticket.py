import json

from src.receipts.json_parse import TicketParser
from src.storage.models import (TicketORM, CategoryORM, StorageORM,
                                PurchaseORM, ProductORM, QRCodeORM)


def test_save_ticket(ticket_json, session):
    ticket_parser = TicketParser.model_validate_json(ticket_json)
    ticket_orm = TicketORM.from_pydantic(ticket_parser)

    CategoryORM(name='Продукты').save()
    category_id = session.query(CategoryORM).where(CategoryORM.name == 'Продукты').scalar().id

    for item in ticket_orm.purchases:
        item.product.category_id = category_id
    ticket_orm.save()

    save_ticket = session.query(TicketORM).scalar()

    assert save_ticket.qr == 't=20240211T1400&s=411.70&fn=7284440700373884&i=14980&fp=1152442848&n=1'
    assert save_ticket.storage_inn == 268040102
    assert save_ticket.date_time == 1707649200
    assert save_ticket.total_sum == 41170

    save_storage = session.query(StorageORM).scalar()

    assert save_storage.inn == 268040102
    assert save_storage.name == 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЗАРИНА"'
    assert save_storage.place == 'ГМ Волочаевская'
    assert save_storage.address == '02 - Республика Башкортостан, г.о. город Стерлитамак,453103,, г Стерлитамак,, ул Волочаевская, д. 6а,,,'

    save_qr_code = session.get(QRCodeORM, 't=20240211T1400&s=411.70&fn=7284440700373884&i=14980&fp=1152442848&n=1')

    assert json.loads(save_qr_code.json_) == json.loads(ticket_json)

    assert session.query(PurchaseORM).count() == 3
    assert session.query(ProductORM).count() == 3
