from __future__ import annotations

from typing import Dict, List, Optional, Union
from bech32 import bech32_encode, bech32_decode

import jigu.core
from jigu.core import (
    Coin,
    Coins,
    AccAddress,
    ValAddress,
    Denom,
    Delegation,
    UnbondingDelegation,
    Validator,
)

from jigu.util import abbreviate
from jigu.util.validation import validate_acc_address, validate_val_address


class AccountQuery(object):
    def __init__(self, terra, address: str):
        validate_acc_address(address)
        self.terra = terra
        self.address = address

    def __str__(self):
        return self.address

    def __repr__(self):
        return f"Account({abbreviate(self.address)})"

    @property
    def validator(self):
        decoded = bech32_decode(self.address)
        val_address = bech32_encode("terravaloper", decoded[1])
        return self.terra.validator(val_address)

    ## Auth

    def info(self) -> jigu.core.Account:
        return self.terra.auth.acc_info(self.address)

    ## Bank

    def balance(self, denom: Optional[Denom] = None) -> Union[Coin, Coins]:
        balances = self.terra.bank.get_balances(self.address)
        if denom is None:
            return balances
        else:
            return balances[denom]

    ## Distribution

    def rewards(
        self, denom: Optional[Denom] = None, validator: Optional[ValAddress] = None
    ):
        if validator:
            validate_val_address(validator)
        rewards, total = self.terra.distribution.get_acc_rewards(self.address)
        if validator is None and denom is None:
            return rewards
        elif validator and denom is None:
            return rewards[validator]
        elif validator is None and denom:
            return total[denom]
        else:
            return rewards[validator][denom]

    def withdraw_address(self) -> AccAddress:
        return self.terra.distribution.get_withdraw_address(delegator=self.address)

    ## Staking

    def delegations(self, validator: Optional[ValAddress] = None) -> List[Delegation]:
        return self.terra.staking.delegations(
            delegator=self.address, validator=validator
        )

    def unbonding_delegations(
        self, validator: Optional[ValAddress] = None
    ) -> List[UnbondingDelegation]:
        return self.terra.staking.unbonding_delegations(
            delegator=self.address, validator=validator
        )

    def redelegations(self):
        # TODO: implement
        return ""

    def bonded_validators(self) -> List[Validator]:
        return self.terra.staking.get_bonded_validators(delegator=self.address)

    # TODO: add pagination
    def staking_txs(self):
        return self.terra.staking.get_staking_txs(delegator=self.address)
