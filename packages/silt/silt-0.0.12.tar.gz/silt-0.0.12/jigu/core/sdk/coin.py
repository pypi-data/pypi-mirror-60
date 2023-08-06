from __future__ import annotations
from typing import Union, Dict, List, Iterable


import warnings
from decimal import Decimal
from jigu.core import Denom, Dec
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.error import DenomIncompatibleError


class Coin(JSONSerializable, JSONDeserializable):
    def __init__(self, denom: str, amount: Union[str, int, Decimal]):
        self.denom = denom
        # guards from accidents
        if type(amount) == float:
            warnings.warn(
                f"Coin amount {amount} (float) and will be converted to int; use strings for decimal amount.",
                SyntaxWarning,
            )
            self.amount = int(amount)
        elif "." in str(amount):
            self.amount = Dec(amount)
        else:
            try:
                self.amount = int(amount)
            except ValueError:
                raise ValueError(f"{amount} not an acceptable value for Coin amount")

    def __repr__(self) -> str:
        if self.denom == "ununsed":
            return "UNUSED"
        else:
            return f"Coin({self.__str__()})"

    def __str__(self) -> str:
        return f"{self.amount}{self.denom}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Coin):
            return self.denom == other.denom and self.amount == other.amount
        else:
            return False

    def __add__(self, other: Coin) -> Coin:
        if self.denom != other.denom:
            raise DenomIncompatibleError(
                f"can't add Coins of different denoms '{self.denom}' and '{other.denom}'"
            )
        return Coin(denom=self.denom, amount=self.amount + other.amount)

    def __sub__(self, other: Coin) -> Coin:
        if self.denom != other.denom:
            raise DenomIncompatibleError(
                f"can't subtract Coins of different denoms '{self.denom}' and '{other.denom}'"
            )
        return Coin(denom=self.denom, amount=self.amount - other.amount)

    def __lt__(self, other: Coin) -> bool:
        if self.denom != other.denom:
            raise DenomIncompatibleError(
                f"can't compare Coins of different denoms '{self.denom}' and '{other.denom}'"
            )
        return self.amount < other.amount

    def __gt__(self, other: Coin) -> bool:
        if self.denom != other.denom:
            raise DenomIncompatibleError(
                f"can't compare Coins of different denoms '{self.denom}' and '{other.denom}'"
            )
        return self.amount > other.amount

    def __ge__(self, other: Coin) -> bool:
        return self > other or self == other

    def __le__(self, other: Coin) -> bool:
        return self < other or self == other

    def to_dict(self) -> dict:
        return {"denom": str(self.denom), "amount": str(self.amount)}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Coin:
        return cls(denom=data["denom"], amount=data["amount"])


class Coins(dict, JSONSerializable, JSONDeserializable):
    def __init__(self, coins: Iterable[Coin]):
        dict.__init__(self)
        for coin in list(coins):
            if self.get(coin.denom, None) is None:
                self[coin.denom] = coin
            else:
                self[coin.denom] = coin + self[coin.denom]

    def __repr__(self):
        return f"Coins({str(self)})"

    def __str__(self):
        return ", ".join(str(coin) for coin in self.coins)

    def to_dict(self) -> List[Dict[Denom, str]]:
        return [coin.to_dict() for coin in self.values()]

    def __add__(self, other: Coins):
        return Coins([coin for coin in other] + self.coins)

    @classmethod
    def from_dict(cls, data: List[Dict[Denom, str]]) -> Coins:
        coins = map(Coin.from_dict, data)
        return cls(coins)

    @property
    def denoms(self) -> List[Denom]:
        return sorted(list(self.keys()))

    @property
    def coins(self) -> List[Coin]:
        return sorted(list(self.values()), key=lambda c: c.denom)

    def __iter__(self):
        return iter(self.coins)
