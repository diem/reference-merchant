import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import requests

from .types import PaymentStatus, Payment, PaymentEventsLog, PaymentEvent

PAYMENT_VASP_URL = os.getenv("PAYMENT_VASP_URL", "http://127.0.0.1:5000")
VASP_TOKEN = os.getenv("VASP_TOKEN")


def start_payment(price: int, currency: str, order_id: UUID) -> Payment:
    """
    Returns: Payment ID as supplied by the payment provider and the URL for
             the retrieval of the payment form.
    """
    r = _post(
        "/payments",
        {
            "amount": price,
            "requested_currency": currency,
            "merchant_reference_id": str(order_id),
        },
    )
    _raise_for_status(r)

    return Payment.from_dict(r.json())


def get_payment_log(payment_id: str) -> Optional[PaymentEventsLog]:
    r = _get(f"/payments/{payment_id}/log")

    if r.status_code == 404:
        return None
    _raise_for_status(r)
    vasp_response = r.json()

    # Reshaping the events to look like what we need
    events = [
        PaymentEvent(
            timestamp=datetime.fromisoformat(ev["created_at"]), event_type=ev["status"]
        )
        for ev in vasp_response["events"]
    ]
    vasp_response["events"] = events

    return PaymentEventsLog.from_dict(vasp_response)


def payout(payment_id: UUID):
    r = _post(f"/payments/{payment_id}/payout")
    _raise_for_status(r)


def refund(payment_id: UUID):
    r = _post(f"/payments/{payment_id}/refund")
    _raise_for_status(r)


def get_payment_status(merchant_reference_id):
    r = _get(f"/payments/{merchant_reference_id}/status")
    _raise_for_status(r)

    return PaymentStatus.from_dict(r.json())


def _get(endpoint: str):
    return requests.get(
        url=PAYMENT_VASP_URL + endpoint,
        headers={"Authorization": f"Bearer {VASP_TOKEN}"},
        allow_redirects=False,
    )


def _post(endpoint: str, data: dict = None):
    return requests.post(
        url=PAYMENT_VASP_URL + endpoint,
        json=data,
        headers={"Authorization": f"Bearer {VASP_TOKEN}"},
        allow_redirects=False,
    )


def _raise_for_status(response: requests.Response):
    if 400 <= response.status_code < 600:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason}: {response.text}",
            response=response,
        )
