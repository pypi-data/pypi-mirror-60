from typing import Dict, Any, Union, Optional

from jigu.api import BaseAPI
from jigu.core import Coin, Dec, Denom

import warnings


class MarketAPI(BaseAPI):
    def swap_rate(self, offer_coin: Coin, ask_denom: Denom) -> Coin:
        if type(offer_coin.amount) != int:
            warnings.warn(
                f"Coin's amount will be truncated to integer: {int(offer_coin.amount)} {offer_coin.denom}",
                SyntaxWarning,
            )
        params = {
            "offer_coin": f"{int(offer_coin.amount)}{offer_coin.denom}",
            "ask_denom": ask_denom,
        }
        bid = self._api_get(f"/market/swap", params=params)
        return Coin.from_dict(bid)

    def terra_pool_delta(self) -> Dec:
        terra_pool_delta = self._api_get("/market/terra_pool_delta")
        return Dec(terra_pool_delta)

    def params(self, key: Optional[str] = None) -> Union[dict, Any]:
        p = self._api_get("/market/parameters")
        p["pool_recovery_period"] = int(p["pool_recovery_period"])
        p["base_pool"] = Dec(p["base_pool"])
        p["min_spread"] = Dec(p["min_spread"])
        p["tobin_tax"] = Dec(p["tobin_tax"])
        ill = p["illiquid_tobin_tax_list"]
        p["illiquid_tobin_tax_list"] = dict()
        for item in ill:
            p["illiquid_tobin_tax_list"][item["denom"]] = Dec(item["tax_rate"])
        if key is None:
            return p
        else:
            return p[key]
