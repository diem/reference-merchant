import pytest

from webapp import app


@pytest.fixture(autouse=True)
def client():
    app.config["TESTING"] = True

    # mocker.patch.object(liquidity.LpClient, "get_quote", return_value=MOCK_QUOTE)
    # mocker.patch.object(
    #     liquidity.LpClient, "trade_and_execute", return_value=MOCK_TRADE
    # )
    # mocker.patch.object(liquidity.LpClient, "lp_details", return_value=MOCK_LP_DETAILS)
    with app.test_client() as client:
        yield client
