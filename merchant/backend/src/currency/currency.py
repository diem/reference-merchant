import typing
from enum import Enum


class DiemCurrency(str, Enum):
    XUS = "XUS"


class FiatCurrency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    NZD = "NZD"
    JPY = "JPY"


Currency = typing.Union[FiatCurrency, DiemCurrency]
