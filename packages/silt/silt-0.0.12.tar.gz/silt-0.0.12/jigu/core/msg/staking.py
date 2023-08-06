from __future__ import annotations
from typing import List, Dict, Any, Union, Optional
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.core import Coin, Coins, AccAddress, ValAddress, Dec
from jigu.core.denoms import uLuna
from jigu.core.msg import Message


class MsgBeginRedelegate(Message):

    type = "staking/MsgBeginRedelegate"
    action = "begin_redelegate"

    def __init__(
        self,
        delegator_address: AccAddress,
        validator_src_address: ValAddress,
        validator_dst_address: ValAddress,
        amount: Coin,
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_src_address)
        validate_val_address(validator_dst_address)
        self.delegator_address = delegator_address
        self.validator_src_address = validator_src_address
        self.validator_dst_address = validator_dst_address
        self.amount = amount

    def msg_value(self) -> Dict[str, Union[str, Union[int, Dec]]]:
        return {
            "delegator_address": self.delegator_address,
            "validator_src_address": self.validator_src_address,
            "validator_dst_address": self.validator_dst_address,
            "amount": (self.amount).amount,  # self.amount is coin
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgBeginRedelegate:
        amount = Coin(uLuna, data["amount"])
        return cls(
            delegator_address=data["delegator_address"],
            validator_src_address=data["validator_src_address"],
            validator_dst_address=data["validator_dst_address"],
            amount=amount,
        )


class MsgDelegate(Message):

    type = "staking/MsgDelegate"
    action = "delegate"

    def __init__(
        self, delegator_address: AccAddress, validator_address: ValAddress, amount: Coin
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.amount = amount

    def msg_value(self) -> Dict[str, Union[str, Coin]]:
        return {
            "delegator_address": self.delegator_address,
            "validator_address": self.validator_address,
            "amount": self.amount,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgDelegate:
        amount = Coin.from_dict(data["amount"])
        return cls(
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
            amount=amount,
        )


class MsgUndelegate(Message):

    type = "staking/MsgUndelegate"
    action = "undelegate"

    def __init__(self, delegator_address: str, validator_address: str, amount: Coin):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.amount = amount

    def msg_value(self) -> Dict[str, Union[str, Coin]]:
        return {
            "delegator_address": self.delegator_address,
            "validator_address": self.validator_address,
            "amount": self.amount,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgUndelegate:
        amount = Coin(uLuna, data["amount"])
        return cls(
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
            amount=amount,
        )


class MsgEditValidator(Message):

    type = "staking/MsgEditValidator"
    action = "edit_validator"

    def __init__(
        self,
        Description: Dict[str, str],
        address: ValAddress,
        commission_rate: Optional[Dec] = None,
        min_self_delegation: Optional[int] = None,
    ):
        validate_val_address(address)
        self.Description = Description
        self.address = address
        self.commission_rate = commission_rate
        self.min_self_delegation = min_self_delegation

    def msg_value(self) -> Dict[str, Union[str, Coin]]:
        return {
            "Description": self.Description,
            "address": self.address,
            "commission_rate": self.amount,
            "min_self_delegation": self.min_self_delegation,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgEditValidator:
        msd = int(data["min_self_delegation"]) if data["min_self_delegation"] else None
        cr = Dec(data["commission_rate"]) if data["commission_rate"] else None
        return cls(
            Description=data["Description"],
            address=data["address"],
            commission_rate=cr,
            min_self_delegation=msd,
        )


class MsgCreateValidator(Message):

    type = "staking/MsgCreateValidator"
    action = "create_validator"

    def __init__(
        self,
        description: Dict[str, str],
        commission: dict,
        min_self_delegation: int,
        delegator_address: AccAddress,
        validator_address: ValAddress,
        pubkey: dict,
        value: Coin,
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.description = description
        self.commission = commission
        self.min_self_delegation = min_self_delegation
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.pubkey = pubkey
        self.value = value

    def msg_value(self) -> Dict[str, Union[str, Coin]]:
        return {
            "description": self.description,
            "commission": self.address,
            "min_self_delegation": self.amount,
            "delegator_address": self.min_self_delegation,
            "validator_address": self.validator_address,
            "pubkey": self.pubkey,
            "value": self.value,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, str]) -> MsgEditValidator:
        return cls(
            description=data["description"],
            commission=data["commission"],
            min_self_delegation=int(data["min_self_delegation"]),
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
            pubkey=data["pubkey"],
            value=Coin.from_dict(data["value"]),
        )
