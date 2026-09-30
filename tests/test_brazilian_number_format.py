import math

from coffee_analysis.reporting.brazilian_number_format import BrazilianNumberFormat

NUMBER_FORMAT = BrazilianNumberFormat()


def test_currency_uses_brazilian_separators() -> None:
    assert NUMBER_FORMAT.currency(1234567.891) == "R$ 1.234.567,89"


def test_missing_values_are_marked() -> None:
    assert NUMBER_FORMAT.integer(None) == "n/d"
    assert NUMBER_FORMAT.percentage(math.nan) == "n/d"


def test_compact_currency_chooses_unit() -> None:
    assert NUMBER_FORMAT.compact_currency(2_621_681) == "R$ 2,6 milhões"
    assert NUMBER_FORMAT.compact_currency(1_874_723) == "R$ 1,9 milhão"
    assert NUMBER_FORMAT.compact_currency(20_300) == "R$ 20,3 mil"
    assert NUMBER_FORMAT.compact_currency(950) == "R$ 950"


def test_signed_percentage_keeps_sign() -> None:
    assert NUMBER_FORMAT.signed_percentage(-0.291) == "-29,1%"
    assert NUMBER_FORMAT.signed_percentage(0.07) == "+7,0%"
