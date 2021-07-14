# VASP imports
import logging
import secrets
from datetime import datetime, timedelta

from diem import utils, identifier
from diem_utils.types.currencies import DiemCurrency

from merchant_vasp import payment_service
from merchant_vasp.config import PAYMENT_EXPIRE_MINUTES, CHAIN_HRP
from merchant_vasp.fiat_liquidity_wrapper import FiatLiquidityWrapper
from merchant_vasp.onchainwallet import OnchainWallet
from merchant_vasp.storage import (
    Payment,
    PaymentOption,
    db_session,
)
from merchant_vasp.storage.models import PaymentStatus, Merchant

logger = logging.getLogger(__name__)


class InvalidPaymentStatus(ValueError):
    def __init__(self, message):
        self.message = message


class TakenMerchantReferenceId(ValueError):
    def __init__(self):
        pass


def create_payment(currency, merchant_reference_id, amount, merchant_id):
    existing_order = Payment.find_by_merchant_reference_id(
        merchant_id, merchant_reference_id
    )
    if existing_order is not None:
        raise TakenMerchantReferenceId

    sub_address = secrets.token_hex(identifier.DIEM_SUBADDRESS_SIZE)
    new_payment = Payment(
        merchant_id=merchant_id,
        requested_currency=currency,
        merchant_reference_id=merchant_reference_id,
        requested_amount=amount,
        expiry_date=datetime.utcnow() + timedelta(minutes=PAYMENT_EXPIRE_MINUTES),
        subaddress=sub_address,
    )
    # Create a payment option per currency, so client can choose
    # their preferred one for paying for this order.
    # Liquidity provider provides us with current rates.
    liquidity = FiatLiquidityWrapper(currency)
    for quote_currency in payment_service.get_supported_network_currencies():
        quote_price = liquidity.quote_price(quote_currency, amount)

        new_payment.payment_options.append(
            PaymentOption(
                payment_id=new_payment.id,
                amount=quote_price,
                currency=quote_currency,
            )
        )
    Payment.add_payment(new_payment)
    logger.debug(
        f"Adding new payment (id {new_payment.id}) to sub address {new_payment.subaddress}"
    )
    return new_payment


def refund(payment):
    if not payment_can_refund(payment):
        raise InvalidPaymentStatus("unclearedrefund")

    if not len(payment.chain_transactions) == 1:
        raise InvalidPaymentStatus("chain_transactions")
    # TODO - support refund of multiple payments

    # TODO - Resolve refund address, currency and amount from blockchain

    target_transaction = payment.chain_transactions[0]
    if target_transaction.is_refund:
        raise InvalidPaymentStatus("refund_transaction")

    refund_target_address, refund_target_sub_address = identifier.decode_account(
        target_transaction.sender_address, CHAIN_HRP
    )
    refund_target_address = utils.account_address_hex(refund_target_address)
    refund_target_sub_address = refund_target_sub_address.hex()

    refund_amount = target_transaction.amount  # payment.requested_amount
    refund_currency = DiemCurrency(target_transaction.currency)

    payment.set_status(PaymentStatus.refund_requested)

    refund_tx_id = None

    try:
        wallet = OnchainWallet()

        refund_tx_id, _ = wallet.send_transaction(
            refund_currency,
            refund_amount,
            refund_target_address,
            refund_target_sub_address,  # TODO - new sub_address for refund?
        )
        payment.add_chain_transaction(
            amount=refund_amount,
            sender_address=wallet.address_str,
            currency=refund_currency,
            tx_id=refund_tx_id,
            is_refund=True,
        )
        payment.set_status(PaymentStatus.refund_completed)
    except Exception as e:  # TODO - narrow to blockchain exception
        logger.exception("Failed during refund")
        payment.set_status(PaymentStatus.refund_error)

    return refund_tx_id, target_transaction


def payout(merchant: Merchant, payment: Payment):
    if not payment_can_payout(payment):
        raise InvalidPaymentStatus("invalid_status")

    settlement_information = merchant.settlement_information
    settlement_currency = merchant.settlement_currency
    if (
        settlement_information
        in (
            None,
            "",
        )
        or settlement_currency in (None, "")
    ):
        raise InvalidPaymentStatus("invalid_merchant_information")

    client_payments = [
        transaction
        for transaction in payment.chain_transactions
        if transaction.is_refund is False
    ]
    if 1 != len(client_payments):
        raise InvalidPaymentStatus("invalid_transaction")
    client_payment = client_payments[0]

    # 1. Get liquidity quote
    liquidity_provider = FiatLiquidityWrapper(client_payment.currency)
    payment.set_status(PaymentStatus.payout_processing)
    db_session.commit()
    # 2. Send requested amount
    payout_target, quote = liquidity_provider.pay_out(
        settlement_currency,
        client_payment.amount,
        merchant.settlement_information,
    )
    # 3. Pay according to quote to payout_target
    tx_id, _ = OnchainWallet().send_transaction(
        DiemCurrency(client_payment.currency),
        client_payment.amount,
        liquidity_provider.vasp_address(),
        payout_target.bytes[: utils.SUB_ADDRESS_LEN].hex(),
    )
    payment.set_status(PaymentStatus.payout_completed)
    db_session.commit()

    return payout_target, quote, tx_id, settlement_information


def get_payment_events(payment):
    return [
        {
            "created_at": payment_log.created_at,
            "status": payment_log.status,
        }
        for payment_log in payment.payment_status_logs
    ]


def get_merchant_full_addr(payment):
    return identifier.encode_account(
        OnchainWallet().address_str, payment.subaddress, CHAIN_HRP
    )


def get_merchant_payments(merchant):
    return [
        {
            "payment_id": payment.id,
            "created_at": payment.created_at,
            "status": payment.status,
            "refund_requested": payment.refund_requested,
        }
        for payment in merchant.payments
    ]


def load_payment(payment_id: str):
    return Payment.query.get(payment_id)


def load_merchant_payment_id(merchant_reference_id: str, merchant: Merchant):
    return Payment.find_by_merchant_reference_id(merchant.id, merchant_reference_id)


def payment_can_payout(payment: Payment):
    return payment.status == PaymentStatus.cleared


payment_can_refund = payment_can_payout


def payment_chain_txs(payment: Payment):
    return [
        {
            "tx_id": tx.tx_id,
            "is_refund": tx.is_refund,
            "sender_address": tx.sender_address,
            "amount": tx.amount,
            "currency": tx.currency,
        }
        for tx in payment.chain_transactions
    ]


def payment_can_pay(payment: Payment):
    return (
        payment.status == PaymentStatus.created
        and payment.expiry_date >= datetime.utcnow()
    )


def request_refund(payment):
    if not payment_can_refund(payment):
        raise InvalidPaymentStatus("unclearedrefund")

    payment.refund_requested = True
    db_session.commit()
