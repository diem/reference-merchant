import os
from http import HTTPStatus
from urllib.parse import urljoin

import werkzeug
from flask import Blueprint, request, url_for, render_template

from merchant_vasp import transaction_manager
from merchant_vasp.payment_service import payment_service
from merchant_vasp.transaction_manager import (
    InvalidPaymentStatus,
    TakenMerchantReferenceId,
)
from .strict_schema_view import (
    StrictSchemaView,
    response_definition,
    path_uuid_param,
    body_parameter,
)
from ..schemas import (
    RefundSchema,
    CreatePaymentSchema,
    PaymentLogSchema,
    PaymentStatusSchema,
    PayoutSchema,
    RefundRequestSchema,
    ListPaymentsSchema,
    CreatePaymentArguments,
    BadArgsSchema,
    PaymentOptionsSchema,
)
from diem import identifier


class PaymentNotFound(werkzeug.exceptions.NotFound):
    pass


def payment_not_found_handler(_):
    return {"error": "notfound"}, HTTPStatus.NOT_FOUND


def bad_payment_status_handler(e):
    return {"error": e.message}, HTTPStatus.BAD_REQUEST


def invalid_args_status_handler(e):
    return {"error": e.args[0]}, HTTPStatus.BAD_REQUEST


vasp = Blueprint("vasp", __name__)
vasp.register_error_handler(PaymentNotFound, payment_not_found_handler)
vasp.register_error_handler(InvalidPaymentStatus, bad_payment_status_handler)
vasp.register_error_handler(KeyError, invalid_args_status_handler)


