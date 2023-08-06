from __future__ import annotations

from typing import Dict, Union, List, Any
from jigu.core import Coin, Dec, Timestamp, AccAddress, ValAddress
from jigu.core.denoms import uLuna
from jigu.util import JSONSerializable, JSONDeserializable, abbreviate, pretty_repr

from jigu.util.validation import validate_acc_address, validate_val_address


class Delegation(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        delegator_address: AccAddress,
        validator_address: ValAddress,
        shares: Coin,
        balance: Coin,
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.shares = shares
        self.balance = balance

    def __repr__(self) -> str:
        return pretty_repr(
            "Delegation",
            ("Delegator:", self.delegator_address),
            ("Validator:", self.validator_address),
            ("Shares:", self.shares),
            ("Balance:", self.balance),
        )

    def to_dict(self) -> dict:
        return {
            "delegator_address": self.delegator_address,
            "validator_address": self.validator_address,
            "shares": str(self.shares.amount),
            "balance": str(self.balance.amount),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Delegation:
        return cls(
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
            shares=Coin(uLuna, data["shares"]),
            balance=Coin(uLuna, data["balance"]),
        )


class UnbondingEntry(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        initial_balance: Coin,
        balance: Coin,
        creation_height: int,
        completion_time: Timestamp,
    ):
        self.initial_balance = initial_balance
        self.balance = balance
        self.creation_height = creation_height
        self.completion_time = completion_time

    def __repr__(self) -> str:
        return pretty_repr(
            "UnbondingEntry",
            ("Initial Balance:", self.initial_balance),
            ("Balance:", self.balance),
            ("Creation Height:", self.creation_height),
            ("Completion Time:", self.completion_time),
        )

    def to_dict(self) -> dict:
        return {
            "initial_balance": str(self.initial_balance.amount),
            "balance": str(self.balance.amount),
            "creation_height": self.creation_height,
            "completion_time": self.completion_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> UnbondingEntry:
        return cls(
            initial_balance=Coin(uLuna, data["initial_balance"]),
            balance=Coin(uLuna, data["balance"]),
            creation_height=int(data["creation_height"]),
            completion_time=Timestamp.from_dict(data["completion_time"]),
        )


class UnbondingDelegation(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        delegator_address: AccAddress,
        validator_address: ValAddress,
        entries: List[UnbondingEntry],
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_address)
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.entries = entries

    def __repr__(self) -> str:
        return pretty_repr(
            "UnbondingEntry",
            ("Delegator:", self.delegator_address),
            ("Validator:", self.validator_address),
            ("Num Entries:", len(self.entries)),
        )

    def to_dict(self) -> dict:
        return {
            "delegator_address": self.delegator_address,
            "validator_address": self.validator_address,
            "entries": self.entries,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UnbondingDelegation:
        entries = [UnbondingEntry.from_dict(entry) for entry in data["entries"]]
        return cls(
            delegator_address=data["delegator_address"],
            validator_address=data["validator_address"],
            entries=entries,
        )


class RedelegationEntry(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        initial_balance: Coin,
        balance: Coin,
        shares_dst: Coin,
        creation_height: int,
        completion_time: Timestamp,
    ):
        self.initial_balance = initial_balance
        self.balance = balance
        self.shares_dst = shares_dst
        self.creation_height = creation_height
        self.completion_time = completion_time

    def __repr__(self) -> str:
        return pretty_repr(
            "RedelegationEntry",
            ("Initial Balance:", self.initial_balance),
            ("Balance:", self.balance),
            ("Shares Dst:", self.shares_dst),
            ("Creation Height:", self.creation_height),
            ("Completion Time:", self.completion_time),
        )

    def to_dict(self) -> dict:
        return {
            "creation_height": self.creation_height,
            "completion_time": self.completion_time,
            "initial_balance": str(self.initial_balance.amount),
            "balance": str(self.balance.amount),
            "shares_dst": str(self.shares.amount),
        }

    @classmethod
    def from_dict(cls, data: dict) -> RedelegationEntry:
        return cls(
            initial_balance=Coin(uLuna, data["initial_balance"]),
            balance=Coin(uLuna, data["balance"]),
            shares_dst=Coin(uLuna, data["initial_balance"]),
            creation_height=int(data["creation_height"]),
            completion_time=Timestamp.from_dict(data["completion_time"]),
        )


class Redelegation(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        delegator_address: AccAddress,
        validator_src_address: ValAddress,
        validator_dst_address: ValAddress,
        entries: List[RedelegationEntry],
    ):
        validate_acc_address(delegator_address)
        validate_val_address(validator_src_address)
        validate_val_address(validator_dst_address)
        self.delegator_address = delegator_address
        self.validator_src_address = validator_src_address
        self.validator_dst_address = validator_dst_address
        self.entries = entries

    def __repr__(self) -> str:
        return pretty_repr(
            "Redelegation",
            ("Delegator:", self.delegator_address),
            ("From Validator:", self.validator_src_address),
            ("To Validator:", self.validator_dst_address),
            ("Num Entries:", len(self.entries)),
        )

    def to_dict(self) -> dict:
        return {
            "delegator_address": self.delegator_address,
            "validator_src_address": self.validator_src_address,
            "validator_dst_address": self.validator_dst_address,
            "entries": self.entries,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UnbondingDelegation:
        entries = [RedelegationEntry.from_dict(re) for re in data["entries"]]
        return cls(
            delegator_address=data["delegator_address"],
            validator_src_address=data["validator_src_address"],
            validator_dst_address=data["validator_dst_address"],
            entries=entries,
        )


class Commission(JSONSerializable, JSONDeserializable):
    def __init__(self, commission_rates: Dict[str, Dec], update_time: Timestamp):
        self.rate = commission_rates["rate"]
        self.max_rate = commission_rates["max_rate"]
        self.max_change_rate = commission_rates["max_change_rate"]
        self.update_time = update_time

    def __repr__(self) -> str:
        return pretty_repr(
            "Commission",
            ("Commission Rate:", str(self.rate)),
            ("          (max):", str(self.max_rate)),
            ("   (max-change):", str(self.max_change_rate)),
            ("Update Time:", self.update_time),
        )

    def to_dict(self):
        return {
            "commission_rates": {
                "rate": self.rate,
                "max_rate": self.max_rate,
                "max_change_rate": self.max_change_rate,
            },
            "update_time": self.update_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Commission:
        commission_rates = {
            key: Dec(data["commission_rates"][key]) for key in data["commission_rates"]
        }
        return cls(
            commission_rates=commission_rates,
            update_time=Timestamp.from_dict(data["update_time"]),
        )


class Validator(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        operator_address: ValAddress,
        consensus_pubkey: str,
        jailed: bool,
        status: int,
        tokens: Coin,
        delegator_shares: Coin,
        description: Dict[str, str],
        unbonding_height: int,
        unbonding_time: Timestamp,
        commission: Commission,
        min_self_delegation: int,
    ):
        validate_val_address(operator_address)
        self.operator_address = operator_address
        self.consensus_pubkey = consensus_pubkey
        self.jailed = jailed
        self.status = status
        self.tokens = tokens
        self.moniker = description["moniker"]
        self.website = description["website"]
        self.identity = description["identity"]
        self.details = description["details"]
        self.delegator_shares = delegator_shares
        self.unbonding_height = unbonding_height
        self.unbonding_time = unbonding_time
        self.commission = commission
        self.min_self_delegation = min_self_delegation

    def __repr__(self) -> str:
        return (
            pretty_repr(
                "Validator Info",
                ("Moniker:", self.moniker),
                ("Website", self.website),
                ("Operator:", self.operator_address),
                ("Consensus Pubkey:", self.consensus_pubkey),
                ("Jailed?", self.jailed),
                ("Identity:", self.identity),
                ("Details:", self.details),
                ("Delegator Shares:", self.delegator_shares),
                ("Unbonding Height:", self.unbonding_height),
                ("Unbonding Time:", self.unbonding_time),
                ("Min. Self-delegation:", self.min_self_delegation),
            )
            + "\n"
            + repr(self.commission)
        )

    def to_dict(self) -> dict:
        return {
            "operator_address": self.operator_address,
            "consensus_pubkey": self.consensus_pubkey,
            "jailed": self.jailed,
            "status": self.status,
            "tokens": str(self.tokens.amount),
            "delegator_shares": str(self.delegator_shares.amount),
            "description": {
                "moniker": self.moniker,
                "website": self.website,
                "identity": self.identity,
                "details": self.details,
            },
            "unbonding_height": self.unbonding_height,
            "unbonding_time": self.unbonding_time,
            "commission": self.commission,
            "min_self_delegation": self.min_self_delegation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Validator:
        return cls(
            operator_address=data["operator_address"],
            consensus_pubkey=data["consensus_pubkey"],
            jailed=data["jailed"],
            status=data["status"],
            tokens=Coin(uLuna, data["tokens"]),
            delegator_shares=Coin(uLuna, data["delegator_shares"]),
            description=data["description"],
            unbonding_height=int(data["unbonding_height"]),
            unbonding_time=Timestamp.from_dict(data["unbonding_time"]),
            commission=Commission.from_dict(data["commission"]),
            min_self_delegation=int(data["min_self_delegation"]),
        )

