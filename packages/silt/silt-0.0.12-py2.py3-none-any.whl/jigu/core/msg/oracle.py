from __future__ import annotations
from typing import List, Dict, Any, Union
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.core import Coin, Coins, AccAddress

from jigu.core.msg import Message


class MsgExchangeRateVote(Message):

    type = "oracle/MsgExchangeRateVote"
    action = "exchange_rate_vote"

    def __init__(
        self,
        exchange_rate: Coin,
        salt: str,
        denom: Denom,
        feeder: AccAddress,
        validator: ValAddress,
    ):
        validate_acc_address(feeder)
        validate_val_address(validator)
        self.exchange_rate = exchange_rate
        self.salt = salt
        self.denom = denom
        self.feeder = feeder
        self.validator = validator

    def msg_value(self) -> Dict[str, str]:
        return {
            "exchange_rate": str(self.exchange_rate.amount),
            "salt": self.salt,
            "denom": self.denom,
            "feeder": self.feeder,
            "validator": self.validator,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgExchangeRateVote:
        xr = Coin(data["denom"], data["exchange_rate"])
        return cls(
            exchange_rate=xr,
            salt=data["salt"],
            denom=xr.denom,
            feeder=data["feeder"],
            validator=data["validator"],
        )


class MsgExchangeRatePrevote(Message):

    type = "oracle/MsgExchangeRatePrevote"
    action = "exchange_rate_prevote"

    def __init__(
        self, hash: str, denom: Denom, feeder: AccAddress, validator: ValAddress
    ):
        validate_acc_address(feeder)
        validate_val_address(validator)
        self.hash = hash
        self.denom = denom
        self.feeder = feeder
        self.validator = validator

    def msg_value(self) -> Dict[str, str]:
        return {
            "hash": self.hash,
            "denom": self.denom,
            "feeder": self.denom,
            "validator": self.validator,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgExchangeRatePrevote:
        return cls(
            hash=data["hash"],
            denom=data["denom"],
            feeder=data["feeder"],
            validator=data["validator"],
        )


class MsgDelegateFeedConsent(Message):

    type = "oracle/MsgDelegateFeedConsent"
    action = "delegate_feed_consent"

    def __init__(self, operator: ValAddress, delegate: AccAddress):
        validate_val_address(operator)
        validate_acc_address(delegate)
        self.operator = operator
        self.delegate = delegate

    def msg_value(self) -> Dict[str, str]:
        return {"operator": self.operator, "delegate": self.delegate}

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgDelegateFeedConsent:
        return cls(operator=data["operator"], delegate=data["delegate"])

