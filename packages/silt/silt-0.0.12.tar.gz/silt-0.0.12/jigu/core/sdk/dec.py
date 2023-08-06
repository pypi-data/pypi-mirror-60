from __future__ import annotations
from typing import Union, Dict, List, Iterable

from decimal import Decimal

from jigu.util import JSONSerializable, JSONDeserializable


class Dec(Decimal, JSONSerializable, JSONDeserializable):
    """Serializes as a string with 18 points of Decimal precision."""

    def __new__(cls, *args, **kwargs):
        return Decimal.__new__(cls, *args, **kwargs)

    def __repr__(self):
        if self.is_zero():
            return "sdk.Dec(0)"
        r = Decimal.__str__(self).rstrip("0")
        return f"sdk.Dec({r})"

    def __str__(self) -> str:
        if self.is_nan() or self.is_infinite():
            return Decimal.__str__(self)
        elif self.is_zero():
            return "0.000000000000000000"
        else:
            number_part, dec_part = Decimal.__str__(self).split(".")
            return f"{number_part}.{dec_part.ljust(18, '0')}"

    def to_dict(self) -> str:
        return self.__str__()

    @classmethod
    def from_dict(cls, data: str) -> Dec:
        return cls(data)
