from .vasp import vasp, VaspRoutes
from .vasp_wallet import vasp_wallet, VaspWalletRoutes


def vasp_routes():
    vasp.add_url_rule(
        rule="/payments",
        view_func=VaspRoutes.CreatePaymentView.as_view("create_payment"),
        methods=["POST"],
    )

    vasp.add_url_rule(
        rule="/payments",
        view_func=VaspRoutes.ListPaymentsView.as_view("list_merchant_payments"),
        methods=["GET"],
    )

    vasp.add_url_rule(
        rule="/payments/<payment_id>",
        view_func=VaspRoutes.PaymentOptionsView.as_view("payment_options"),
        methods=["GET"],
    )

    vasp.add_url_rule(
        rule="/payments/<payment_id>/log",
        view_func=VaspRoutes.PaymentLogView.as_view("payment_log"),
        methods=["GET"],
    )

    vasp.add_url_rule(
        rule="/payments/<merchant_reference_id>/status",
        view_func=VaspRoutes.PaymentStatusView.as_view("payment_status"),
        methods=["GET"],
    )

    vasp.add_url_rule(
        rule="/payments/<merchant_reference_id>/request_refund",
        view_func=VaspRoutes.RefundRequestView.as_view("request_refund"),
        methods=["POST"],
    )

    vasp.add_url_rule(
        rule="/payments/<payment_id>/payout",
        view_func=VaspRoutes.PayoutView.as_view("payout"),
        methods=["POST"],
    )

    vasp.add_url_rule(
        rule="/payments/<payment_id>/refund",
        view_func=VaspRoutes.RefundView.as_view("refund"),
        methods=["POST"],
    )


def vasp_wallet_routes():
    vasp_wallet.add_url_rule(
        rule="/supported_network_currencies",
        view_func=VaspWalletRoutes.SupportedNetworkCurrenciesView.as_view(
            "network_currencies"
        ),
        methods=["GET"],
    )

    vasp_wallet.add_url_rule(
        rule="/supported_currencies",
        view_func=VaspWalletRoutes.SupportedCurrenciesView.as_view("currencies"),
        methods=["GET"],
    )


vasp_routes()
vasp_wallet_routes()
