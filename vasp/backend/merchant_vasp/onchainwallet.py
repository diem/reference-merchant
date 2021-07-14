# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

import os

from diem import testnet, jsonrpc, diem_types
from diem_utils.custody import Custody
from diem_utils.vasp import Vasp

from merchant_vasp.config import JSON_RPC_URL

CHAIN_ID = diem_types.ChainId(value=os.getenv("CHAIN_ID", testnet.CHAIN_ID.value))

Custody.init(CHAIN_ID)


class OnchainWallet(Vasp):
    def __init__(self):
        wallet_custody_account_name = os.getenv(
            "WALLET_CUSTODY_ACCOUNT_NAME", "merchant-wallet"
        )
        super().__init__(jsonrpc.Client(JSON_RPC_URL), wallet_custody_account_name)
