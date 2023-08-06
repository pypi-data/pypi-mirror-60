from __future__ import annotations

import hashlib
from mnemonic import Mnemonic
from ecdsa import curves, SECP256k1, SigningKey
from ecdsa.util import sigencode_string, sigencode_string_canonize
from bip32utils import BIP32Key, BIP32_HARDEN

from jigu.key import Key


def _derive_root(seed: str) -> BIP32Key:
    return BIP32Key.fromEntropy(bytes.fromhex(seed))


def _derive_child(root: BIP32Key, account: int = 0, index: int = 0):
    # HD Path: 44'/330'/<acc>'/0/<idx>
    return (
        root.ChildKey(44 + BIP32_HARDEN)
        .ChildKey(330 + BIP32_HARDEN)
        .ChildKey(account + BIP32_HARDEN)
        .ChildKey(0)
        .ChildKey(index)
    )


class MnemonicKey(Key):
    """Implements Key interface with 24-word mnemonic."""

    public_key = None

    def __init__(self, mnemonic: str, account: int = 0, index: int = 0):
        self.mnemonic = mnemonic
        seed = Mnemonic("english").to_seed(self.mnemonic).hex()
        root = _derive_root(seed)
        child = _derive_child(root, account, index)
        self.account = account
        self.index = index
        self.private_key = child.PrivateKey()
        self.public_key = child.PublicKey()

    @classmethod
    def generate(cls, account: int = 0, index: int = 0) -> MnemonicKey:
        return cls(
            mnemonic=Mnemonic("english").generate(256), account=account, index=index
        )

    def sign(self, payload: bytes) -> bytes:
        """Sign a payload. Uses ecdsa curves, SECP256k1 by default."""
        sk = SigningKey.from_string(self.private_key, curve=SECP256k1)
        return sk.sign_deterministic(
            payload.encode(),
            hashfunc=hashlib.sha256,
            sigencode=sigencode_string_canonize,
        )
