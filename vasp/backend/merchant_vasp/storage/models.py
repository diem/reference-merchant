# pyre-ignore-all-errors
import uuid
import enum
import secrets
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    BigInteger,
    Float,
    event,
)
from sqlalchemy.orm import relationship
from . import Base, db_session


class Merchant(Base):
    __tablename__ = "merchant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=True)
    settlement_information = Column(String, unique=False, nullable=True)
    settlement_currency = Column(String, unique=False, nullable=True)
    api_key = Column(String, unique=True, default=lambda: secrets.token_urlsafe(64))

    payments = relationship("Payment", lazy=True)

    @staticmethod
    def find_by_token(token: str):
        return Merchant.query.filter_by(api_key=token).first()


class PaymentStatus(str, enum.Enum):
    created = "created"
    cleared = "cleared"
    rejected = "rejected"
    error = "error"

    payout_processing = "payout_processing"
    payout_completed = "payout_completed"

    refund_requested = "refund_requested"
    refund_rejected = "refund_rejected"
    refund_completed = "refund_completed"
    refund_error = "refund_error"


class RefundStatus(str, enum.Enum):
    none = "none"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_reference_id = Column(String, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchant.id"), index=True, nullable=False)
    # payment_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    requested_amount = Column(BigInteger, nullable=False)
    requested_currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default=PaymentStatus.created)
    refund_requested = Column(Boolean, nullable=False, default=False)
    last_update = Column(DateTime, nullable=True)  # TODO - meta field setup
    subaddress = Column(String, unique=True, nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    payment_options = relationship("PaymentOption", lazy=False)
    chain_transactions = relationship("ChainTransaction", lazy=False)
    payment_status_logs = relationship("PaymentStatusLog", lazy=True)

    merchant = relationship("Merchant", foreign_keys="Payment.merchant_id", lazy=True)

    @staticmethod
    def add_payment(new_payment):
        db_session.add(new_payment)
        db_session.commit()

    @staticmethod
    def find_by_merchant_reference_id(merchant_id: int, merchant_reference_id: str):
        return Payment.query.filter_by(
            merchant_id=merchant_id, merchant_reference_id=merchant_reference_id
        ).one_or_none()

    @staticmethod
    def find_by_subaddress(subaddress: str):
        return Payment.query.filter_by(subaddress=subaddress).one_or_none()

    @staticmethod
    def find_by_public_token(public_token: str):
        return Payment.query.filter_by(public_token=public_token).one_or_none()

    def is_expired(self):
        return self.expiry_date <= datetime.utcnow()

    def is_payment_option_valid(self, amount: int, currency: str):
        return (
            PaymentOption.query.filter_by(
                payment_id=self.id, amount=amount, currency=currency
            ).one_or_none()
            is not None
        )

    def set_status(self, status: PaymentStatus):
        if (
            status in (PaymentStatus.refund_requested, PaymentStatus.payout_processing)
            and self.status != PaymentStatus.cleared
        ):
            raise ValueError(f"Cannot change {self.status} to {status}")
        self.status = status
        status_log = PaymentStatusLog(payment_id=self.id, status=status)
        self.payment_status_logs.append(status_log)

    def add_chain_transaction(
        self,
        sender_address: str,
        amount: int,
        currency: int,
        tx_id: int,
        is_refund: bool = False,
    ):
        self.chain_transactions.append(
            ChainTransaction(
                payment_id=self.id,
                sender_address=sender_address,
                amount=amount,
                currency=currency,
                tx_id=tx_id,
                is_refund=is_refund,
            )
        )
        db_session.commit()

    def get_chain_transaction(self, tx_id: int):
        return ChainTransaction.query.filter_by(tx_id=tx_id).one_or_none()


@event.listens_for(Payment, "after_insert")
def set_initial_status(mapper, connect, target):
    target.set_status(target.status)


class ChainTransaction(Base):
    __tablename__ = "chain_transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String, ForeignKey("payment.id"), nullable=False)
    sender_address = Column(String, nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String, nullable=False)
    is_refund = Column(Boolean, nullable=False, default=False)
    tx_id = Column(Integer, nullable=False)  # version


class PaymentOption(Base):
    __tablename__ = "payment_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String, ForeignKey("payment.id"), nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String, nullable=False)


class PaymentStatusLog(Base):
    __tablename__ = "payment_status_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String, ForeignKey("payment.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)
