import pytest

from src.receipts.qr_code import QRCReader
from src.settings import settings


def test_ticket_filter(valid_image, invalid_image, qr_code):
    assert QRCReader(valid_image).filter(settings.TICKET_QR_FILTER) == [qr_code]
    assert QRCReader(invalid_image).filter(settings.TICKET_QR_FILTER) == []


def test_ticket_filter_negative():
    with pytest.raises(FileNotFoundError):
        QRCReader('failed_name_file').filter(settings.TICKET_QR_FILTER)


