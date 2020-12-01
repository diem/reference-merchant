from dataclasses import dataclass
from datetime import datetime
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PaymentStatus:
    status: str
    expiry_date: str


@dataclass_json
@dataclass
class Payment:
    payment_id: str
    payment_form_url: str


@dataclass_json
@dataclass
class PaymentEvent:
    timestamp: datetime
    event_type: str


@dataclass_json
@dataclass
class BlockchainTx:
    tx_id: int
    is_refund: bool
    sender_address: str
    amount: int
    currency: str


@dataclass_json
@dataclass
class PaymentEventsLog:
    status: str
    merchant_address: str
    can_payout: bool
    can_refund: bool
    chain_txs: List[BlockchainTx]
    events: List[PaymentEvent]
