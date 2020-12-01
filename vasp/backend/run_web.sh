#!/bin/bash

export FLASK_ENV=${COMPOSE_ENV:-development}
export FLASK_APP="webapp:init()"

flask run --host 0.0.0.0 --port ${MERCHANT_BACKEND_PORT:-5000}
