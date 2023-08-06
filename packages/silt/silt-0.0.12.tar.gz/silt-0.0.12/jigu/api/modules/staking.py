from typing import List, Dict, Optional, Any, Union
from jigu.api import BaseAPI

from jigu.core import (
    Coin,
    Coins,
    Validator,
    Delegation,
    UnbondingDelegation,
    Redelegation,
    AccAddress,
    ValAddress,
)
from jigu.core.denoms import uLuna
from jigu.util.validation import (
    validate_acc_address,
    validate_val_address,
    ValidationError,
)


class StakingAPI(BaseAPI):
    def delegations(
        self,
        delegator: Optional[AccAddress] = None,
        validator: Optional[ValAddress] = None,
    ) -> Union[Delegation, List[Delegation]]:
        if delegator is not None and validator is not None:
            validate_acc_address(delegator)
            validate_val_address(validator)
            return Delegation.from_dict(
                self._api_get(
                    f"/staking/delegators/{delegator}/delegations/{validator}"
                )
            )
        elif delegator:
            validate_acc_address(delegator)
            delgns = self._api_get(f"/staking/delegators/{delegator}/delegations")
        elif validator:
            validate_val_address(validator)
            delgns = self._api_get(f"/staking/validators/{validator}/delegations")
        else:
            raise ValidationError(
                "arguments delegator and validator cannot both be None"
            )
        return [Delegation.from_dict(delgn) for delgn in delgns]

    def unbonding_delegations(
        self,
        delegator: Optional[AccAddress] = None,
        validator: Optional[ValAddress] = None,
    ) -> Union[UnbondingDelegation, List[UnbondingDelegation]]:
        if delegator is not None and validator is not None:
            validate_acc_address(delegator)
            validate_val_address(validator)
            return UnbondingDelegation.from_dict(
                self._api_get(
                    f"/staking/delegators/{delegator}/delegations/{validator}"
                )
            )
        elif delegator:
            validate_acc_address(delegator)
            delgns = self._api_get(
                f"/staking/delegators/{delegator}/unbonding_delegations"
            )
        elif validator:
            validate_val_address(validator)
            delgns = self._api_get(
                f"/staking/validators/{validator}/unbonding_delegations"
            )
        else:
            raise ValidationError(
                "arguments delegator and validator cannot both be None"
            )
        return [UnbondingDelegation.from_dict(delgn) for delgn in delgns]

    def redelegations(
        self,
        delegator: Optional[AccAddress] = None,
        validator_from: Optional[ValAddress] = None,
        validator_to: Optional[ValAddress] = None,
    ):
        params = {}
        if delegator:
            validate_acc_address(delegator)
            params["delegator"] = delegator
        if validator_from:
            validate_val_address(validator_from)
            params["validator_from"] = validator_from
        if validator_to:
            validate_val_address(validator_to)
            params["validator_to"] = validator_to
        res = self._api_get(f"/staking/redelegations", params=params)
        return [Redelegation.from_dict(rd) for rd in res]

    def get_bonded_validators(
        self, delegator: AccAddress
    ) -> Dict[ValAddress, Validator]:
        validate_acc_address(delegator)
        vs = self._api_get(f"/staking/delegators/{delegator}/validators")
        return {v["operator_address"]: Validator.from_dict(v) for v in vs}

    def get_staking_txs(self, delegator: AccAddress):
        validate_acc_address(delegator)
        return self._api_get(f"/staking/delegators/{delegator}/txs")
    
    def validators(self, status: Optional[str] = None) -> List[Validator]:
        params = dict()
        if status is not None:
            params['status'] = status
        vs = self._api_get("/staking/validators", params=params)
        return [Validator.from_dict(v) for v in vs]

    def val_info(self, validator: ValAddress) -> Validator:
        validate_val_address(validator)
        v = self._api_get(f"/staking/validators/{validator}")
        return Validator.from_dict(v)

    def pool(self, category: Optional[str] = None) -> Union[Coin, Dict[str, Coin]]:
        stk_pool = self._api_get("/staking/pool")
        res = {
            "bonded": Coin(uLuna, stk_pool["bonded_tokens"]),
            "not_bonded": Coin(uLuna, stk_pool["not_bonded_tokens"]),
        }
        if category is None:
            return res
        else:
            return res[category]

    def params(self, key: Optional[str] = None) -> Union[dict, Any]:
        p = self._api_get("/staking/parameters")
        p["unbonding_time"] = int(p["unbonding_time"])
        if key is None:
            return p
        else:
            return p[key]
