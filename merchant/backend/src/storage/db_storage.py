# pyre-ignore-all-errors

# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

import os
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .model import StorageBase, Order, OrderItem

DB_URL = os.getenv("DB_URL", "sqlite:////tmp/merchant.db")


session = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def configure():
    connect_args = {}
    if DB_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    StorageBase.metadata.bind = create_engine(DB_URL, connect_args=connect_args)


def create_storage():
    StorageBase.metadata.create_all()


def setup():
    configure()
    create_storage()


def cleanup():
    session.remove()


def reset_storage():
    StorageBase.metadata.drop_all()
    StorageBase.metadata.create_all()


def create_order(items: List[OrderItem]) -> Order:
    currency = items[0].currency

    total_price = 0
    for item in items:
        total_price += item.price
        if item.currency != currency:
            raise ValueError("Different currencies in the same order not supported")

    order = Order(price=total_price, currency=currency)
    order.items = items

    session.add(order)
    session.commit()

    return order


def get_order_details(order_id: str) -> Order:
    return session.query(Order).get(order_id)


def set_order_payment_reference(order_id: str, payment_ref: str):
    order = session.query(Order).get(order_id)
    order.vasp_payment_reference = payment_ref
    session.commit()
