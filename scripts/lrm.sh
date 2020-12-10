#!/usr/bin/env bash

# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

script_dir="$(dirname "$0")"
project_dir="$(dirname "$script_dir")"

source "$script_dir/funcs.sh"

show_help() {
  echo ""
  warn "Diem reference merchant C&C"
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
  echo "build <build_mode>         Rebuild all services. Build mode `helm` will build images for helm chart."
  echo "purge                      Reset local database"
  echo
}

OPTIND=1

PRODUCTION=1
COMPOSE_YAML=docker/docker-compose.yaml
COMPOSE_DEV_YAML=docker/dev.docker-compose.yaml
COMPOSE_STATIC_YAML=docker/static.docker-compose.yaml
PG_VOLUME=pg-data
export GW_PORT=8080

frontend=frontend
backend=vasp-backend-web-server
gateway=gateway
db_file=/tmp/test.db

run() {
  local cmd=$1
  shift 1
  if type "$cmd" >/dev/null 2>&1; then
    "$cmd" "$@"
  else
    echo "$cmd doesn't exist"
  fi
}

build_helm() {
  info "running docker to compile frontend..."
  docker build -t reference-merchant-frontend-build -f "${project_dir}/merchant/frontend/Dockerfile" "${project_dir}/merchant/frontend/" || fail 'merchant frontend container build failed!'
  docker create --name tmp_reference_merchant_frontend reference-merchant-frontend-build || fail 'frontend compilation failed!'
  rm -rf "${project_dir}/gateway/tmp/frontend/"
  mkdir -p "${project_dir}/gateway/tmp/frontend/"
  docker cp tmp_reference_merchant_frontend:/app/build/. "${project_dir}/gateway/tmp/frontend/" || fail 'frontend copy artifacts failed!'
  docker rm tmp_reference_merchant_frontend
  info "frontend build completed"

  docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_STATIC_YAML} build || fail 'docker-compose build failed!'
}

build() {
  local build_mode=$1
  info "build mode is ${build_mode}"

  info "***Building Pay-with-Diem***"
  (cd vasp/backend/pay_with_diem; REACT_APP_BACKEND_URL=/vasp yarn build) || fail 'pay-with-diem build failed!'

  if [ "$build_mode" = "helm" ]; then
    build_helm
  else
    info "***Building docker services***"
    # build all the service images using compose
    docker-compose -f ${COMPOSE_YAML} -f ${COMPOSE_DEV_YAML} build || fail 'docker-compose build failed!'
  fi
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

  info "***Installing pay_with_diem yarn***"
  sh -c "cd vasp/backend/pay_with_diem && yarn"

  info "***Installing liquidity dependencies***"
  sh -c "cd liquidity && pipenv install --dev"

  info "***Setup Liquidity Provider***"
  info "***Setup Liquidity Provider***"
  (cd liquidity; pipenv run python setup_env.py || exit 1) || fail "Liquidity service setup failed"

  info "***Setting up environment .env files***"
  PIPENV_PIPFILE=vasp/backend/Pipfile pipenv run python scripts/set_env.py || fail "Merchant setup failed"

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
