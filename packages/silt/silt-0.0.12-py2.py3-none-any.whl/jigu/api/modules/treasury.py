from typing import List, Dict, Any, Optional, Union

from jigu.api import BaseAPI
from jigu.core import Coin, Coins, Dec, PolicyConstraints, Denom

from jigu.core.denoms import uLuna


class TreasuryAPI(BaseAPI):
    def tax_cap(self, denom: Denom) -> Coin:
        cap = self._api_get(f"/treasury/tax_cap/{denom}")
        return Coin(denom, cap)

    def tax_rate(self) -> Dec:
        tax_rate = self._api_get("/treasury/tax_rate")
        return Dec(tax_rate)

    def reward_weight(self) -> Dec:
        reward_weight = self._api_get("/treasury/reward_weight")
        return Dec(reward_weight)

    def tax_proceeds(self, denom: Optional[Denom] = None) -> Coins:
        res = self._api_get("/treasury/tax_proceeds")
        tax_proceeds = Coins.from_dict(res)
        if denom is None:
            return tax_proceeds
        else:
            return tax_proceeds[denom]

    def seigniorage_proceeds(self) -> Coin:
        sp = self._api_get("/treasury/seigniorage_proceeds")
        return Coin(uLuna, int(sp))

    def params(self, key: Optional[str] = None) -> Union[dict, int, Dec]:
        p = self._api_get("/treasury/parameters")
        p["seigniorage_burden_target"] = Dec(p["seigniorage_burden_target"])
        p["mining_increment"] = Dec(p["mining_increment"])
        p["window_short"] = int(p["window_short"])
        p["window_long"] = int(p["window_long"])
        p["window_probation"] = int(p["window_probation"])
        p["tax_policy"] = PolicyConstraints.from_dict(p["tax_policy"])
        p["reward_policy"] = PolicyConstraints.from_dict(p["reward_policy"])
        if key is None:
            return p
        else:
            return p[key]
