from dataclasses import dataclass, field, Field
from datetime import datetime
from typing import List, Optional

from dataclasses_json import dataclass_json, config
from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Range, Length

from libra_utils.types.currencies import FiatCurrency


def fiat_amount_field() -> Field:
    """Defines fiat currency amount schema field"""
    return field(
        metadata=config(
            mm_field=fields.Int(
                description="Amount of fiat currency in scale factor 6",
                validate=Range(min=1),
                strict=True,
            )
        )
    )


def fiat_currency_code_field() -> Field:
    """Defines fiat currency code schema field"""
    return field(
        metadata=config(
            mm_field=fields.Str(
                description="Fiat currency code",
                validate=OneOf(list(FiatCurrency.__members__)),
            )
        )
    )


def global_trade_item_number_field() -> Field:
    """Defines a schema field containing Global Trade Item Number (GTIN)"""
    return field(
        metadata=config(
            mm_field=fields.Str(
                description="Global Trade Item Number (GTIN)",
                validate=Length(min=8, max=14),
            )
        )
    )


@dataclass_json
@dataclass
class Product:
    name: str
    description: str
    payment_type: str
    gtin: str = global_trade_item_number_field()
    price: int = fiat_amount_field()
    currency: str = fiat_currency_code_field()


@dataclass_json
@dataclass
class ProductList:
    products: List[Product]


@dataclass_json
@dataclass
class CheckoutItem:
    quantity: int
    gtin: str = global_trade_item_number_field()


@dataclass_json
@dataclass
class CheckoutRequest:
    items: List[CheckoutItem]


class CheckoutResponse(Schema):
    order_id = fields.UUID(required=True)
    vasp_payment_id = fields.UUID(required=True)
    payment_form_url = fields.URL(require_tld=False, required=True)


@dataclass_json
@dataclass
class PaymentEvent:
    timestamp: datetime
    event_type: str


@dataclass_json
@dataclass
class BlockchainTx:
    tx_id: int
    is_refund: bool


@dataclass_json
@dataclass
class PaymentStatus:
    status: str
    merchant_address: str
    can_payout: bool
    can_refund: bool
    events: List[PaymentEvent]
    chain_txs: Optional[List[BlockchainTx]]


@dataclass_json
@dataclass
class ProductOrder:
    product: Product
    quantity: int


@dataclass_json
@dataclass
class OrderDetails:
    order_id: str
    created_at: datetime
    vasp_payment_reference: str
    payment_status: Optional[PaymentStatus]
    products: List[ProductOrder]
    total_price: int = fiat_amount_field()
    currency: str = fiat_currency_code_field()
