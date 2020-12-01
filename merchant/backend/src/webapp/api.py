from dataclasses import asdict
from uuid import UUID

from flask import Blueprint, request
from requests import HTTPError

import store.products
from store.orders import OrderItem, get_order_details
from vasp_client import vasp_client
from vasp_client.types import PaymentStatus

from .schemas import (
    CheckoutRequest,
    CheckoutResponse,
    ProductList,
    OrderDetails,
    ProductOrder,
    Product,
)
from .strict_schema_view import (
    StrictSchemaView,
    response_definition,
    body_parameter,
    path_str_param,
    path_uuid_param,
)

api = Blueprint("api", __name__)


def order_item_to_product_order(item: OrderItem) -> ProductOrder:
    return ProductOrder(
        quantity=item.quantity,
        product=Product.from_dict(
            store.products.get_product_details(item.gtin).to_dict()
        ),
    )


class ApiView(StrictSchemaView):
    pass


class ProductListView(ApiView):
    summary = "Returns list of products"
    parameters = []
    responses = {
        200: response_definition("list of products", schema=ProductList.schema),
    }

    def get(self):
        products = store.products.get_products_list()
        product_list = ProductList(products=list(products))

        return product_list.to_dict(), 200


class CheckoutView(ApiView):
    summary = "Initiate new payment process for a single product"
    parameters = [
        body_parameter(CheckoutRequest),
    ]
    responses = {
        200: response_definition(
            "Payment ID and payment form URL", schema=CheckoutResponse
        ),
    }

    def post(self):
        purchase_request = CheckoutRequest.from_dict(request.json)

        items = [
            OrderItem(gtin=item.gtin, quantity=item.quantity)
            for item in purchase_request.items
        ]
        order = store.orders.create_order(items)
        payment = vasp_client.start_payment(
            order.total_price, order.currency, order.order_id
        )
        store.orders.set_order_payment_reference(order.order_id, payment.payment_id)

        return (
            {
                "order_id": order.order_id,
                "vasp_payment_id": payment.payment_id,
                "payment_form_url": payment.payment_form_url,
            },
            200,
        )


class OrderDetailsView(ApiView):
    summary = "Returns payment details"
    parameters = [
        path_str_param(
            name="order_id", description="Get payment status", required=True
        ),
    ]
    responses = {
        200: response_definition("Log of payment events", schema=OrderDetails.schema),
    }

    def get(self, order_id):
        order = get_order_details(order_id)
        if order is None:
            return "Unknown order", 404

        payment_status = vasp_client.get_payment_log(order.vasp_payment_reference)

        order_details = OrderDetails(
            order_id=str(order.order_id),
            created_at=order.created_at,
            vasp_payment_reference=order.vasp_payment_reference,
            total_price=order.total_price,
            currency=order.currency,
            products=[order_item_to_product_order(item) for item in order.items],
            payment_status=payment_status,
        )

        return order_details.to_dict(), 200


class PaymentStatusView(ApiView):
    summary = "Get payment status"
    parameters = [
        path_str_param(name="order_id", description="Get payment status", required=True)
    ]

    responses = {
        200: response_definition("Payment Status", schema=PaymentStatus.schema),
    }

    def get(self, order_id: str):
        try:
            payment_status = vasp_client.get_payment_status(
                merchant_reference_id=order_id
            )
            return payment_status.to_dict(), 200
        except HTTPError as e:
            raise e


class PayoutView(ApiView):
    summary = "Request pay-out for a specific payment"
    parameters = [
        path_uuid_param("payment_id", "VASP payment ID"),
    ]

    def post(self, payment_id: UUID):
        vasp_client.payout(payment_id)
        return {"status": "OK"}, 200


class RefundView(ApiView):
    summary = "Refund specific payment"
    parameters = [
        path_uuid_param("payment_id", "VASP payment ID"),
    ]

    def post(self, payment_id: UUID):
        vasp_client.refund(payment_id)
        return {"status": "OK"}, 200


api.add_url_rule(
    rule="/products",
    view_func=ProductListView.as_view("product_list"),
    methods=["GET"],
)

api.add_url_rule(
    rule="/payments", view_func=CheckoutView.as_view("checkout"), methods=["POST"],
)

api.add_url_rule(
    rule="/payments/<uuid:payment_id>/payout",
    view_func=PayoutView.as_view("payout"),
    methods=["POST"],
)

api.add_url_rule(
    rule="/payments/<uuid:payment_id>/refund",
    view_func=RefundView.as_view("refund"),
    methods=["POST"],
)

api.add_url_rule(
    rule="/orders/<uuid:order_id>",
    view_func=OrderDetailsView.as_view("order_details"),
    methods=["GET"],
)

api.add_url_rule(
    rule="/orders/<uuid:order_id>/payment",
    view_func=PaymentStatusView.as_view("payment_status"),
    methods=["GET"],
)
