from http import HTTPStatus
from uuid import UUID

import pytest

from vasp_client import vasp_client
from vasp_client.types import PaymentStatus, Payment

test_payment_id = "6b8314d6-97a6-4519-b943-c64672042800"
test_url = "http://redorect/to_here"


@pytest.fixture
def start_payment_mock(monkeypatch):
    def start_payment_mock_impl(price: int, currency: str, order_id: UUID) -> Payment:
        return Payment(payment_id=test_payment_id, payment_form_url=test_url)

    monkeypatch.setattr(vasp_client, "start_payment", start_payment_mock_impl)


def test_checkout_new_order(client, start_payment_mock):
    test_gtin = "00000001"

    checkout_request_body = {"items": [{"gtin": test_gtin, "quantity": 1}]}
    response = client.post("/payments", json=checkout_request_body)

    assert HTTPStatus.OK == response.status_code
    assert response.json["payment_form_url"] == test_url


test_payment_status = PaymentStatus(status="cleared", expiry_date="now")


def test_get_payment_status(client, mocker):
    mocker.patch.object(
        vasp_client, "get_payment_status", return_value=test_payment_status
    )

    test_order_id = "1743d9e4-b66f-4362-ae08-d5991f418062"
    response = client.get(f"/orders/{test_order_id}/payment")

    assert HTTPStatus.OK == response.status_code
    assert test_payment_status == PaymentStatus.from_dict(response.json)
