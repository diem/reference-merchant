# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

import os

JSON_RPC_URL = os.getenv("JSON_RPC_URL", "https://testnet.libra.org/v1")
VASP_ADDR = os.getenv("VASP_ADDR")

DEFL_CONFIG = {
    "libra_node_uri": JSON_RPC_URL,
    "sync_interval_ms": 1000,
    "progress_file_path": "/tmp/pubsub_progress",
    "accounts": [VASP_ADDR],
    "log_file": "/tmp/pubsub_log",
    "progress_storage_type": "file",
    "account_subscription_storage_type": "in_memory",
    "transaction_progress_storage_type": "in_memory",
    "transaction_progress_storage_config": {},
    "pubsub_type": "pubsub.client.LRWPubSubClient",
    "pubsub_config": {"file_path": "/tmp/pubsub_messages"},
    "sync_strategy_type": "event_stream",
    "sync_strategy_config": {"subscription_fetch_interval_ms": 1000, "batch_size": 2, },
}
