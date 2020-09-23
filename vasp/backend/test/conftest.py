import json

import pytest
from libra_utils.custody import Custody

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
