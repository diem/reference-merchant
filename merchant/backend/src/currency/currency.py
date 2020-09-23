import typing
from enum import Enum


class LibraCurrency(str, Enum):
    LBR = "LBR"
    Coin1 = "Coin1"
    Coin2 = "Coin2"


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
