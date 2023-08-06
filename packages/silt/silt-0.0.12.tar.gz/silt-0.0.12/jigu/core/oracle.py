from __future__ import annotations
from typing import Dict, Union
from jigu.core import Coin, Denom, ValAddress, Dec
from jigu.util import JSONSerializable, JSONDeserializable, abbreviate
from jigu.util.validation import validate_val_address


class ExchangeRateVote(JSONSerializable, JSONDeserializable):
    def __init__(self, exchange_rate: Coin, denom: Denom, voter: ValAddress):
        validate_val_address(voter)
        self.exchange_rate = exchange_rate
        self.denom = denom
        self.voter = voter

    def __repr__(self):
        if self.exchange_rate.amount <= 0:
            xr = f"ABSTAIN for uluna<>{self.denom}"
        else:
            xr = f"{self.exchange_rate.amount}{self.denom}"
        return f"ExchangeRateVote(voter={abbreviate(self.voter)}, xr={xr})"

    def to_dict(self) -> Dict[str, Union[Dec, Denom, ValAddress]]:
        return {
            "exchange_rate": str(self.exchange_rate.amount),
            "denom": self.denom,
            "voter": self.voter,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ExchangeRateVote:
        xr = Coin(data["denom"], data["exchange_rate"])
        return cls(exchange_rate=xr, denom=xr.denom, voter=data["voter"])


class ExchangeRatePrevote(JSONSerializable, JSONDeserializable):
    def __init__(self, hash: str, denom: Denom, voter: ValAddress):
        validate_val_address(voter)
        self.hash = hash
        self.denom = denom
        self.voter = voter

    def __repr__(self):
        return f"ExchangeRatePrevote(voter={abbreviate(self.voter)}, hash={self.hash}, denom={self.denom})"

    def to_dict(self) -> Dict[str, str]:
        return {"hash": self.hash, "denom": self.denom, "voter": self.voter}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ExchangeRatePrevote:
        return cls(hash=data["hash"], denom=data["denom"], voter=data["voter"])


def vote_hash(salt: str, exchange_rate: Dec, denom: str, voter: str) -> str:
    payload = f"{salt}:{exchange_rate}:{denom}:{voter}"
    sha_hash = hashlib.sha256(payload.encode()).digest()
    return sha_hash.hexdigest()[:40]
