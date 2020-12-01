from dataclasses import dataclass

from .amount import Amount
from .currency import FiatCurrency


@dataclass
class Price:
    amount: Amount
    currency: FiatCurrency
