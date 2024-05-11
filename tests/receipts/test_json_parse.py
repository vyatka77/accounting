import pytest
from pydantic_core import ValidationError

from src.receipts.json_parse import TicketParser


def test_ticket_parser(after_parser, before_parser):
    parser = TicketParser.model_validate_json(after_parser)
    assert parser.model_dump() == before_parser


@pytest.mark.parametrize("after",
                         [('fail json',), (1,), ('"key":true',)],
                         ids=['string', 'integer', 'fail json'])
def test_ticket_parser_negative(after):
    with pytest.raises(ValidationError):
        TicketParser.model_validate_json(after)
