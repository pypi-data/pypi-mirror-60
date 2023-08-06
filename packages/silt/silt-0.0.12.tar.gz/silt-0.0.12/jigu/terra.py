from typing import Optional, List, Dict, Union

import jigu.client.http

from jigu.api import (
    AuthAPI,
    BankAPI,
    SupplyAPI,
    DistributionAPI,
    StakingAPI,
    SlashingAPI,
    OracleAPI,
    MarketAPI,
    TreasuryAPI,
    GovAPI,
    TendermintAPI,
    TxAPI,
)

from jigu.core import *
from jigu.core.denoms import uLuna
from jigu.error import DenomNotFoundError
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.query import AccountQuery, ValidatorQuery, Wallet, ProposalQuery
from jigu.networks import COLUMBUS


class Terra(object):
    def __init__(
        self,
        node_uri: str = COLUMBUS["node_uri"],
        chain_id: str = COLUMBUS["chain_id"],
        default_gas_prices: Union[List[Coin], Coins] = [Coin(uLuna, "0.015")],
        default_gas_adjustment: str = "1.4",
    ):
        self._node_uri = node_uri
        self._chain_id = chain_id
        self._c = jigu.client.http.HTTPClient(
            api_base=self._node_uri, chain_id=self._chain_id
        )
        self.default_gas_prices = default_gas_prices
        self.default_gas_adjustment = default_gas_adjustment

        # module APIs
        self._auth = AuthAPI(self._c)
        self._bank = BankAPI(self._c)
        self._supply = SupplyAPI(self._c)
        self._distribution = DistributionAPI(self._c)
        self._staking = StakingAPI(self._c)
        self._slashing = SlashingAPI(self._c)
        self._oracle = OracleAPI(self._c)
        self._market = MarketAPI(self._c)
        self._treasury = TreasuryAPI(self._c)
        self._gov = GovAPI(self._c)

        # lower-level APIs
        self._tendermint = TendermintAPI(self._c)
        self._tx = TxAPI(self._c)

        # collection queries
        self._blocks = jigu.query.Blocks(self)

    def __repr__(self):
        return f"Terra({self._node_uri} -> {self.chain_id})"

    @property
    def node_uri(self):
        return self._node_uri

    @property
    def chain_id(self) -> str:
        return self._chain_id

    # Core Module APIs

    @property
    def auth(self):
        return self._auth

    @property
    def bank(self):
        return self._bank

    # The supply module is simple enough to be reduced to this special interface.
    # This function serves as a proxy to get the supply total.
    def supply(self, denom: Optional[str] = None):
        total_supply = self._supply.get_total()
        if denom is None:
            return total_supply
        if denom not in total_supply:
            raise DenomNotFoundError(
                f"denom '{denom}' was not found, avaialble denoms are: {total_supply.denoms}"
            )
        return total_supply[denom]

    @property
    def distribution(self):
        return self._distribution

    @property
    def staking(self):
        return self._staking

    @property
    def slashing(self):
        return self._slashing

    @property
    def oracle(self):
        return self._oracle

    @property
    def market(self):
        return self._market

    @property
    def treasury(self):
        return self._treasury

    @property
    def gov(self):
        return self._gov

    # lower-level APIs

    def is_syncing(self) -> bool:
        """Checks whether the node is currently syncing with the blockchain."""
        return self._tendermint.get_syncing()

    def node_info(self) -> Dict[str, dict]:
        """Get information about the node."""
        return self._tendermint.get_node_info()

    def get_tx_info(self, hash: str) -> TxInfo:
        """Look up a transaction's information from its hash."""
        return self._tx.get_info(hash)

    def broadcast_tx(self, tx: SignedTx, mode: str = "block") -> TxInfo:
        """Broadcasts a signed transaction on the blockchain."""
        return self._tx.broadcast(tx, mode)

    def encode_tx(self, tx: StdTx) -> str:
        return self._tx.encode(tx)

    def estimate_tx_fee(
        self,
        tx: Union[UnsignedTx, SignedTx],
        gas_adjustment: Union[float, str] = None,
        gas_prices: List[Coin] = None,
    ) -> Fee:
        if not gas_prices:
            gas_prices = self.default_gas_prices
        if not gas_adjustment:
            gas_adjustment = self.default_gas_adjustment
        return self._tx.estimate_fee(tx, gas_adjustment, gas_prices)

    # Object query based APIs

    def account(self, arg) -> AccountQuery:
        validate_acc_address(arg)
        return AccountQuery(self, arg)

    def validator(self, arg) -> ValidatorQuery:
        validate_val_address(arg)
        return ValidatorQuery(self, arg)

    def wallet(self, arg) -> Wallet:
        return Wallet(self, arg)

    def proposal(self, id: int) -> ProposalQuery:
        return ProposalQuery(self, id)

    ##

    @property
    def blocks(self):
        return self._blocks
    
    def validatorset(self, height=None):
        all_validators = self.staking.validators()
        vset = self._tendermint.get_validatorset(height=height)
        # join validators using pubkey
        by_pubkey = { x['pub_key']: x for x in vset }
        return [{
            "validator": v,
            "info": by_pubkey[v.consensus_pubkey],
        } for v in all_validators if v.consensus_pubkey in by_pubkey]