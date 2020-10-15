from http import HTTPStatus

from libra_utils.vasp import Vasp

from merchant_vasp.config import PAYMENT_EXPIRE_MINUTES
from merchant_vasp.payment_service import payment_service
from merchant_vasp.storage.models import PaymentStatusLog
from .conftest import *


@pytest.fixture
def mock_get_supported_network_currencies(monkeypatch):
    def get_supported_network_currencies_impl():
        return DEFAULT_LIBRA_CURRENCY

    monkeypatch.setattr(
        payment_service,
        "get_supported_network_currencies",
        get_supported_network_currencies_impl,
    )


def test_supported_network_currencies(
    client, mocker, mock_get_supported_network_currencies
):
    currencies = (_.code for _ in MOCK_NETWORK_SUPPORTED_CURRENCIES)
    data = client.get("/supported_network_currencies").get_json()
    assert len(data["currencies"]) > 0
    for c in currencies:
        assert c in data["currencies"]


def test_supported_currencies(client, mocker):
    currencies = MOCK_SUPPORTED_CURRENCIES
    data = client.get("/supported_currencies").get_json()
    assert len(data["currencies"]) > 0
    for c in currencies:
        assert c in data["currencies"]


def test_get_nonexisting_payment(client):
    rv = client.get(f"/payments/x/status", headers=GOOD_AUTH)
    assert HTTPStatus.NOT_FOUND == rv.status_code
    assert rv.get_json() == {"error": "notfound"}


def test_get_existing_payment_wrong_user(client):
    rv = client.get(f"/payments/{CREATED_ORDER_ID}/status", headers={"token": TOKEN_2})
    assert HTTPStatus.UNAUTHORIZED == rv.status_code
    assert rv.get_json() == {"error": "noauth"}


def test_get_nonauthenticated_payment(client):
    rv = client.get(f"/payments/{CREATED_ORDER_ID}/status")
    assert HTTPStatus.UNAUTHORIZED == rv.status_code
    assert rv.get_json() == {"error": "noauth"}


def test_get_payment(client):
    rv = client.get(f"/payments/{CREATED_ORDER_ID}/status", headers=GOOD_AUTH)
    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()
    assert data["status"] == "created"
    time_difference = (
        datetime.fromisoformat(data["expiry_date"]) - datetime.utcnow()
    ).total_seconds() - PAYMENT_EXPIRE_MINUTES * 60
    assert time_difference <= 10


def test_checkout_noauth(client):
    rv = client.post("/payments", json=CHECKOUT_ARGS())
    assert HTTPStatus.UNAUTHORIZED == rv.status_code


def test_checkout_nonjson(client):
    rv = client.post("/payments", data=CHECKOUT_ARGS(), headers=GOOD_AUTH)
    assert HTTPStatus.BAD_REQUEST == rv.status_code


def test_checkout_success(client):
    rv = client.post("/payments", json=CHECKOUT_ARGS(), headers=GOOD_AUTH)
    data = rv.get_json()
    assert HTTPStatus.OK == rv.status_code

    time_difference = (
        datetime.fromisoformat(data["expiry_date"]) - datetime.utcnow()
    ).total_seconds()

    assert (
        (PAYMENT_EXPIRE_MINUTES * 60) - 3
        <= time_difference
        <= (PAYMENT_EXPIRE_MINUTES * 60) + 3
    )
    assert "http:" in data["payment_form_url"] or "https:" in data["payment_form_url"]


def test_checkout_missingarg(client):
    args = CHECKOUT_ARGS()
    del args["requested_currency"]
    rv = client.post("/payments", json=args, headers=GOOD_AUTH)
    assert HTTPStatus.BAD_REQUEST == rv.status_code
    assert rv.get_json() == {"error": "'requested_currency' is a required property"}


def test_checkout_unique_merchant_reference_id(client):
    args = CHECKOUT_ARGS()
    rv = client.post("/payments", json=args, headers=GOOD_AUTH)
    assert HTTPStatus.OK == rv.status_code

    rv = client.post("/payments", json=args, headers=GOOD_AUTH)
    assert HTTPStatus.BAD_REQUEST == rv.status_code
    assert rv.get_json() == {"error": "dup_merchant_reference_id"}


def test_checkout_negative(client):
    args = CHECKOUT_ARGS()
    args["amount"] = -1
    rv = client.post("/payments", json=args, headers=GOOD_AUTH)
    assert rv.get_json() == {"error": "-1 is less than the minimum of 0"}
    assert HTTPStatus.BAD_REQUEST == rv.status_code


def test_refund_success(client, mocker):
    count_status_log = PaymentStatusLog.query.filter_by(
        payment_id=CLEARED_PAYMENT_ID
    ).count()

    send_mock = mocker.patch.object(
        Vasp, "send_transaction", return_value=(REFUND_TX_ID, 9)
    )

    rv = client.post(f"/payments/{CLEARED_PAYMENT_ID}/refund", headers=GOOD_AUTH)

    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()
    assert data["refund_tx_id"] == REFUND_TX_ID
    send_mock.assert_called_once()
    assert (
        count_status_log + 1
        == PaymentStatusLog.query.filter_by(payment_id=CLEARED_PAYMENT_ID).count()
    )
    refund_log = PaymentStatusLog.query.filter_by(payment_id=CLEARED_PAYMENT_ID).all()[
        -1
    ]
    assert refund_log.status == PaymentStatus.refund_requested
    time_difference = (datetime.utcnow() - refund_log.created_at).total_seconds()

    assert 0 < time_difference < 5


