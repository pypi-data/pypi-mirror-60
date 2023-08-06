from __future__ import annotations
from typing import List, Dict, Any, Union
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.core import Coin, Coins, AccAddress

from jigu.core.msg import Message


class MsgSetWithdrawAddress(Message):

    type = "distribution/MsgSetWithdrawAddress"
    action = "set_withdraw_address"

    def __init__(self, delegator_address: AccAddress, withdraw_address: AccAddress):
        validate_acc_address(delegator_address)
        validate_acc_address(withdraw_address)
        self.delegator_address = delegator_address
        self.withdraw_address = withdraw_address

    def msg_value(self) -> Dict[str, AccAddress]:
        return {
            "delegator_address": self.delegator_address,
            "withdraw_address": self.withdraw_address,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, AccAddress]) -> MsgSetWithdrawAddress:
        return cls(
            delegator_address=data["delegator_address"],
            withdraw_address=data["withdraw_address"],
        )


class MsgWithdrawDelegationReward(Message):

    type = "distribution/MsgWithdrawDelegationReward"
    action = "withdraw_delegation_reward"

    def __init__(self, delegator_address: AccAddress, validator_address: ValAddress):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.delegator_address = delegator_address
        self.validator_address = validator_address

    def msg_value(self) -> Dict[str, Union[AccAddress, ValAddress]]:
        return {
            "delegator_address": self.delegator_address,
            "validator_address": self.validator_address,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, AccAddress]) -> MsgWithdrawDelegationReward:
        return cls(
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
        )


class MsgWithdrawValidatorCommission(Message):

    type = "distribution/MsgWithdrawValidatorCommission"
    action = "withdraw_validator_commission"

    def __init__(self, validator_address: ValAddress):
        validate_val_address(validator_address)
        self.validator_address = validator_address

    def msg_value(self) -> Dict[str, Union[AccAddress, ValAddress]]:
        return {"validator_address": self.validator_address}

    @classmethod
    def from_msg_dict(
        cls, data: Dict[str, AccAddress]
    ) -> MsgWithdrawValidatorCommission:
        return cls(validator_address=data["validator_address"])

