import abc

import hashlib
from cached_property import cached_property
from bech32 import bech32_encode, convertbits

BECH32_PUBKEY_DATA_PREFIX = "eb5ae98721"


def _address_from_public_key(pbk: bytes) -> bytes:
    sha = hashlib.sha256()
    rip = hashlib.new("ripemd160")
    sha.update(pbk)
    rip.update(sha.digest())
    return rip.digest()


def _get_bech(prefix: str, payload: str) -> str:
    return bech32_encode(
        prefix, convertbits(bytes.fromhex(payload), 8, 5)
    )  # base64 -> base32


class Key(object, metaclass=abc.ABCMeta):
    """Abstract interface for managing a Terra private key / public key pair."""

    _base_address = ""  # use for determining (acc, val) addresses w/ Bech32

    def __repr__(self) -> str:
        return f"Key({self.acc_address})"

    @property
    @abc.abstractmethod
    def public_key(self) -> bytes:
        """Get the Key's associated public key."""
        raise NotImplementedError("Keys must implement public_key property")

    @cached_property
    def base_address(self) -> bytes:
        """Get's the Key's base address for determining Bech32 acc, val addresses."""
        sha = hashlib.sha256()
        rip = hashlib.new("ripemd160")
        sha.update(self.public_key)
        rip.update(sha.digest())
        return rip.digest()

    @abc.abstractmethod
    def sign(self, payload: bytes) -> bytes:
        """Signs a bytes payload with the private key."""
        raise NotImplementedError("Keys must implement sign()")

    @property
    def acc_address(self) -> str:
        """Get's the key's associated account (terra- prefixed) address."""
        return _get_bech("terra", self.base_address.hex())

    @property
    def acc_pubkey(self) -> str:
        """Get's the key's associated Terra public key (terrapub- prefixed)"""
        return _get_bech("terrapub", BECH32_PUBKEY_DATA_PREFIX + self.public_key.hex())

    @property
    def val_address(self) -> str:
        """Get's the key's associated validator operator (terravaloper- prefixed) address."""
        return _get_bech("terravaloper", self.base_address.hex())

    @property
    def val_pubkey(self) -> str:
        """Get's the key's associated Terra public key (terrapub- prefixed)"""
        return _get_bech(
            "terravaloperpub", BECH32_PUBKEY_DATA_PREFIX + self.public_key.hex()
        )
