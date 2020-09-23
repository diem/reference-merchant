import json
from functools import wraps
from http import HTTPStatus

from flask import g, request, Response

from ...merchant_vasp.storage import Merchant


def get_token_id_from_request() -> str:
    return request.headers.get("Authorization", "").split(" ")[-1]


def verify_merchant_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_id = get_token_id_from_request()
        merchant = Merchant.find_by_token(token_id)

        if merchant is not None:
            g.merchant_id = merchant.id
            return f(*args, **kwargs)
        else:
            error = json.dumps({"error": "noauth"})
            return Response(
                error, status=HTTPStatus.UNAUTHORIZED, mimetype="application/json"
            )

    return decorated_function
