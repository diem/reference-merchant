import json
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
# FIXME: DM
from libra.jsonrpc import CurrencyInfo
from libra_utils.custody import Custody
from libra_utils.sdks import liquidity
from libra_utils.types.currencies import DEFAULT_LIBRA_CURRENCY
from libra_utils.types.liquidity.currency import CurrencyPairs
from libra_utils.types.liquidity.lp import LPDetails
from libra_utils.types.liquidity.quote import QuoteData, Rate
from libra_utils.types.liquidity.trade import TradeId

from webapp import app

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
    DEFAULT_LIBRA_CURRENCY,
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

    Custody.init()


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
