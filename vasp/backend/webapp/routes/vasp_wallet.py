from http import HTTPStatus

from flask import Blueprint

from merchant_vasp.payment_service import payment_service
from .strict_schema_view import StrictSchemaView, response_definition
from ..schemas import CurrencyListSchema

vasp_wallet = Blueprint("vasp_wallet", __name__)


class VaspWalletRoutes:
    class SupportedNetworkCurrenciesView(StrictSchemaView):
        require_merchant = False
        summary = "Get supported network currencies"
        responses = {
            HTTPStatus.OK: response_definition(
                "Currencies listed succesfully", schema=CurrencyListSchema
            )
        }

        def get(self):
            return (
                {"currencies": payment_service.get_supported_network_currencies()},
                HTTPStatus.OK,
            )

    class SupportedCurrenciesView(StrictSchemaView):
        require_merchant = False
        summary = "Get supported currencies"
        responses = {
            HTTPStatus.OK: response_definition(
                "Currencies listed succesfully", schema=CurrencyListSchema
            )
        }

        def get(self):
            return (
                {"currencies": payment_service.get_supported_currencies()},
                HTTPStatus.OK,
            )
