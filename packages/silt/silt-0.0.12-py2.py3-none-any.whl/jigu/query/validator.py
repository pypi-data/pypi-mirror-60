from __future__ import annotations
from typing import Optional, List, Dict, Union

from bech32 import bech32_decode, bech32_encode
from jigu.util import abbreviate
import jigu.query
import jigu.terra
from jigu.core import *


class ValidatorQuery(object):
    def __init__(self, terra: jigu.terra.Terra, val_address: ValAddress):
        self.terra = terra
        self.val_address = val_address

    def __str__(self):
        return self.val_address

    def __repr__(self):
        return f"Validator({abbreviate(self.val_address)})"

    # Staking
    def info(self) -> Validator:
        return self.terra.staking.val_info(self.val_address)

    @property
    def account(self):
        decoded = bech32_decode(self.val_address)
        acc_address = bech32_encode("terra", decoded[1])
        return self.terra.account(acc_address)

    def delegations(self, delegator: Optional[AccAddress] = None) -> List[Delegation]:
        return self.terra.staking.delegations(validator=self.val_address, delegator=delegator)

    def unbonding_delegations(
        self, delegator: Optional[AccAddress] = None
    ) -> List[UnbondingDelegation]:
        return self.terra.staking.unbonding_delegations(
            validator=self.val_address, delegator=delegator
        )

    @property
    def redelegations(self):
        # TODO: implement
        return ""

    # Distribution
    def rewards(
        self, denom: Optional[Denom] = None, include_delegators: Optional[bool] = False
    ) -> Union[Coin, Coins]:
        if include_delegators:
            rewards = self.terra.distribution.get_val_fee_rewards(self.val_address)
        else:
            rewards = self.terra.distribution.get_val_rewards(self.val_address)
        if denom is None:
            return rewards
        else:
            return rewards[denom]

    def reward_info(self, key: Optional[str] = None):
        return self.terra.distribution.get_val_reward_info(self.val_address, key)

    # Oracle
    def feeder(self) -> jigu.query.AccountQuery:
        return self.terra.account(
            self.terra.oracle.get_feeder_address(validator=self.val_address)
        )

    def misses(self) -> int:
        return self.terra.oracle.get_misses(validator=self.val_address)

    def votes(self, denom: Optional[Denom] = None) -> List[ExchangeRateVote]:
        return self.terra.oracle.votes(validator=self.val_address, denom=denom)

    def prevotes(self, denom: Optional[Denom] = None) -> List[ExchangeRatePrevote]:
        return self.terra.oracle.prevotes(validator=self.val_address, denom=denom)
