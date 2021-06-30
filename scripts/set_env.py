# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from diem import LocalAccount, utils, testnet, diem_types
from diem_utils.custody import Custody
from diem_utils.vasp import Vasp

diem_client = testnet.create_client()

wallet_account_name = "wallet"


def get_private_key_hex(key: Ed25519PrivateKey) -> str:
    return key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()


def init_onchain_account(
        custody_private_keys,
        account_name,
        account: LocalAccount,
        base_url,
        compliance_key,
        chain_id: int
):
    account_addr = utils.account_address_hex(account.account_address)
    print(f'Creating and initialize blockchain account {account_name} @ {account_addr}')
    os.environ["CUSTODY_PRIVATE_KEYS"] = custody_private_keys
    Custody.init(diem_types.ChainId.from_int(chain_id))
    vasp = Vasp(diem_client, account_name)
    vasp.setup_blockchain(base_url, compliance_key)
    print(f'Account initialization done!')

    return vasp


if len(sys.argv) > 2 or len(sys.argv) > 1 and '--help' in sys.argv:
    print("""
    Setup wallet and liquidity environment including blockchain private keys generation.
    Usage: set_env.py
    Flags: --force      Will regenerate blockchain keys and run current .env configuration.
    """)

    exit()

compliance_private_key = Ed25519PrivateKey.generate()

GW_PORT = os.getenv("GW_PORT", 8080)
ENV_FILE_NAME = os.getenv("ENV_FILE_NAME", ".env")
LIQUIDITY_SERVICE_HOST = os.getenv("LIQUIDITY_SERVICE_HOST", "merchant-liquidity")
LIQUIDITY_SERVICE_PORT = os.getenv("LIQUIDITY_SERVICE_PORT", 5000)
JSON_RPC_URL = os.getenv("JSON_RPC_URL", "https://testnet.diem.com/v1")
FAUCET_URL = os.getenv("FAUCET_URL", "https://testnet.diem.com/mint")
CHAIN_ID = int(os.getenv("CHAIN_ID", testnet.CHAIN_ID.value))
OFFCHAIN_SERVICE_PORT: int = int(os.getenv("OFFCHAIN_SERVICE_PORT", 8091))
VASP_BASE_URL = os.getenv("VASP_BASE_URL", "http://0.0.0.0:8091")
VASP_COMPLIANCE_KEY = utils.private_key_bytes(compliance_private_key).hex()
VASP_PUBLIC_KEY_BYTES = utils.public_key_bytes(compliance_private_key.public_key())

wallet_account = LocalAccount.generate()

execution_dir_path = os.getcwd()
wallet_env_file_path = os.path.join(execution_dir_path, "vasp/backend", ENV_FILE_NAME)

print(f"Creating {wallet_env_file_path}")

# setup merchant wallet
with open(wallet_env_file_path, "w") as dotenv:
    private_keys = {f"{wallet_account_name}": get_private_key_hex(wallet_account.private_key)}
    wallet_custody_private_keys = json.dumps(private_keys, separators=(',', ':'))
    dotenv.write(f"GW_PORT={GW_PORT}\n")
    dotenv.write(f"WALLET_CUSTODY_ACCOUNT_NAME={wallet_account_name}\n")
    dotenv.write(f"CUSTODY_PRIVATE_KEYS={wallet_custody_private_keys}\n")
    dotenv.write(f"VASP_ADDR={utils.account_address_hex(wallet_account.account_address)}\n")
    dotenv.write(f"VASP_BASE_URL={VASP_BASE_URL}\n")
    dotenv.write(f"VASP_COMPLIANCE_KEY={VASP_COMPLIANCE_KEY}\n")
    dotenv.write(f"LIQUIDITY_SERVICE_HOST={LIQUIDITY_SERVICE_HOST}\n")
    dotenv.write(f"LIQUIDITY_SERVICE_PORT={LIQUIDITY_SERVICE_PORT}\n")
    dotenv.write(f"OFFCHAIN_SERVICE_PORT={OFFCHAIN_SERVICE_PORT}\n")
    dotenv.write(f"JSON_RPC_URL={JSON_RPC_URL}\n")
    dotenv.write(f"FAUCET_URL={FAUCET_URL}\n")
    dotenv.write(f"CHAIN_ID={CHAIN_ID}\n")

    init_onchain_account(
        custody_private_keys=wallet_custody_private_keys,
        account_name=wallet_account_name,
        account=wallet_account,
        base_url=VASP_BASE_URL,
        compliance_key=VASP_PUBLIC_KEY_BYTES,
        chain_id=CHAIN_ID
    )
