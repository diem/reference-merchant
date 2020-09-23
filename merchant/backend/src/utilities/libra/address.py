## Copied and modified from lrw/src/wallet/storage/subaddress.py

import os
from bech32 import encode as bech32encode, decode as bech32decode

VASP_ADDRESS_LENGTH: int = 16
SUBADDRESS_LENGTH: int = 8

HRP_TESTNET = "tlb"
HRP_MAINNET = "lbr"


class LibraAddress(object):
    @staticmethod
    def encode_full_addr(vasp_addr, subaddr=None, hrp=HRP_TESTNET) -> str:
        if subaddr is None or subaddr == "":
            version = 0
            raw_bytes = bytes.fromhex(vasp_addr)
        else:
            version = 1
            if isinstance(subaddr, str):
                subaddr = LibraAddress.encode_subaddr(subaddr)
            raw_bytes = bytes.fromhex(vasp_addr) + subaddr
        encoded_addr = bech32encode(hrp, version, raw_bytes)
        if encoded_addr is None:
            raise ValueError(f'Cannot convert to LibraAddress: "{raw_bytes}"')

        return encoded_addr

    # returns address, subaddress tuple
    @staticmethod
    def decode_full_addr(encoded_address, hrp=HRP_TESTNET):
        assert hrp in (HRP_TESTNET, HRP_MAINNET)
        # Do basic bech32 decoding
        version, decoded_address = bech32decode(hrp, encoded_address)
        if decoded_address is None:
            raise ValueError(
                f'Incorrect version or bech32 encoding: "{encoded_address}"'
            )
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
            if len(decoded_address) < VASP_ADDRESS_LENGTH + SUBADDRESS_LENGTH:
                raise ValueError(
                    f"Libra network sub-address must be > 16+8"
                    f' bytes, found: "{len(decoded_address)}"'
                )

            addr_bytes = bytes(decoded_address)
            return (
                addr_bytes[:VASP_ADDRESS_LENGTH].hex(),
                addr_bytes[VASP_ADDRESS_LENGTH:].hex(),
            )

    @staticmethod
    def gen_raw_subaddr() -> bytes:
        """
        Return a raw subaddress bytestring of a given length
        """
        return os.urandom(SUBADDRESS_LENGTH)

    @staticmethod
    def encode_subaddr(subaddr: str) -> bytes:
        return bytes.fromhex(subaddr)

    @staticmethod
    def decode_subaddr(subaddr: bytes) -> str:
        return subaddr.hex()
