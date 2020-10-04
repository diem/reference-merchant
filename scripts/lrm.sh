#!/usr/bin/env bash

# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

script_dir="$(dirname "$0")"
project_dir="$(dirname "$script_dir")"

source "$script_dir/funcs.sh"

show_help() {
  echo ""
  warn "Libra reference merchant C&C"
  echo ""
  echo "Usage: scripts/lrm.sh <command>"
  echo ""
  info "Commands:"
  echo ""
  echo "setup_environment          Create a .env file with custody private key and wallet public address for the project."
  echo "start <port>               Build project and run all components in production mode."
  echo "develop <port>             Build project and run all components in development mode."
  echo "logs                       Show services logs when debug mode is active"
  echo "down                       Stop all running services and remove them"
  echo "stop                       Stop all running services"
  echo "build                      Rebuild all services"
  echo "purge                      Reset local database"
  echo
}

OPTIND=1

PRODUCTION=1
COMPOSE_YAML=docker/docker-compose.yaml
COMPOSE_DEV_YAML=docker/dev.docker-compose.yaml
PG_VOLUME=pg-data
export GW_PORT=8080

frontend=frontend
backend=vasp-backend-web-server
gateway=gateway
db_file=/tmp/test.db



run() {
  local cmd=$1;
  shift 1
  if type "$cmd" >/dev/null 2>&1; then
    "$cmd" "$@"
  else
    echo "$cmd doesn't exist"
  fi
}

build() {
  info "***Building Pay-with-Libra***"
  (cd vasp/backend/pay_with_libra; REACT_APP_BACKEND_URL=/vasp yarn build) || fail 'pay-with-libra build failed!'

  info "***Building docker services***"
  # build all the service images using compose
  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} build  || fail 'docker-compose build failed!'
}

start() {
  build "$@"
  # run
  GW_PORT=$port docker-compose -f ${COMPOSE_YAML} up --detach
  docker-compose -f ${COMPOSE_YAML} logs --follow
}

develop() {
  local port=${1:-8000}
  local follow=${2:-true}
  echo "debug mode with gw port ${port}"

  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} pull redis

  GW_PORT=$port docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} up --detach --no-build

  if [ "$follow" == true ]; then
    docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} logs --follow --tail=500
    stop
  fi
}


purge() {
  info "Remove pg volume"
  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} down
  docker volume rm -f lrm_${PG_VOLUME}
}

logs() {
  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} logs --follow
}

down() {
  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} down
}

stop() {
  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} stop
}

setup_environment() {
  if ! command -v yarn -v &> /dev/null
  then
    fail "yarn not found"
  fi

  if ! command -v python &> /dev/null
  then
    fail "Install Python 3.7 or greater"
  fi

  if ! python -c 'import sys; assert sys.version_info >= (3, 7)' &> /dev/null
  then
    fail "You need Python 3.7 or greater installed and mapped to the 'python' command"
  fi

  if ! command -v pipenv &> /dev/null
  then
    ec "Installing pipenv"
    pip install pipenv
    exit
  fi

  info "***Initializing utilities submodule***"
  git submodule update --init

  info "***Installing vasp backend dependencies***"
  sh -c "cd vasp/backend && pipenv install --dev"

  info "***Installing merchant backend dependencies***"
  sh -c "cd merchant/backend && pipenv install --dev"

  info "***Installing merchant frontend dependencies***"
  sh -c "cd merchant/frontend && yarn"

  info "***Installing liquidity dependencies***"
  sh -c "cd liquidity && pipenv install --dev"

  info "***Setting up environment .env files***"
  PIPENV_PIPFILE=vasp/backend/Pipfile pipenv run python scripts/set_env.py

  info "***Setting up blockchain Vasp account***"
  PIPENV_PIPFILE=vasp/backend/Pipfile pipenv run python scripts/setup_blockchain.py

  info "***Setting up docker-compose project name***"
  cp .env.example .env
}
# make sure we actually *did* get passed a valid function name
if declare -f "$1" >/dev/null 2>&1; then
  # invoke that function, passing arguments through
  "$@" # same as "$1" "$2" "$3" ... for full argument list

else
  show_help
  exit 1
fi