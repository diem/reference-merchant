import dramatiq
from libra_utils.libra import decode_subaddr

from ..payment_service import process_incoming_transaction, PaymentServiceException
from ..storage import db_session

from pubsub.types import TransactionMetadata, LRWPubSubEvent


@dramatiq.actor(store_results=True)
def process_incoming_txn(txn: LRWPubSubEvent) -> None:
    metadata = txn.metadata
    receiver_subaddress = None
    sender_subaddress = None
    if metadata:
        if metadata.to_subaddress:
            receiver_subaddress = decode_subaddr(metadata.to_subaddress)

        sender_subaddress = decode_subaddr(metadata.from_subaddress)
        if sender_subaddress == "":
            sender_subaddress = None

    # TODO - handle exception here?
    try:
        process_incoming_transaction(
            version=txn.version,
            sender_address=txn.sender,
            sender_subaddress=sender_subaddress,
            receiver_address=txn.receiver,
            receiver_subaddress=receiver_subaddress,
            sequence=txn.sequence,
            amount=txn.amount,
            currency=txn.currency,
        )
    except PaymentServiceException as _:
        # TODO - log exception
        db_session.rollback()
    finally:
        db_session.remove()
