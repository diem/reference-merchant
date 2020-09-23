#!/bin/bash

# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

set -e

export LP_DB_NAME="liquidity_provider_db"
export VASP_DB_NAME="vasp_backend_db"
export DB_USER="backenduser"
export DB_PASSWORD="backendpassword"

psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    CREATE DATABASE $VASP_DB_NAME;
    GRANT ALL PRIVILEGES ON DATABASE $VASP_DB_NAME TO $DB_USER;
EOSQL

psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $LP_DB_NAME;
    GRANT ALL PRIVILEGES ON DATABASE $LP_DB_NAME TO $DB_USER;
EOSQL
