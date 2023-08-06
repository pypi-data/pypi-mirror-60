from __future__ import annotations
from typing import Dict, Optional, Union
import warnings

from jigu.core import Coin, Coins, Dec
from jigu.error import AccountNotFoundWarning
from jigu.util import JSONSerializable, JSONDeserializable, pretty_repr
from jigu.util.validation import validate_acc_address


class Account(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        address: str,
        coins: Coins,
        public_key: Optional[str],
        account_number: Union[str, int],
        sequence: Union[str, int],
    ):
        if address:
            validate_acc_address(address)
        else:
            warnings.warn(
                "Account was not found; perhaps wrong chain or send some funds first.",
                AccountNotFoundWarning,
            )
        self.address = address
        self.coins = coins
        self.public_key = public_key
        self.account_number = int(account_number)
        self.sequence = int(sequence)

    def __repr__(self) -> str:
        return pretty_repr(
            "Account Info",
            ("Address:", self.address),
            ("Balance:", self.coins),
            ("Public Key:", self.public_key),
            ("Account Number:", self.account_number),
            ("Sequence:", self.sequence),
        )

    def to_dict(self) -> dict:
        return {
            "type": "core/Account",
            "value": {
                "address": self.address,
                "coins": self.coins,
                "public_key": self.public_key,
                "account_number": str(self.account_number),
                "sequence": str(self.sequence),
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> Account:
        return cls(
            address=data["address"],
            coins=Coins.from_dict(data["coins"]),
            public_key=data["public_key"],
            account_number=data["account_number"],
            sequence=data["sequence"],
        )


class VestingSchedule(JSONSerializable, JSONDeserializable):
    def __init__(self, start_time: str, end_time: str, ratio: Dec):
        self.start_time = int(start_time)
        self.end_time = int(end_time)
        self.ratio = ratio

    def to_dict(self):
        return {
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "ratio": self.ratio,
        }

    def __repr__(self) -> str:
        return pretty_repr(
            "VestingSchedule",
            ("Start Time:", self.start_time),
            ("End Time:", self.end_time),
            ("Ratio", self.ratio),
        )

    @classmethod
    def from_dict(cls, data: dict) -> VestingSchedule:
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
            ratio=Dec(data["ratio"]),
        )


class LazyGradedVestingAccount(Account):
    def __init__(
        self,
        base_account: Account,
        original_vesting: Coins,
        delegated_free: Coins,
        delegated_vesting: Coins,
        end_time: int,
        vesting_schedules: dict,
    ):
        Account.__init__(
            self,
            address=base_account.address,
            coins=base_account.coins,
            public_key=base_account.public_key,
            account_number=base_account.account_number,
            sequence=base_account.sequence,
        )
        self.original_vesting = original_vesting
        self.delegated_free = delegated_free
        self.delegated_vesting = delegated_vesting
        self.end_time = end_time
        self.vesting_schedules = vesting_schedules

    def to_dict(self):
        return {
            "type": "core/LazyGradedVestingAccount",
            "value": {
                "BaseVestingAccount": {
                    "BaseAccount": Account.to_dict(self),
                    "original_vesting": self.original_vesting,
                    "delegated_free": self.delegated_free,
                    "delegated_vesting": self.delegated_vesting,
                    "end_time": self.end_time,
                },
                "vesting_schedules": self.vesting_schedules,
            },
        }

    def __repr__(self) -> str:
        return (
            pretty_repr(
                "LazyGradedVestingAccount",
                ("Address:", self.address),
                ("Balance:", self.coins),
                ("Public Key:", self.public_key),
                ("Account Number:", self.account_number),
                ("Sequence:", self.sequence),
                ("Original Vesting:", self.original_vesting),
                ("Delegated Free:", self.delegated_free),
                ("Delegated Vesting:", self.delegated_vesting),
                ("End Time:", self.end_time),
            )
            + "\n\nVesting Schedules:\n"
            + repr(self.vesting_schedules)
        )

    @classmethod
    def from_dict(cls, data: dict) -> LazyGradedVestingAccount:
        bva = data[
            "BaseVestingAccount"
        ]  # value = { bva { ... } vesting_schedules { } }
        original_vesting = Coins.from_dict(bva["original_vesting"])
        delegated_free = Coins.from_dict(bva["delegated_free"])
        delegated_vesting = Coins.from_dict(bva["delegated_vesting"])
        vesting_schedules = dict()
        for s in data["vesting_schedules"]:
            vesting_schedules[s["denom"]] = []
            for schedule in s["schedules"]:
                vesting_schedules[s["denom"]].append(
                    VestingSchedule.from_dict(schedule)
                )
        return cls(
            base_account=Account.from_dict(bva["BaseAccount"]),
            original_vesting=original_vesting,
            delegated_free=delegated_free,
            delegated_vesting=delegated_vesting,
            end_time=int(bva["end_time"]),
            vesting_schedules=vesting_schedules,
        )
