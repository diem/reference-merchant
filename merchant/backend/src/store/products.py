from dataclasses import dataclass
from typing import Iterable

from dataclasses_json import dataclass_json

from currency import Amount, FiatCurrency, Price


@dataclass_json
@dataclass
class Product:
    gtin: str
    price: int
    currency: str
    name: str
    description: str
    quantity: int
    payment_type: str


PRODUCTS = {
    "00000001": Product(
        gtin="00000001",
        price=34250000,
        currency=FiatCurrency.USD.value,
        name="Libra T-Shirt",
        description="The all new Libra T-Shirt available now. Amazing black / white colors!",
        quantity=1000,
        payment_type="direct",
    )
}


def get_product_details(gtin: str):
    if gtin in PRODUCTS:
        return PRODUCTS[gtin]
    else:
        return None


def get_products_list() -> Iterable[Product]:
    return PRODUCTS.values()
