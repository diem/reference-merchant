# pyre-strict

from flasgger import Swagger
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from storage import storage

from .api import api


def _create_app() -> Flask:
    app = Flask(__name__)

    # Register api endpoints
    app.register_blueprint(api)

    # pyre-ignore[8]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

    return app


app: Flask = _create_app()


@app.before_first_request
def lazy_init() -> None:
    with app.app_context():
        storage.setup()


@app.teardown_appcontext
def remove_session(*args, **kwargs) -> None:  # pyre-ignore
    storage.cleanup()
