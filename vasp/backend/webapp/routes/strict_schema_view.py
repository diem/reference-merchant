from http import HTTPStatus
from typing import Tuple, List, Optional

from jsonschema.exceptions import ValidationError
from flasgger import SwaggerView, utils
from flask import request, current_app, abort, jsonify, make_response
from requests import RequestException
from werkzeug.exceptions import HTTPException

from merchant_vasp.storage import Merchant

BEARER_LEN = len("Bearer ")

orig_utils_validate = utils.validate


def patched_validate(*args, **kwargs):
    kwargs["require_data"] = False
    orig_utils_validate(*args, **kwargs)


utils.validate = patched_validate


class StrictSchemaView(SwaggerView):
    """
    A Flask view handling Swagger generation and response/request schema
    validation.
    Note that, as opposed to the original Flask MethodView, the view methods
    (get, post etc.) support returning only (response, status_code) tuples.
    For errors it is possible to raise exceptions.
    """

    # If True, a merchant must be identified for the action
    require_merchant = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._merchant = None
        self._token = None

        self.logger = None

        if self.parameters:
            for p in self.parameters:
                param_type = p.get("in", None)
                if param_type == "body":
                    self.validation = True
                    self.validation_error_handler = self._validation_error_handler
                    break

    @property
    def merchant(self):
        if self._merchant is None:
            raise AttributeError("Merchant unavailable when not in a request context")
        return self._merchant

    def dispatch_request(self, *args, **kwargs):
        self.logger = current_app.logger

        if self.require_merchant:
            token = self._get_auth_token_from_headers(request.headers)
            self._merchant = Merchant.find_by_token(token)

            if self._merchant is None:
                return self.respond_with_error(HTTPStatus.UNAUTHORIZED, "noauth")

        try:
            response, status_code = super().dispatch_request(*args, **kwargs)
        except RequestException as err:
            if err.response:
                error_text = f"{err.request.method} {err.request.url} {err.response.status_code}: {err.response}"
                if err.response.status_code == 500:
                    current_app.logger.error(error_text)
                else:
                    current_app.logger.warn(error_text)
            elif err.request:
                current_app.logger.error(
                    f"{err.request.method} {err.request.url}: {err}"
                )
            else:
                current_app.logger.error(err)
            raise
        except Exception as err:
            current_app.logger.error(err)
            raise

        # Reset arguments after handling request
        self._merchant = None
        self.logger = None

        response = validate_response(response, status_code, self.responses)

        return response, status_code

    @staticmethod
    def _validation_error_handler(err, _data, _main_def):
        if isinstance(err, ValidationError):
            return abort(
                make_response(jsonify(error=err.message), HTTPStatus.BAD_REQUEST)
            )

        raise err

    @staticmethod
    def respond_with_error(code: int, error: str) -> Tuple[dict, int]:
        return {"error": error}, code

    @staticmethod
    def _get_auth_token_from_headers(headers):
        return headers.get("Authorization", "").split(" ")[-1]

    def _has_parameter(self, name):
        for parameter in self.parameters:
            if name == parameter["name"]:
                return True
        return False


def validate_response(response, http_status_code, response_definitions):
    schema_factory = (
        response_definitions.get(http_status_code, {})
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )
    if not schema_factory:
        return response
    schema = schema_factory()
    response = schema.dump(response)
    errors = schema.validate(response)
    if errors:
        raise ResponseSchemaError(schema.__class__.__name__, response, errors)
    return response


def response_definition(description, schema=None):
    """Helps to create response definitions"""
    return {
        "description": description,
        "content": {"application/json": {"schema": schema}},
    }


def body_parameter(schema):
    return {"name": "body", "in": "body", "required": True, "schema": schema}


def query_bool_param(name, description, required):
    return {
        "name": name,
        "in": "query",
        "required": required,
        "description": description,
        "schema": {"type": "boolean"},
    }


def query_int_param(name, description, required):
    return {
        "name": name,
        "in": "query",
        "required": required,
        "description": description,
        "schema": {"type": "integer"},
    }


def query_str_param(
    name, description, required, allowed_vlaues: Optional[List[str]] = None
):
    param_definition = {
        "name": name,
        "in": "query",
        "required": required,
        "description": description,
        "schema": {"type": "string"},
    }

    if allowed_vlaues:
        param_definition["enum"] = allowed_vlaues

    return param_definition


def path_uuid_param(name, description):
    return {
        "name": name,
        "in": "path",
        "required": True,
        "description": description,
        "schema": {"type": "string", "format": "uuid",},
    }


def path_string_param(name, description):
    return {
        "name": name,
        "in": "path",
        "required": True,
        "description": description,
        "schema": {"type": "string"},
    }


def query_positive_float_param(name, description):
    return {
        "name": name,
        "in": "json",
        "required": True,
        "description": description,
        "schema": {"type": "float", "format": "positive"},
    }


def __url_bool_to_python(value):
    if value is None:
        return None

    if value in ["True", "true", "Yes", "yes", "1"]:
        return True

    if value in ["False", "false", "No", "no", "0"]:
        return False

    raise ValueError(f"Cannot convert {value} to bool")


class ResponseSchemaError(Exception):
    def __init__(self, schema, response, errors):
        super().__init__(
            f"Response schema validation error "
            f"schema={schema}, response={response}, errors={errors}"
        )
        self.schema = schema
        self.response = response
        self.errors = errors

    def to_dict(self):
        return {
            "message": "Response schema validation error",
            "schema": self.schema,
            "response": self.response,
            "errors": self.errors,
        }