def test_refund_uncleared_payment(client, mocker):
    send_mock = mocker.patch.object(
        Vasp, "send_transaction", return_value=(REFUND_TX_ID, 9)
    )

    rv = client.post(f"/payments/{PAYMENT_ID}/refund", headers=GOOD_AUTH)

    assert HTTPStatus.BAD_REQUEST == rv.status_code
    assert rv.get_json() == {"error": "unclearedrefund"}
    send_mock.assert_not_called()


def test_refund_no_args(client):
    rv = client.post("/refund", headers=GOOD_AUTH)
    assert HTTPStatus.NOT_FOUND == rv.status_code


def test_refund_noauth(client):
    rv = client.post("/payments/doesntmatter/refund")
    assert HTTPStatus.UNAUTHORIZED == rv.status_code
    assert rv.get_json() == {"error": "noauth"}


def test_refund_bad_payment_id(client, mocker):
    send_mock = mocker.patch.object(
        Vasp, "send_transaction", return_value=(REFUND_TX_ID, 9)
    )

    rv = client.post("/payments/mattarpaneer/refund", headers=GOOD_AUTH)

    assert HTTPStatus.NOT_FOUND == rv.status_code
    assert rv.get_json() == {"error": "notfound"}
    send_mock.assert_not_called()


def test_pay_bad_id(client):
    rv = client.get(f"/payments/nonexisting_payment")
    assert HTTPStatus.NOT_FOUND == rv.status_code
    assert PAYMENT_ID not in rv.get_data(as_text=True)


def test_pay_rejected(client):
    payment = Payment.query.get(REJECTED_PAYMENT_ID)
    rv = client.get(f"/payments/{payment.id}")
    assert HTTPStatus.NOT_FOUND == rv.status_code
    assert payment.subaddress not in rv.get_data(as_text=True)
    assert PAYMENT_ID not in rv.get_data(as_text=True)


def test_pay_expired(client):
    payment = Payment.query.get(EXPIRED_PAYMENT_ID)
    rv = client.get(f"/payments/{payment.id}")
    assert HTTPStatus.NOT_FOUND == rv.status_code
    assert PAYMENT_ID not in rv.get_data(as_text=True)
    assert payment.subaddress not in rv.get_data(as_text=True)


def test_pay_success(client):
    payment = Payment.query.get(PAYMENT_ID)
    rv = client.get(f"/payments/{payment.id}")

    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()
    assert data["payment_id"] == payment.id


def test_pay_used(client):
    payment = Payment.query.get(CLEARED_PAYMENT_ID)

    rv = client.get(f"/payments/{payment.id}")
    assert HTTPStatus.NOT_FOUND == rv.status_code


def test_payment_log_noauth(client):
    payment = Payment.query.get(CLEARED_PAYMENT_ID)

    rv = client.get(f"/payments/{payment.id}/log")
    assert HTTPStatus.UNAUTHORIZED == rv.status_code


def test_payment_log(client):
    payment = Payment.query.get(CLEARED_PAYMENT_ID)
    payment.set_status(PaymentStatus.rejected)
    db_session.commit()

    rv = client.get(f"/payments/{payment.id}/log", headers=GOOD_AUTH)
    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()

    assert data["status"] == payment.status
    assert data["events"][-1]["status"] == PaymentStatus.rejected
    assert data["events"][-2]["status"] == PaymentStatus.cleared


def test_payout_refunded(client):
    rv = client.post(f"/payments/{REJECTED_PAYMENT_ID}/payout", headers=GOOD_AUTH)
    assert HTTPStatus.BAD_REQUEST == rv.status_code
    assert rv.get_json()["error"] == "invalid_status"


def test_payout_noauth(client):
    rv = client.post(f"/payments/{CLEARED_PAYMENT_ID}/payout")
    assert HTTPStatus.UNAUTHORIZED == rv.status_code


def test_payout_success(mocker, client):
    send_mock = mocker.patch.object(
        Vasp, "send_transaction", return_value=(PAYOUT_TX_ID, 9)
    )

    rv = client.post(f"/payments/{CLEARED_PAYMENT_ID}/payout", headers=GOOD_AUTH)
    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()

    payment = Payment.query.get(CLEARED_PAYMENT_ID)
    merchant = payment.merchant

    assert data["target"] == merchant.settlement_information
    assert PaymentStatus.payout_completed == payment.status
    send_mock.assert_called_once()


def test_refund_request_success(client):
    payment = Payment.query.get(CLEARED_PAYMENT_ID)
    rv = client.post(
        f"/payments/{payment.merchant_reference_id}/request_refund", headers=GOOD_AUTH
    )

    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()
    assert data["status"] == payment.status
    assert data["refund_requested"] == True


def test_refund_request_uncleared(client):
    payment = Payment.query.get(PAYMENT_ID)
    rv = client.post(
        f"/payments/{payment.merchant_reference_id}/request_refund", headers=GOOD_AUTH
    )

    assert HTTPStatus.BAD_REQUEST == rv.status_code
    data = rv.get_json()
    assert data["error"] == "unclearedrefund"


def test_list_payments(client):
    rv = client.get(f"/payments", headers=GOOD_AUTH)
    assert HTTPStatus.OK == rv.status_code
    data = rv.get_json()["payments"]

    # Find CLEARED_PAYMENT_ID
    payment = [p for p in data if p["payment_id"] == CLEARED_PAYMENT_ID][0]

    assert payment["status"] == PaymentStatus.cleared
    assert payment["refund_requested"] == False
