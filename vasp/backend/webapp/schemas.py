from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Range
from diem_utils.types.currencies import FiatCurrency

from merchant_vasp.storage import PaymentStatus


def fiat_amount_field(**kwargs) -> fields.Field:
    """Defines fiat currency amount schema field"""
    return fields.Int(
        description="Amount of fiat currency in scale factor 6",
        validate=Range(min=1),
        strict=True,
        **kwargs,
    )


def diem_amount_field(**kwargs) -> fields.Field:
    """Defines Diem currency amount schema field"""
    return fields.Int(
        description="Amount of Diem currency in scale factor 6",
        validate=Range(min=1),
        strict=True,
        **kwargs,
    )


def positive_double_field(**kwargs) -> fields.Field:
    return fields.Decimal(
        description="Amount of currency",
        validate=Range(min=0, min_inclusive=False),
        strict=True,
        **kwargs,
    )


def fiat_currency_code_field(**kwargs) -> fields.Field:
    """Defines fiat currency code schema field"""
    return fields.Str(
        description="Fiat currency code",
        validate=OneOf(list(FiatCurrency.__members__)),
        **kwargs,
    )


def diem_currency_code_field(**kwargs) -> fields.Field:
    """Defines Diem currency code schema field"""
    return fields.Str(
        description="Diem currency code",
        **kwargs,
    )


def payment_status_field(**kwargs):
    """Defines payment status field"""
    return fields.Str(
        description="Payment status",
        validate=OneOf(list(PaymentStatus.__members__)),
        **kwargs,
    )


class BadArgsSchema(Schema):
    error = fields.Str(required=True)


class RefundSchema(Schema):
    refund_tx_id = fields.Int(required=True)
    payment_tx_id = fields.Int(required=True)


class RefundRequestSchema(Schema):
    status = payment_status_field()
    refund_requested = fields.Bool(required=True)


class CreatePaymentArguments(Schema):
    amount = positive_double_field()
    requested_currency = fields.Str(required=True)
    merchant_reference_id = fields.Str(required=True)


class CreatePaymentSchema(Schema):
    payment_id = fields.UUID(required=True)
    expiry_date = fields.DateTime(required=True)
    payment_form_url = fields.Str(required=True)


class _PaymentItem(Schema):
    payment_id = fields.UUID(required=True)
    created_at = fields.DateTime(required=True)
    status = payment_status_field()
    refund_requested = fields.Bool(required=True)


class ListPaymentsSchema(Schema):
    payments = fields.List(fields.Nested(_PaymentItem), required=True)


class _PaymentLogSingleEvent(Schema):
    created_at = fields.DateTime(required=True)
    status = payment_status_field()


class _PaymentLogSingleTx(Schema):
    tx_id = fields.Int(required=True)
    is_refund = fields.Bool(required=True)
    sender_address = fields.Str(required=True)
    amount = fields.Float(required=True)
    currency = fields.Str(required=True)


class PaymentLogSchema(Schema):
    status = payment_status_field()
    merchant_address = fields.Str(required=True)
    events = fields.List(fields.Nested(_PaymentLogSingleEvent), required=True)
    can_payout = fields.Bool(required=True)
    can_refund = fields.Bool(required=True)
    chain_txs = fields.List(fields.Nested(_PaymentLogSingleTx), required=True)


class PaymentStatusSchema(Schema):
    status = payment_status_field()
    expiry_date = fields.DateTime(required=True)


class PayoutSchema(Schema):
    target = fields.Str(required=True)
    trade_id = fields.Str(required=True)
    quote_amount = fields.Float(required=True)
    quote_id = fields.Str(required=True)
    tx_id = fields.Int(required=True)


class CurrencyListSchema(Schema):
    currencies = fields.List(fields.Str, required=True)


class PaymentOptionSchema(Schema):
    address = fields.Str(required=True)
    currency = diem_currency_code_field(required=True)
    amount = diem_amount_field(required=True)
    payment_link = fields.Str(required=True)


class PaymentOptionsSchema(Schema):
    payment_id = fields.UUID(required=True)
    fiat_price = fiat_amount_field()
    fiat_currency = fiat_currency_code_field()
    options = fields.List(fields.Nested(PaymentOptionSchema), required=True)
