# pyre-strict
import logging
import os
import time

import psycopg2
from flask import Flask, request
from flask.logging import default_handler
from sqlalchemy.exc import IntegrityError
from werkzeug.middleware.proxy_fix import ProxyFix

from merchant_vasp.config import DB_URL
from merchant_vasp.storage import db_session, engine, models, Merchant
from .routes import vasp, vasp_wallet

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(default_handler)


def _wait_for_postgres():
    if "sqlite:" in DB_URL:
        return

    retries = 30

    for i in range(retries):
        try:
            conn = psycopg2.connect(DB_URL)
            app.logger.info("Postgres is ready!")
            conn.close()
            return
        except psycopg2.OperationalError:
            app.logger.warning("Postgres is not ready, waiting...")
            time.sleep(1)

    app.logger.error("Database failed to start, exiting...")
    exit(1)


def _setup_fake_merchant():
    try:
        merchant_name = os.getenv("FAKE_MERCHANT_NAME", "LRM Merchant")

        if Merchant.query.filter_by(name=merchant_name).first():
            return

        db_session.add(
            Merchant(
                name=merchant_name,
                settlement_information=os.getenv(
                    "FAKE_MERCHANT_SETTLEMENT_INFO", "Fake Bank, Account #808-909"
                ),
                settlement_currency="USD",
                api_key=os.getenv("FAKE_MERCHANT_API_KEY", "abcdefghijklmnop"),
            )
        )
        db_session.commit()
    except IntegrityError:
        pass


def _create_db(app: Flask) -> None:
    with app.app_context():
        models.Base.metadata.create_all(bind=engine)


def _create_app() -> Flask:
    app = Flask(__name__, static_folder='../pay_with_diem/build', static_url_path='/pay/')

    app.debug = True

    # register api endpoints
    app.register_blueprint(vasp)
    app.register_blueprint(vasp_wallet)

    # pyre-ignore[8]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

    return app


app: Flask = _create_app()


def init() -> Flask:
    _wait_for_postgres()
    _create_db(app)
    _setup_fake_merchant()
    app.logger.info("App init complete!")
    return app


@app.before_request
def log_request_info():
    app.logger.debug("Headers: %s", repr(request.headers))
    app.logger.debug("Body: %s", repr(request.get_data()))


@app.teardown_appcontext
def remove_session(*args, **kwargs) -> None:  # pyre-ignore
    db_session.remove()