class VaspRoutes:
    class MerchantVaspView(StrictSchemaView):
        tags = ["vasp"]
        require_merchant = True

    class PaymentVaspView(MerchantVaspView):
        success_message = ""

        parameters = [
            path_uuid_param("payment_id", "ID of an existing payment"),
        ]

        def _validate_payment(self):
            if self.payment is None or (
                self.require_merchant and self.payment.merchant_id != self.merchant.id
            ):
                raise PaymentNotFound

        def _load_payment(self, payment_id):
            self.payment = transaction_manager.load_payment(payment_id)
            self._validate_payment()

        def _load_payment_by_merchant_reference_id(self, merchant_reference_id):
            self.payment = transaction_manager.load_merchant_payment_id(
                merchant_reference_id, self.merchant
            )
            self._validate_payment()

    class PaymentLogView(PaymentVaspView):
        responses = {
            HTTPStatus.OK: response_definition(
                "Payment Log fetched", schema=PaymentLogSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }

        def _get_schema(self):
            return

        def get(self, payment_id):
            self._load_payment(payment_id)
            return (
                {
                    "status": self.payment.status,
                    "merchant_address": transaction_manager.get_merchant_full_addr(
                        self.payment
                    ),
                    "events": transaction_manager.get_payment_events(self.payment),
                    "can_payout": transaction_manager.payment_can_payout(self.payment),
                    "can_refund": transaction_manager.payment_can_refund(self.payment),
                    "chain_txs": transaction_manager.payment_chain_txs(self.payment),
                },
                HTTPStatus.OK,
            )

    class PaymentStatusView(PaymentVaspView):
        summary = "Get payment current status"

        responses = {
            HTTPStatus.OK: response_definition(
                "Payment Status fetched", schema=PaymentStatusSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }

        def get(self, merchant_reference_id):
            self._load_payment_by_merchant_reference_id(merchant_reference_id)
            return (
                {
                    "status": self.payment.status,
                    "expiry_date": self.payment.expiry_date,
                },
                HTTPStatus.OK,
            )

    class PaymentOptionsView(PaymentVaspView):
        require_merchant = False
        summary = "Get available checkout options for a payment"

        responses = {
            HTTPStatus.OK: response_definition(
                "Checkout options fetched", schema=PaymentOptionsSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }
        vaspAddress = os.getenv("VASP_ADDR")
        chainId = os.getenv("CHAIN_ID")
        hrp = identifier.HRPS[int(chainId)]
        sender_address = (
            identifier.encode_account(vaspAddress, "0000000000000000", hrp),
        )

        def get(self, payment_id):
            self._load_payment(payment_id)
            if not transaction_manager.payment_can_pay(self.payment):
                raise PaymentNotFound

            return (
                dict(
                    payment_id=self.payment.id,
                    options=payment_service.generate_payment_options_with_qr(
                        self.payment
                    ),
                    fiat_price=self.payment.requested_amount,
                    fiat_currency=self.payment.requested_currency,
                    wallet_url=os.getenv("WALLET_URL"),
                    base_merchant_url=os.getenv("BASE_MERCHANT_URL"),
                    vasp_address=self.sender_address,
                ),
                HTTPStatus.OK,
            )

    class ListPaymentsView(MerchantVaspView):
        summary = "List payments for merchant"
        responses = {
            HTTPStatus.OK: response_definition(
                "List payments successful", schema=ListPaymentsSchema
            )
        }

        def get(self):
            return (
                {"payments": transaction_manager.get_merchant_payments(self.merchant)},
                HTTPStatus.OK,
            )

    class CreatePaymentView(MerchantVaspView):
        summary = "Create a new transaction"
        responses = {
            HTTPStatus.OK: response_definition(
                "CreatePayment successful", schema=CreatePaymentSchema
            ),
            HTTPStatus.BAD_REQUEST: response_definition(
                "Invalid arguments", BadArgsSchema
            ),
        }
        parameters = [body_parameter(CreatePaymentArguments)]

        def post(self):
            rfq = request.json
            currency = rfq["requested_currency"]
            merchant_reference_id = rfq["merchant_reference_id"]
            amount = rfq["amount"]

            try:
                new_payment = transaction_manager.create_payment(
                    currency, merchant_reference_id, amount, self.merchant.id
                )
            except TakenMerchantReferenceId:
                return self.respond_with_error(
                    HTTPStatus.BAD_REQUEST, "dup_merchant_reference_id"
                )

            payment_form_url = self._generate_payment_url(new_payment)

            return (
                {
                    "payment_id": new_payment.id,
                    "expiry_date": new_payment.expiry_date,
                    "payment_form_url": payment_form_url,
                },
                HTTPStatus.OK,
            )

        def _generate_payment_url(self, new_payment):
            external_root = (
                os.getenv("MY_EXTERNAL_URL", "http://127.0.0.1:5000").strip("/") + "/"
            )
            payment_form_url = (
                external_root + "pay/index.html?payment=" + new_payment.id
            )
            self.logger.debug(f"payment form url: {payment_form_url}")
            return payment_form_url

    class PayoutView(PaymentVaspView):
        summary = "Pay out a transaction"

        responses = {
            HTTPStatus.OK: response_definition(
                "Payout successful", schema=PayoutSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }

        def post(self, payment_id):
            self._load_payment(payment_id)

            (
                payout_target,
                quote,
                tx_id,
                settlement_information,
            ) = transaction_manager.payout(self.merchant, self.payment)

            return (
                {
                    "target": settlement_information,
                    "trade_id": payout_target,
                    "quote_amount": quote.amount,
                    "quote_id": quote.quote_id,
                    "tx_id": tx_id,
                },
                HTTPStatus.OK,
            )

    class RefundRequestView(PaymentVaspView):
        summary = "Request a refund"

        responses = {
            HTTPStatus.OK: response_definition(
                "Request successful", schema=RefundRequestSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }

        # TODO: this is terrible - the client is REQUIRED to have the auth token of the merchant
        # require_merchant = False

        def post(self, merchant_reference_id):
            self._load_payment_by_merchant_reference_id(merchant_reference_id)
            self.logger.info(f"refund requested for payment id {self.payment.id}")

            transaction_manager.request_refund(self.payment)

            return (
                {
                    "status": self.payment.status,
                    "refund_requested": self.payment.refund_requested,
                },
                HTTPStatus.OK,
            )

    class RefundView(PaymentVaspView):
        summary = "Approve a refund"

        responses = {
            HTTPStatus.OK: response_definition(
                "Refund successful", schema=RefundSchema
            ),
            HTTPStatus.NOT_FOUND: response_definition("Unknown payment"),
        }

        def post(self, payment_id):
            self.logger.info(f"refund approved for payment id {payment_id}")
            self._load_payment(payment_id)

            refund_tx_id, target_transaction = transaction_manager.refund(self.payment)

            return (
                {
                    "refund_tx_id": refund_tx_id,
                    "payment_tx_id": target_transaction.tx_id,
                },
                HTTPStatus.OK,
            )
