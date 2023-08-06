from typing import Dict, List, Optional, Union, Any, Callable
from collections import defaultdict

from jigu.core import (
    Coin,
    Coins,
    Dec,
    ValAddress,
    AccAddress,
    Denom,
    ExchangeRateVote,
    ExchangeRatePrevote,
)
from jigu.error import ValidationError

from jigu.util.validation import validate_val_address
from jigu.api import BaseAPI


class OracleAPI(BaseAPI):

    # for some reason, votes and prevotes for a certain (val, denom) pair will give STILL give you a list
    def votes(
        self, validator: Optional[ValAddress] = None, denom: Optional[Denom] = None
    ):
        if validator is not None and denom is not None:
            validate_val_address(validator)
            votes = self._api_get(f"/oracle/denoms/{denom}/votes/{validator}")
        elif validator:
            validate_val_address(validator)
            votes = self._api_get(f"/oracle/voters/{validator}/votes")
        elif denom:
            votes = self._api_get(f"/oracle/denoms/{denom}/votes")
        else:
            raise ValidationError("arguments validator and denom cannot both be None")
        return [ExchangeRateVote.from_dict(vote) for vote in votes]

    def prevotes(
        self, validator: Optional[ValAddress] = None, denom: Optional[Denom] = None
    ):
        if validator is not None and denom is not None:
            validate_val_address(validator)
            prevotes = self._api_get(f"/oracle/denoms/{denom}/prevotes/{validator}")
        elif validator:
            validate_val_address(validator)
            prevotes = self._api_get(f"/oracle/voters/{validator}/prevotes")
        elif denom:
            prevotes = self._api_get(f"/oracle/denoms/{denom}/prevotes")
        else:
            raise ValidationError("arguments validator and denom cannot both be None")
        return [ExchangeRatePrevote.from_dict(prevote) for prevote in prevotes]

    def exchange_rates(self, denom: Optional[ValAddress] = None) -> Union[Coin, Coins]:
        res = self._api_get("/oracle/denoms/exchange_rates")
        rates = Coins.from_dict(res)
        if denom is None:
            return rates
        else:
            return rates[denom]

    def active_denoms(self) -> List[Denom]:
        return self._api_get("/oracle/denoms/actives")

    def get_feeder_address(self, validator: ValAddress) -> AccAddress:
        validate_val_address(validator)
        return self._api_get(f"/oracle/voters/{validator}/feeder")

    def get_misses(self, validator: ValAddress) -> int:
        validate_val_address(validator)
        misses = self._api_get(f"/oracle/voters/{validator}/miss")
        return int(misses)

    def params(self, key: Optional[str] = None) -> Union[dict, int, Dec, List[Denom]]:
        p = self._api_get("/oracle/parameters")
        p["vote_period"] = int(p["vote_period"])
        p["vote_threshold"] = Dec(p["vote_threshold"])
        p["reward_band"] = Dec(p["reward_band"])
        p["reward_distribution_window"] = int(p["reward_distribution_window"])
        p["slash_fraction"] = Dec(p["slash_fraction"])
        p["slash_window"] = int(p["slash_window"])
        p["min_valid_per_window"] = Dec(p["min_valid_per_window"])
        if key is None:
            return p
        else:
            return p[key]
