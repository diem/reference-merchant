import typing
from enum import Enum


class LibraCurrency(str, Enum):
    Coin1 = "Coin1"


class FiatCurrency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    NZD = "NZD"
    JPY = "JPY"


Currency = typing.Union[FiatCurrency, LibraCurrency]
