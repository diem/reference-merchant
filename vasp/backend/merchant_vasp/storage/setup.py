# pyre-ignore-all-errors
from . import db_session, engine, Base
from .models import Merchant, PaymentStatus, Payment, PaymentOption


def clear_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
