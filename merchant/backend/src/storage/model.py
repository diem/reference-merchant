import uuid
from datetime import datetime

from sqlalchemy import MetaData, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    BigInteger,
    Enum,
)

from currency import FiatCurrency


StorageBase = declarative_base(metadata=MetaData())


class HasPrice:
    price = Column(BigInteger, nullable=False)
    currency = Column(
        Enum(FiatCurrency, native_enum=False, create_constraint=False), nullable=False
    )


class Order(HasPrice, StorageBase):
    __tablename__ = "order"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    vasp_payment_reference = Column(String, nullable=True)
    items = relationship("OrderItem", back_populates="order")


class OrderItem(HasPrice, StorageBase):
    __tablename__ = "order_item"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_gtin = Column(String, nullable=False)
    product_quantity = Column(Integer, nullable=False)

    order_id = Column(String, ForeignKey("order.id"), nullable=False)
    order = relationship("Order", back_populates="items")
