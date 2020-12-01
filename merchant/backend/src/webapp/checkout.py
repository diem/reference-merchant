from flask import render_template


def render_checkout(order, checkout_options):
    return render_template("checkout.html", order_id=str(order.order_id))
