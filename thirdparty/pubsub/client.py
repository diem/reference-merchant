# pyre-strict

# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
from typing import Any, Dict, Optional

from libra import jsonrpc

from merchant_vasp.background_tasks import process_incoming_txn
from .types import LRWPubSubEvent

logger = logging.getLogger(__name__)


class FileProgressStorage:
    def __init__(self, path: str) -> None:
        self.path = path

    def fetch_state(self) -> Dict[str, int]:
        try:
            with open(self.path, "r") as file:
                return json.loads(file.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_state(self, state: Dict[str, int]) -> None:
        with open(self.path, "w") as file:
            file.write(json.dumps(state))


class LRWPubSubClient:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.sync_interval_ms = config["sync_interval_ms"]
        self.accounts = config["accounts"]

        self.libra_node_uri = config["libra_node_uri"]
        self.progress_file_path = config["progress_file_path"]
        self.fetch_batch_size = 10
        self.processor = config.get("processor", process_incoming_txn)

        logger.info(f"Loaded LRWPubSubClient with config: {config}")

        self.client = jsonrpc.Client(self.libra_node_uri)
        self.progress = FileProgressStorage(self.progress_file_path)

    def start(self) -> None:
        sync_state = self.init_progress_state()
        while True:
            sync_state = self.sync(sync_state, catch_error=True)
            time.sleep(self.sync_interval_ms / 1000)

    def sync(
            self, state: Dict[str, int], catch_error: Optional[bool] = False
    ) -> Dict[str, int]:
        after_sync_state = state.copy()
        for key in state:
            try:
                sequence_num = state[key]
                events = self.client.get_events(
                    key, sequence_num, self.fetch_batch_size
                )
                for event in events:
                    lrw_event = LRWPubSubEvent.from_jsonrpc_event(event)
                    self.processor.send(lrw_event)
                    logger.info(f"SUCCESS: sent to wallet onchain {lrw_event}")

                after_sync_state[key] = sequence_num + len(events)
            except Exception as exc:
                logger.exception(f"failed to perform sync for event key {key}: {exc}")
                if not catch_error:
                    raise exc

        self.progress.save_state(after_sync_state)
        logger.info(f"processed next chunk. New state is {after_sync_state}")

        return after_sync_state

    def init_progress_state(self) -> Dict[str, int]:
        state = self.progress.fetch_state()
        for address in self.accounts:
            account = self.client.get_account(address)
            if account is None:
                logger.error(f"account not found: {address}")
                continue
            if account.received_events_key not in state:
                state[account.received_events_key] = 0
        return state
