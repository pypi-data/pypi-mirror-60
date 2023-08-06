from __future__ import annotations
from typing import List, Dict, Any, Union, Type
import abc

from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.core import *
from jigu.core.denoms import uLuna


class StdMsg(JSONSerializable, JSONDeserializable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def msg_value(self) -> Dict[str, Any]:
        raise NotImplementedError("StdMsg must implement msg_value()")

    @classmethod
    @abc.abstractmethod
    def from_msg_dict(cls, data: Dict[str, Any]) -> Type[StdMsg]:
        raise NotImplementedError("StdMsg must implement from_msg_dict()")

    @property
    @abc.abstractmethod
    def type(self):
        raise NotImplementedError("StdMsg must have property type")

    @property
    @abc.abstractmethod
    def action(self):
        raise NotImplementedError("StdMsg must have property action")

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.msg_value()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Type[StdMsg]:
        data = data["value"]
        return cls.from_msg_dict(data)


Message = StdMsg

from .bank import MsgSend, MsgMultiSend
from .distribution import (
    MsgSetWithdrawAddress,
    MsgWithdrawDelegationReward,
    MsgWithdrawValidatorCommission,
)
from .oracle import MsgExchangeRatePrevote, MsgExchangeRateVote, MsgDelegateFeedConsent
from .gov import MsgSubmitProposal, MsgVote, MsgDeposit
from .market import MsgSwap
from .staking import (
    MsgBeginRedelegate,
    MsgDelegate,
    MsgUndelegate,
    MsgEditValidator,
    MsgCreateValidator,
)

MSGTYPES = {
    "bank/MsgSend": MsgSend,
    "bank/MsgMultiSend": MsgMultiSend,
    "distribution/MsgSetWithdrawAddress": MsgSetWithdrawAddress,
    "distribution/MsgWithdrawDelegationReward": MsgWithdrawDelegationReward,
    "distribution/MsgWithdrawValidatorCommission": MsgWithdrawValidatorCommission,
    "oracle/MsgExchangeRatePrevote": MsgExchangeRatePrevote,
    "oracle/MsgExchangeRateVote": MsgExchangeRateVote,
    "oracle/MsgDelegateFeedConsent": MsgDelegateFeedConsent,
    "gov/MsgSubmitProposal": MsgSubmitProposal,
    "gov/MsgDeposit": MsgDeposit,
    "gov/MsgVote": MsgVote,
    "market/MsgSwap": MsgSwap,
    "staking/MsgBeginRedelegate": MsgBeginRedelegate,
    "staking/MsgDelegate": MsgDelegate,
    "staking/MsgUndelegate": MsgUndelegate,
    "staking/MsgEditValidator": MsgEditValidator,
    "staking/MsgCreateValidator": MsgCreateValidator,
}
