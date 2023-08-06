from typing import List, Dict, Optional, Union

from jigu.api import BaseAPI
from jigu.error import ValidationError
from jigu.core import Coin, Coins, Dec, AccAddress, ValAddress, Denom

from jigu.util.validation import validate_acc_address, validate_val_address
from pprint import pprint


class DistributionAPI(BaseAPI):
    def get_acc_rewards(self, delegator: AccAddress):
        validate_acc_address(delegator)
        data = self._api_get(f"/distribution/delegators/{delegator}/rewards")
        rewards = data["rewards"]
        totals = Coins.from_dict(data["total"])
        return (
            {r["validator_address"]: Coins.from_dict(r["reward"]) for r in rewards},
            totals,
        )

    def get_reward(self, delegator: AccAddress, validator: ValAddress):
        validate_acc_address(delegator)
        validate_val_address(validator)
        return self._api_get(
            f"/distribution/delegators/{delegator}/rewards/{validator}"
        )

    def get_withdraw_address(self, delegator: AccAddress) -> AccAddress:
        validate_acc_address(delegator)
        return self._api_get(f"/distribution/delegators/{delegator}/withdraw_address")

    def get_val_reward_info(self, validator: ValAddress, key: Optional[str] = None):
        validate_val_address(validator)
        res = self._api_get(f"/distribution/validators/{validator}")
        rewards = {
            "self_bond": Coins.from_dict(res["self_bond_rewards"]),
            "commission": Coins.from_dict(res["val_commission"]),
        }
        if key is None:
            return rewards
        else:
            return rewards[key]

    def get_val_fee_rewards(self, validator: ValAddress) -> Coins:
        validate_val_address(validator)
        rewards = self._api_get(
            f"/distribution/validators/{validator}/outstanding_rewards"
        )
        return Coins.from_dict(rewards)

    def get_val_rewards(self, validator: ValAddress) -> Coins:
        validate_val_address(validator)
        rewards = self._api_get(f"/distribution/validators/{validator}/rewards")
        return Coins.from_dict(rewards)

    def community_pool(self, denom: Optional[Denom] = None) -> Union[Coin, Coins]:
        res = self._api_get("/distribution/community_pool")
        cp = Coins.from_dict(res)
        if denom is None:
            return cp
        else:
            return cp[denom]

    def params(self, key: Optional[str] = None) -> Union[dict, Dec, bool]:
        p = self._api_get("/distribution/parameters")
        p["community_tax"] = Dec(p["community_tax"])
        p["base_proposer_reward"] = Dec(p["base_proposer_reward"])
        p["bonus_proposer_reward"] = Dec(p["bonus_proposer_reward"])
        if key is None:
            return p
        else:
            return p[key]
