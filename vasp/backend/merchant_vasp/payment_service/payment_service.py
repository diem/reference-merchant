import logging
from typing import Tuple

import pyqrcode
from libra import identifier, jsonrpc, testnet
from libra_utils.types.currencies import FiatCurrency, LibraCurrency

from .payment_exceptions import *
from ..onchainwallet import OnchainWallet
from ..storage import Payment, PaymentStatus, db_session

logger = logging.getLogger(__name__)


def get_supported_network_currencies() -> Tuple[str]:
    # TODO - error handling
    api = jsonrpc.Client(testnet.JSON_RPC_URL)
    supported_currency_info = api.get_currencies()

    return tuple(_.code for _ in supported_currency_info)


def get_supported_currencies() -> Tuple[str]:
    # TODO - error handling
    supported_currency_info = [_.value for _ in FiatCurrency] + [
        _.value for _ in LibraCurrency
    ]

    return tuple(supported_currency_info)


def process_incoming_transaction(
        version,
        sender_address,
        sender_sub_address,
        receiver_address,
        receiver_sub_address,
        amount,
        currency,
) -> None:
    """This function receives incoming payment events from the chain"""
    # Check if the payment is intended for us - this address is configured via environment variable, see config.py
    if receiver_address != OnchainWallet().address_str:
        logging.debug("Received payment to unknown base address.")
        raise WrongReceiverAddressException("wrongaddr")

    # Locate payment id and payment options related to the given subaddress
    payment = Payment.find_by_subaddress(receiver_sub_address)
    if payment is None:
        logging.debug(
            f"Could not find the qualifying payment {receiver_sub_address}, ignoring."
        )
        # TODO - Process for errant payments?
        raise PaymentForSubaddrNotFoundException("wrongsubaddr")

    if payment.status != PaymentStatus.created:
        logging.debug(f"Payment status is invalid: {payment.status}")
        raise PaymentStatusException("invalidpaymentstatus")

    if payment.is_expired():
        logging.debug(f"Payment expired: {payment.expiry_date}. Rejecting.")
        payment.set_status(PaymentStatus.rejected)
        db_session.commit()
        # TODO - Do we need a reaper process to simply mark expired payments as such?
        raise PaymentExpiredException("paymentexpired")

    # verify payment matches any of the payment options for this payment id
    if not payment.is_payment_option_valid(amount, currency):
        logging.debug(
            "Payment does not match any of the relevant payment options, ignoring."
        )
        # TODO - Set status to rejected here or ignore?
        raise PaymentOptionNotFoundException("paymentoptionnotfound")

    # We're good - mark as cleared
    logging.debug(f"Clearing payment id {payment.id}")
    payment.set_status(PaymentStatus.cleared)
    # version is tx_id

    payment.add_chain_transaction(
        identifier.encode_account(sender_address, sender_sub_address),
        amount,
        currency,
        version,
    )
    db_session.commit()


def generate_payment_options_with_qr(payment):
    payment_options_with_qr = []

    vasp_addr = OnchainWallet().address_str
    logger.debug(f"Current vasp address: {vasp_addr}")
    full_payment_addr = identifier.encode_account(vasp_addr, payment.subaddress)
    logger.debug(f"Rendering full payment link: {full_payment_addr}")

    bech32addr = identifier.encode_account(vasp_addr, payment.subaddress)

    for payment_option in payment.payment_options:
        payment_link = f"libra://{bech32addr}?c={payment_option.currency}&am={payment_option.amount}"
        payment_option_attributes = dict(
            address=bech32addr,
            currency=payment_option.currency,
            amount=payment_option.amount,
            payment_link=payment_link,
        )
        qr = pyqrcode.create(payment_link)
        payment_option_attributes["qr_b64"] = qr.png_as_base64_str(scale=10)

        payment_options_with_qr.append(payment_option_attributes)

    return payment_options_with_qr
