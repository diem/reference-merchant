import pytest
from libra_utils.types.currencies import DEFAULT_LIBRA_CURRENCY

from merchant_vasp import payment_service
from merchant_vasp.onchainwallet import OnchainWallet
from merchant_vasp.storage import Payment, PaymentStatus
from ..webapp.conftest import (
    REJECTED_PAYMENT_SUBADDR,
    SENDER_MOCK_ADDR,
    SENDER_MOCK_SUBADDR,
    EXPIRED_PAYMENT_SUBADDR,
    PAYMENT_SUBADDR,
    PAYMENT_AMOUNT,
    PAYMENT_CURRENCY,
    PAYMENT_ID,
)

CURRENCY = DEFAULT_LIBRA_CURRENCY


def test_payment_to_wrong_address(db):
    with pytest.raises(
            payment_service.WrongReceiverAddressException, match="wrongaddr"
    ) as e:
        payment_service.process_incoming_transaction(
            version=0,
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address="cccccccccccccccccccccccccccccccc",  # wrong addr
            receiver_sub_address="ffffffffffffffff",
            amount=100,
            currency=CURRENCY,
        )


def test_payment_to_wrong_sub_address(db):
    with pytest.raises(
            payment_service.PaymentForSubaddrNotFoundException, match="wrongsubaddr"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address="ffffffffffffffff",  # wrong sub address
            amount=100,
            currency=CURRENCY,
            version=0,
        )


def test_payment_status_invalid(db):
    with pytest.raises(
            payment_service.PaymentStatusException, match="invalidpaymentstatus"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address=REJECTED_PAYMENT_SUBADDR,
            amount=100,
            currency=CURRENCY,
            version=0,
        )


def test_payment_expired(db):
    with pytest.raises(
            payment_service.PaymentExpiredException, match="paymentexpired"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address=EXPIRED_PAYMENT_SUBADDR,
            amount=100,
            currency=CURRENCY,
            version=0,
        )


def test_invalid_payment_amount(db):
    with pytest.raises(
            payment_service.PaymentOptionNotFoundException, match="paymentoptionnotfound"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address=PAYMENT_SUBADDR,
            amount=PAYMENT_AMOUNT - 1,  # underpaying
            currency=PAYMENT_CURRENCY,
            version=0,
        )

    with pytest.raises(
            payment_service.PaymentOptionNotFoundException, match="paymentoptionnotfound"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address=PAYMENT_SUBADDR,
            amount=PAYMENT_AMOUNT + 1,  # overpaying
            currency=PAYMENT_CURRENCY,
            version=0,
        )


def test_invalid_payment_currency(db):
    with pytest.raises(
            payment_service.PaymentOptionNotFoundException, match="paymentoptionnotfound"
    ) as e:
        payment_service.process_incoming_transaction(
            sender_address=SENDER_MOCK_ADDR,
            sender_sub_address=SENDER_MOCK_SUBADDR,
            receiver_address=OnchainWallet().address_str,
            receiver_sub_address=PAYMENT_SUBADDR,
            amount=PAYMENT_AMOUNT,
            currency="USD",
            version=0,
        )


def test_successful_payment(db):
    payment_version = 808
    payment_service.process_incoming_transaction(
        sender_address=SENDER_MOCK_ADDR,
        sender_sub_address=SENDER_MOCK_SUBADDR,
        receiver_address=OnchainWallet().address_str,
        receiver_sub_address=PAYMENT_SUBADDR,
        amount=PAYMENT_AMOUNT,
        currency=PAYMENT_CURRENCY,
        version=payment_version,
    )

    payment = db.query(Payment).filter(Payment.id == PAYMENT_ID).one()
    assert payment.status == PaymentStatus.cleared
    assert payment.get_chain_transaction(payment_version) is not None
