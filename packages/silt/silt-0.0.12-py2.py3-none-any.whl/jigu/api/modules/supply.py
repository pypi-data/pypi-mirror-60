from typing import List, Dict

from jigu.core import Coin, Coins
from jigu.api import BaseAPI


class SupplyAPI(BaseAPI):
    def get_total(self) -> Coins:
        total_supply = self._api_get("/supply/total")
        return Coins.from_dict(total_supply)
