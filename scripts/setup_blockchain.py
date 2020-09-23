# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

import sys
import os
import dotenv

from libra_utils.vasp import Vasp
from libra_utils.custody import Custody


wallet_env_file_path = os.path.join(os.getcwd(), "vasp/backend", ".env")

print(f"Loading {wallet_env_file_path}")
dotenv.load_dotenv(dotenv_path=wallet_env_file_path)

Custody.init()
wallet_custody_account_name = os.getenv(
    "WALLET_CUSTODY_ACCOUNT_NAME", "merchant-wallet"
)
vasp = Vasp(wallet_custody_account_name)
vasp.setup_blockchain()
