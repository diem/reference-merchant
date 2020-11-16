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
    image_url: str


PRODUCTS = {
    "00000001": Product(
            gtin="00000001",
            price=34250000,
            currency=FiatCurrency.USD.value,
            name="T-Shirt",
            description="The all new T-Shirt available now. Amazing purple / white colors!",
            quantity=1000,
            payment_type="direct",
            image_url="/images/t-shirt-purple.png"
        ),
    "00000002": Product(
            gtin="00000002",
            price=15890000,
            currency=FiatCurrency.EUR.value,
            name="Key Chain",
            description="The all new Key Chain available now in purple colors!",
            quantity=1000,
            payment_type="direct",
            image_url="/images/key-chain.png"
        ),
    "00000003": Product(
            gtin="00000003",
            price=21010000,
            currency=FiatCurrency.USD.value,
            name="Hat",
            description="The all new Hat available now. Amazing purple color!",
            quantity=1000,
            payment_type="direct",
            image_url="/images/hat.png"
        )
}


def get_product_details(gtin: str):
    if gtin in PRODUCTS:
        return PRODUCTS[gtin]
    else:
        return None


def get_products_list() -> Iterable[Product]:
    return PRODUCTS.values()
