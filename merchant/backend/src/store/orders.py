from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from storage import storage
from .products import get_product_details


@dataclass
class OrderItem:
    gtin: str
    quantity: int

    @staticmethod
    def from_storage(item: storage.OrderItem):
        return OrderItem(gtin=item.product_gtin, quantity=item.product_quantity)


@dataclass
class Order:
    order_id: UUID
    created_at: datetime
    vasp_payment_reference: str
    items: List[OrderItem]
    total_price: int
    currency: str

    @staticmethod
    def from_storage(order: storage.Order):
        return Order(
            order_id=UUID(order.id),
            created_at=order.created_at,
            vasp_payment_reference=order.vasp_payment_reference,
            total_price=order.price,
            currency=order.currency.value,
            items=[OrderItem.from_storage(item) for item in order.items],
        )


def create_order(items: List[OrderItem]) -> Order:
    storage_items = []
    for item in items:
        product = get_product_details(item.gtin)
        storage_items.append(
            storage.OrderItem(
                product_gtin=item.gtin,
                product_quantity=item.quantity,
                price=product.price,
                currency=product.currency,
            )
        )

    storage_order = storage.create_order(storage_items)
    return Order.from_storage(storage_order)


def set_order_payment_reference(order_id: UUID, payment_ref: str):
    storage.set_order_payment_reference(str(order_id), payment_ref)


def get_order_details(order_id: UUID) -> Order:
    return Order.from_storage(storage.get_order_details(str(order_id)))
