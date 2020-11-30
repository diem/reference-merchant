import json
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
# FIXME: DM
from diem import identifier
from diem.jsonrpc import CurrencyInfo
from diem.testnet import CHAIN_ID
from diem_utils.custody import Custody
from diem_utils.types.currencies import DEFAULT_DIEM_CURRENCY
from diem_utils.types.liquidity.currency import CurrencyPairs
from diem_utils.types.liquidity.lp import LPDetails
from diem_utils.types.liquidity.quote import QuoteData, Rate
from diem_utils.types.liquidity.trade import TradeId

from merchant_vasp.config import CHAIN_HRP
from merchant_vasp.storage import (
    db_session,
    clear_db,
    Merchant,
    Payment,
    PaymentOption,
    PaymentStatus,
)

CHECKOUT_ARGS = lambda: {
    "amount": 8.12,
    "requested_currency": "USD",
    "merchant_reference_id": str(random.randint(200, 2000)),
}

MOCK_SUPPORTED_CURRENCIES = [
    "USD",
    "EUR",
    "GBP",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
    "JPY",
    # FIXME: DM
    DEFAULT_DIEM_CURRENCY,
]

MOCK_NETWORK_SUPPORTED_CURRENCIES = [
    CurrencyInfo(
        code="Coin1",
        scaling_factor=1000000,
        fractional_part=100,
        to_lbr_exchange_rate=0.5,
        mint_events_key="",
        burn_events_key="",
        preburn_events_key="",
        cancel_burn_events_key="",
        exchange_rate_update_events_key="",
    ),
]

MOCK_QUOTE = QuoteData(
    quote_id=UUID("f24d20f8-e49c-4303-a736-afec37f7f7f3"),
    rate=Rate(pair=CurrencyPairs.Coin1_USD, rate=1040000),
    expires_at=datetime(
        2020, 7, 5, 16, 47, 49, 452315, tzinfo=timezone(timedelta(seconds=10800), "IDT")
    ),
    amount=100,
)

MOCK_TRADE = TradeId(UUID("f24d20f8-0011-4206-9736-afec37f7f7f3"))

MOCK_LP_DETAILS = LPDetails(
    sub_address="waka" * 8, vasp="b" * 32, IBAN_number="1" * 64,
)

FAKE_WALLET_PRIVATE_KEY = (
    "682ddb5bcb41abd0a362fe3b332af32a9135abc8effbd75abe8ec6192e2b0c8b"
)
FAKE_WALLET_VASP_ADDR = "9135abc8effbd75abe8ec6192e2b0c8b"
FAKE_LIQUIDITY_PRIVATE_KEY = (
    "e3993257580a98855a5e068c579d06f036f92c7dac37c7b3094f78b2f26b3f00"
)
FAKE_LIQUIDITY_VASP_ADDR = "36f92c7dac37c7b3094f78b2f26b3f00"

TOKEN_1 = "mailmen111"
GOOD_AUTH = {"Authorization": f"Bearer {TOKEN_1}"}

MERCHANT_MOCK_ADDR = "M" * 32
MERCHAND_CURRENCY = "USD"
PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d1"
CLEARED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d2"
REJECTED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d3"
EXPIRED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d4"
CREATED_ORDER_ID = "4"
PAYMENT_SUBADDR = "aaaaaaaaaaaaaaaa"
PAYMENT_AMOUNT = 234
# FIXME: DM
PAYMENT_CURRENCY = DEFAULT_DIEM_CURRENCY
PAYMENT_AMOUNT_2 = 432
REFUND_TX_ID = 7000289
PAYOUT_TX_ID = 7000281
TRANSACTION_ORIGIN = "BLAH"
CLEARED_ORDER_ID = "5"
REJECTED_ORDER_ID = "REJ"
EXPIRED_ORDER_ID = "EXP"
PAYMENT_TX_ID = 5555
EXPIRED_PAYMENT_SUBADDR = "bbbbbbbbbbbbbbbc"
REJECTED_PAYMENT_SUBADDR = "bbbbbbbbbbbbbbbb"
SENDER_MOCK_ADDR = "B" * 32
SENDER_MOCK_SUBADDR = "ffffffffffffffff"
TOKEN_2 = "mailmen222"
CLEARED_PAYMENT_SUBADDR = "ffffffffffffffff"
CLEARED_TX_ID = 7000282


