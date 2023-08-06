from typing import List, Dict

from jigu.api import BaseAPI
from jigu.util.validation import validate_acc_address

from jigu.core import Coin, Coins, AccAddress
from jigu.error import TerraAPIError, ValidationError


class BankAPI(BaseAPI):
    def get_balances(self, address: AccAddress) -> Coins:
        validate_acc_address(address)
        balances = self._api_get(f"/bank/balances/{address}")
        return Coins.from_dict(balances)
