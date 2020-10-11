import dramatiq
from libra import libra_types
from libra_utils.types.currencies import LibraCurrency

from pubsub.types import LRWPubSubEvent
from ..payment_service import process_incoming_transaction, PaymentServiceException
from ..storage import db_session


@dramatiq.actor(store_results=True)
def process_incoming_txn(txn: LRWPubSubEvent) -> None:
    metadata = txn.metadata

    sender_sub_address = None
    receiver_sub_address = None

    if metadata and isinstance(metadata, libra_types.Metadata__GeneralMetadata) \
            and isinstance(metadata.value, libra_types.GeneralMetadata__GeneralMetadataVersion0):
        general_metadata = metadata.value.value

        if general_metadata.to_subaddress:
            receiver_sub_address = general_metadata.to_subaddress.hex()

        if general_metadata.from_subaddress:
            sender_sub_address = general_metadata.from_subaddress.hex()

    try:
        process_incoming_transaction(version=txn.version, sender_address=txn.sender,
                                     sender_sub_address=sender_sub_address, receiver_address=txn.receiver,
                                     receiver_sub_address=receiver_sub_address, amount=txn.amount,
                                     currency=LibraCurrency[txn.currency])
    except PaymentServiceException as _:
        # TODO - log exception
        db_session.rollback()

    finally:
        db_session.remove()