@pytest.fixture(autouse=True)
def init_test_onchainwallet(monkeypatch):
    monkeypatch.setenv("WALLET_CUSTODY_ACCOUNT_NAME", "test_wallet")
    monkeypatch.setenv("LIQUIDITY_CUSTODY_ACCOUNT_NAME", "test_liq")
    monkeypatch.setenv(
        "CUSTODY_PRIVATE_KEYS",
        json.dumps(
            {
                "test_wallet": FAKE_WALLET_PRIVATE_KEY,
                "test_liq": FAKE_LIQUIDITY_PRIVATE_KEY,
            }
        ),
    )

    Custody.init(CHAIN_ID)


# TODO - rescope
@pytest.fixture()
def db():
    clear_db()
    # Add Merchant and Payment for testing
    merchant = Merchant(
        api_key=TOKEN_1,
        settlement_information=MERCHANT_MOCK_ADDR,
        settlement_currency=MERCHAND_CURRENCY,
    )
    db_session.add(merchant)
    db_session.commit()

    payment = Payment(
        id=PAYMENT_ID,
        merchant_id=merchant.id,
        merchant_reference_id=CREATED_ORDER_ID,
        requested_amount=1,
        requested_currency="USD",
        subaddress=PAYMENT_SUBADDR,
        expiry_date=datetime.utcnow() + timedelta(minutes=10),
    )
    payment.payment_options.extend(
        [
            PaymentOption(
                payment_id=payment.id, amount=PAYMENT_AMOUNT, currency=PAYMENT_CURRENCY,
            ),
            PaymentOption(
                payment_id=payment.id,
                amount=PAYMENT_AMOUNT_2,
                currency=PAYMENT_CURRENCY,
            ),
        ]
    )

    cleared_payment = Payment(
        id=CLEARED_PAYMENT_ID,
        merchant_reference_id=CLEARED_ORDER_ID,
        merchant_id=merchant.id,
        requested_amount=10,
        requested_currency="USD",
        status=PaymentStatus.cleared,
        subaddress="f3704755d1100cd2",
        expiry_date=datetime.utcnow() - timedelta(minutes=10),
    )
    cleared_payment.payment_options.append(
        PaymentOption(
            payment_id=cleared_payment.id,
            amount=cleared_payment.requested_amount,
            currency=cleared_payment.requested_currency,
        )
    )
    cleared_payment.add_chain_transaction(
        sender_address=identifier.encode_account(SENDER_MOCK_ADDR, SENDER_MOCK_SUBADDR, CHAIN_HRP),
        amount=10,
        # FIXME: DM
        currency=DEFAULT_DIEM_CURRENCY,
        tx_id=CLEARED_TX_ID,
    )

    rejected_payment = Payment(
        id=REJECTED_PAYMENT_ID,
        merchant_id=merchant.id,
        merchant_reference_id=REJECTED_ORDER_ID,
        status=PaymentStatus.rejected,
        requested_amount=100,
        requested_currency="USD",
        expiry_date=datetime.utcnow(),
        subaddress=REJECTED_PAYMENT_SUBADDR,
    )

    expired_payment = Payment(
        id=EXPIRED_PAYMENT_ID,
        merchant_id=merchant.id,
        merchant_reference_id=EXPIRED_ORDER_ID,
        requested_amount=100,
        requested_currency="USD",
        subaddress=EXPIRED_PAYMENT_SUBADDR,
        expiry_date=datetime.utcnow() - timedelta(seconds=1),
    )

    db_session.add(rejected_payment)
    db_session.add(cleared_payment)
    db_session.add(expired_payment)
    db_session.add(payment)

    db_session.commit()

    yield db_session
