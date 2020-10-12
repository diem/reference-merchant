import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from libra import identifier
from libra.jsonrpc import CurrencyInfo
from libra_utils.sdks import liquidity
from libra_utils.types.liquidity.currency import CurrencyPairs
from libra_utils.types.liquidity.lp import LPDetails
from libra_utils.types.liquidity.quote import Rate, QuoteData
from libra_utils.types.liquidity.trade import TradeId

from merchant_vasp.storage import (
    db_session,
    clear_db,
    Merchant,
    Payment,
    PaymentOption,
    PaymentStatus,
)
from webapp import app

TOKEN_1 = "mailmen111"
TOKEN_2 = "mailmen222"
PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d1"
CLEARED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d2"
CLEARED_PAYMENT_SUBADDR = "ffffffffffffffff"
CLEARED_TX_ID = 7000282
REJECTED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d3"
EXPIRED_PAYMENT_ID = "00000000-0000-7777-0000-00000000d0d4"
REFUND_TX_ID = 7000289
PAYOUT_TX_ID = 7000281
TRANSACTION_ORIGIN = "BLAH"
CREATED_ORDER_ID = "4"
CLEARED_ORDER_ID = "5"
REJECTED_ORDER_ID = "REJ"
EXPIRED_ORDER_ID = "EXP"
PAYMENT_TX_ID = 5555
PAYMENT_AMOUNT = 234
PAYMENT_CURRENCY = "LBR"
PAYMENT_AMOUNT_2 = 432
PAYMENT_CURRENCY_2 = "Coin1"
PAYMENT_SUBADDR = "aaaaaaaaaaaaaaaa"
EXPIRED_PAYMENT_SUBADDR = "bbbbbbbbbbbbbbbc"
REJECTED_PAYMENT_SUBADDR = "bbbbbbbbbbbbbbbb"

MERCHANT_MOCK_ADDR = "M" * 32
MERCHAND_CURRENCY = "USD"
SENDER_MOCK_ADDR = "B" * 32
SENDER_MOCK_SUBADDR = "ffffffffffffffff"

GOOD_AUTH = {"Authorization": f"Bearer {TOKEN_1}"}

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
    "LBR",
    "Coin1",
    "Coin2",
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
    CurrencyInfo(
        code="Coin2",
        scaling_factor=1000000,
        fractional_part=100,
        to_lbr_exchange_rate=0.5,
        mint_events_key="",
        burn_events_key="",
        preburn_events_key="",
        cancel_burn_events_key="",
        exchange_rate_update_events_key="",
    ),
    CurrencyInfo(
        code="LBR",
        scaling_factor=1000000,
        fractional_part=1000,
        to_lbr_exchange_rate=1.0,
        mint_events_key="",
        burn_events_key="",
        preburn_events_key="",
        cancel_burn_events_key="",
        exchange_rate_update_events_key="",
    ),
]

MOCK_QUOTE = QuoteData(
    quote_id=UUID("f24d20f8-e49c-4303-a736-afec37f7f7f3"),
    rate=Rate(pair=CurrencyPairs.LBR_Coin1, rate=1040000),
    expires_at=datetime(
        2020, 7, 5, 16, 47, 49, 452315, tzinfo=timezone(timedelta(seconds=10800), "IDT")
    ),
    amount=100,
)

MOCK_TRADE = TradeId(UUID("f24d20f8-0011-4206-9736-afec37f7f7f3"))

MOCK_LP_DETAILS = LPDetails(
    sub_address="waka" * 8, vasp="b" * 32, IBAN_number="1" * 64,
)


# TODO - rescope
@pytest.fixture()
def db(mocker):
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
                currency=PAYMENT_CURRENCY_2,
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
        sender_address=identifier.encode_account(SENDER_MOCK_ADDR, SENDER_MOCK_SUBADDR),
        amount=10,
        currency="LBR",
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


@pytest.fixture()
def client(db, mocker):
    app.config["TESTING"] = True

    mocker.patch.object(liquidity.LpClient, "get_quote", return_value=MOCK_QUOTE)
    mocker.patch.object(
        liquidity.LpClient, "trade_and_execute", return_value=MOCK_TRADE
    )
    mocker.patch.object(liquidity.LpClient, "lp_details", return_value=MOCK_LP_DETAILS)
    with app.test_client() as client:
        yield client
