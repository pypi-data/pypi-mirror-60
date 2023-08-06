from __future__ import annotations
from typing import List, Dict, Any, Union
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address
from jigu.core import Coin, Coins, AccAddress

from jigu.core.msg import Message


class MsgSwap(Message):

    type = "market/MsgSwap"
    action = "swap"

    def __init__(self, trader: AccAddress, offer_coin: Coin, ask_denom: Denom):
        validate_acc_address(trader)
        self.trader = trader
        self.offer_coin = offer_coin
        self.ask_denom = ask_denom

    def msg_value(self) -> Dict[str, Any]:
        return {
            "trader": self.trader,
            "offer_coin": self.ask_denom,
            "ask_denom": self.ask_denom,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, Any]) -> MsgSwap:
        return cls(
            trader=data["trader"],
            offer_coin=Coin.from_dict(data["offer_coin"]),
            ask_denom=data["ask_denom"],
        )
