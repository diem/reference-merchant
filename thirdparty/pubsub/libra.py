# pyre-ignore-all-errors

# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

import os
from dataclasses import dataclass
from typing import Optional, Tuple, List

from bech32 import encode, decode
from libra import testnet, jsonrpc
from libra.jsonrpc import CurrencyInfo

ASSOC_ADDRESS: str = "0000000000000000000000000a550c18"
ASSOC_AUTHKEY: str = "3126dc954143b1282565e8829cd8cdfdc179db444f64b406dee28015fce7f392"

VASP_ADDRESS_LENGTH: int = 16
SUB_ADDRESS_LENGTH: int = 8


# tlb for testnet, lbr for mainnet
def encode_full_addr(
        vasp_addr: str, sub_address: Optional[str] = None, hrp: str = "tlb"
) -> str:
    if sub_address is None or sub_address == "":
        version = 0
        raw_bytes = bytes.fromhex(vasp_addr)
    else:
        version = 1
        raw_bytes_sub_address = encode_sub_address(sub_address)
        raw_bytes = bytes.fromhex(vasp_addr) + raw_bytes_sub_address
    encoded_addr = encode(hrp, version, raw_bytes)
    if encoded_addr is None:
        raise ValueError(f'Cannot convert to LibraAddress: "{raw_bytes}"')

    return encoded_addr


# returns address, sub address tuple
def decode_full_addr(
        encoded_address: str, hrp: str = "tlb"
) -> Tuple[str, Optional[str]]:
    assert hrp in ("lbr", "tlb")
    # Do basic bech32 decoding
    version, decoded_address = decode(hrp, encoded_address)
    if decoded_address is None:
        raise ValueError(f'Incorrect version or bech32 encoding: "{encoded_address}"')
    # Set the version
    if version == 0:
        # This is a libra network address without subaddress.
        if len(decoded_address) != VASP_ADDRESS_LENGTH:
            raise ValueError(
                f"Libra network address must be 16"
                f' bytes, found: "{len(decoded_address)}"'
            )
        return bytes(decoded_address).hex(), None

    elif version == 1:
        # This is a libra network sub-address
        if len(decoded_address) < VASP_ADDRESS_LENGTH + SUB_ADDRESS_LENGTH:
            raise ValueError(
                f"Libra network sub-address must be > 16+8"
                f' bytes, found: "{len(decoded_address)}"'
            )

        addr_bytes = bytes(decoded_address)
        return (
            addr_bytes[:VASP_ADDRESS_LENGTH].hex(),
            addr_bytes[VASP_ADDRESS_LENGTH:].hex(),
        )


def gen_raw_subaddr() -> bytes:
    """
    Return a raw sub address bytestring of a given length
    """
    return os.urandom(SUB_ADDRESS_LENGTH)


def gen_sub_address() -> str:
    return decode_sub_address(gen_raw_subaddr())


def encode_sub_address(sub_address: str) -> bytes:
    return bytes.fromhex(sub_address)


def decode_sub_address(sub_address: bytes) -> str:
    return sub_address.hex()


@dataclass
class TransactionMetadata:
    def __init__(
            self,
            to_sub_address: bytes = b"",
            from_sub_address: bytes = b"",
            referenced_event: bytes = b"",
    ) -> None:
        self.to_sub_address: bytes = to_sub_address
        self.from_sub_address: bytes = from_sub_address
        self.referenced_event: bytes = referenced_event

    def to_bytes(self) -> bytes:
        ret = b""
        if self.to_sub_address:
            ret += b"\x01" + self.to_sub_address
        else:
            ret += b"\x00"

        if self.from_sub_address:
            ret += b"\x01" + self.from_sub_address
        else:
            ret += b"\x00"

        if self.referenced_event:
            ret += b"\x01" + self.referenced_event
        else:
            ret += b"\x00"

        return ret

    @staticmethod
    def from_bytes(lcs_bytes: bytes) -> "TransactionMetadata":
        """
        Parse transaction metadata by LCS standard. On error, return empty
        """
        if len(lcs_bytes) == 0:
            print("Metadata empty")
            return TransactionMetadata()

        curr_byte = 2
        to_sub_address, from_sub_address, referenced_event = b"", b"", b""

        try:
            to_sub_address_present = lcs_bytes[curr_byte] == 0x01
            curr_byte += 1
            if not to_sub_address_present:  # to_sub_address is mandatory
                return TransactionMetadata()
            to_sub_address = lcs_bytes[curr_byte: curr_byte + 8]
            curr_byte += 8

            from_sub_address_present = lcs_bytes[curr_byte] == 0x01
            curr_byte += 1
            if from_sub_address_present:
                from_sub_address = lcs_bytes[curr_byte: curr_byte + 8]
                curr_byte += 8

            referenced_event_present = lcs_bytes[curr_byte] == 0x01
            curr_byte += 1
            if referenced_event_present:
                referenced_event = lcs_bytes[curr_byte:]

            return TransactionMetadata(to_sub_address, from_sub_address, referenced_event)
        except IndexError:
            print("Metadata malformed")
            return TransactionMetadata()


def encode_txn_metadata(meta: TransactionMetadata) -> bytes:
    return meta.to_bytes()


def decode_txn_metadata(meta_bytes: bytes) -> "TransactionMetadata":
    return TransactionMetadata.from_bytes(meta_bytes)


def get_network_supported_currencies() -> List[CurrencyInfo]:
    api = jsonrpc.Client(testnet.JSON_RPC_URL)

    return api.get_currencies()
