from dataclasses import dataclass

import flasgger
from dataclasses_json import DataClassJsonMixin
from dataclasses_json.mm import build_schema
from flask import request, current_app
from requests import RequestException

BEARER_LEN = len("Bearer ")


def _patch_flassger():
    validate_fn = flasgger.utils.validate

    def patched_validate(*args, **kwargs):
        kwargs["require_data"] = False
        validate_fn(*args, **kwargs)

    flasgger.utils.validate = patched_validate


_patch_flassger()


def is_valid_token(_):
    """
    Placeholder until we have proper authorization.
    """
    return True


@dataclass
class Token:
    user_id: str


def get_token(_):
    """
    Placeholder until we have proper authorization.
    """
    return Token(user_id="007")


class StrictSchemaView(flasgger.SwaggerView):
    """
    A Flask view handling Swagger generation and response/request schema
    validation.

    Note that, as opposed to the original Flask MethodView, the view methods
    (get, post etc.) support returning only (response, status_code) tuples.
    For errors it is possible to raise exceptions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_id = None

        self.logger = None

        if self.parameters:
            for p in self.parameters:
                param_type = p.get("in", None)
                if param_type == "body":
                    self.validation = True
                    break

    @property
    def user_id(self):
        if self._user_id is None:
            raise AttributeError("User ID is unavailable when not in a request context")
        return self._user_id

    def dispatch_request(self, *args, **kwargs):
        self.logger = current_app.logger

        token = get_auth_token_from_headers(request.headers)
        if not is_valid_token(token):
            return "Unauthenticated", 401

        self._user_id = get_token(token).user_id

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

        self._user_id = None
        self.logger = None

        validate_response(response, status_code, self.responses)

        return response, status_code


def validate_response(response, http_status_code, response_definitions):
    schema_factory = (
        response_definitions.get(http_status_code, {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
    )
    if not schema_factory:
        return
    schema = schema_factory()
    response = schema.dump(response)
    errors = schema.validate(response)
    if errors:
        raise ResponseSchemaError(schema.__class__.__name__, response, errors)


def get_auth_token_from_headers(headers):
    return headers.get("Authorization", "")[BEARER_LEN:]


def response_definition(description, schema):
    """Helps to create response definitions"""
    return {
        "description": description,
        "content": {"application/json": {"schema": schema}},
    }


def body_parameter(klass):
    return {
        "name": "body",
        "in": "body",
        "required": True,
        "schema": build_schema(klass, DataClassJsonMixin, False, False),
    }


def query_bool_param(name, description, required):
    return {
        "name": name,
        "in": "query",
        "required": required,
        "description": description,
        "schema": {"type": "boolean"},
    }


def path_str_param(name, description, required):
    return {
        "name": name,
        "in": "path",
        "required": required,
        "description": description,
        "schema": {"type": "string"},
    }


def path_uuid_param(name, description):
    return {
        "name": name,
        "in": "path",
        "required": True,
        "description": description,
        "schema": {"type": "string", "format": "uuid", },
    }


def url_bool_to_python(value):
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
