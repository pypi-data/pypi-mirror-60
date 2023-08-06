from __future__ import annotations
from typing import Dict, Union, Any
from jigu.core import Coin, Dec
from jigu.util import JSONSerializable, JSONDeserializable, pretty_repr


class PolicyConstraints(JSONSerializable, JSONDeserializable):
    def __init__(self, rate_min: Dec, rate_max: Dec, cap: Coin, change_max: Dec):
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.cap = cap
        self.change_max = change_max

    def __repr__(self) -> str:
        return pretty_repr(
            "PolicyConstraints",
            ("Rate (min):", self.rate_min),
            ("Rate (MAX):", self.rate_max),
            ("Max Change:", self.change_max),
            ("Cap:", self.cap),
        )

    def to_dict(self) -> Dict[str, Union[Dec, Coin]]:
        return {
            "rate_min": self.rate_min,
            "rate_max": self.rate_max,
            "cap": self.cap,
            "change_max": self.change_max,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PolicyConstraints:
        return cls(
            rate_min=Dec(data["rate_min"]),
            rate_max=Dec(data["rate_max"]),
            cap=Coin.from_dict(data["cap"]),
            change_max=Dec(data["change_max"]),
        )
