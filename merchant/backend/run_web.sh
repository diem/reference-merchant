#!/bin/bash

export FLASK_ENV=${COMPOSE_ENV:-development}
export FLASK_APP=src/webapp
export SETUP_FAKE_DATA=1

if [ "$FLASK_ENV" != "production"  ]; then
  PIPENV=pipenv run
fi

bash
${PIPENV} flask run --host 0.0.0.0 --port ${MERCHANT_BACKEND_PORT:-5000}
