from typing import Union

from jigu.api import BaseAPI
from jigu.util.validation import validate_acc_address

from jigu.core import AccAddress, Account, LazyGradedVestingAccount


class AuthAPI(BaseAPI):
    def acc_info(self, address: AccAddress) -> Union[Account, LazyGradedVestingAccount]:
        info = self._api_get(f"/auth/accounts/{address}")
        if info["type"] == "core/Account":
            return Account.from_dict(info["value"])
        elif info["type"] == "core/LazyGradedVestingAccount":
            return LazyGradedVestingAccount.from_dict(info["value"])
        else:
            raise ValueError("could not deserialize account in auth.acc_info")
