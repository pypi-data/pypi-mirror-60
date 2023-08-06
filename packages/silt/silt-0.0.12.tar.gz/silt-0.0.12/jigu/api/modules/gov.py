from typing import Dict, Any, Optional, List

from jigu.core import Proposal, AccAddress, Coin
from jigu.core.denoms import uLuna
from jigu.util.validation import validate_acc_address
from jigu.api import BaseAPI


class GovAPI(BaseAPI):
    """Interface for interacting with the Governance API."""

    def proposals(self, id: Optional[str] = None):
        """Gets a list of governance proposals."""

        if id is not None:
            return Proposal.from_dict(self._api_get(f"/gov/proposals/{id}"))  # singular
        else:
            ps = self._api_get(f"/gov/proposals")
            return [Proposal.from_dict(p) for p in ps]

    def get_proposal_proposer(self, id: str) -> AccAddress:
        """Gets the proposal's proposer"""

        res = self._api_get(f"/gov/proposals/{id}/proposer")
        return res["proposer"]

    def get_proposal_deposits(self, id: str):
        """Get the proposal's deposits."""

        return self._api_get(f"/gov/proposals/{id}/deposits")

    def get_proposal_deposit(self, id: str, depositor: AccAddress):
        return self._api_get(f"/gov/proposals/{id}/deposits/{depositor}")

    def get_proposal_votes(self, id: str):
        return self._api_get(f"/gov/proposals/{id}/votes")

    def get_proposal_vote(self, id: str, voter: str):
        return self._api_get(f"/gov/proposals/{id}/votes/{voter}")

    def get_proposal_tally(self, id: str) -> Dict[str, Coin]:
        res = self._api_get(f"/gov/proposals/{id}/tally")
        tally = dict()
        for key in res:
            tally[key] = Coin(uLuna, int(res[key]))
        return tally

    @property
    def deposit_params(self):
        return self._api_get(f"/gov/parameters/deposit")

    @property
    def vote_params(self):
        return self._api_get(f"/gov/parameters/voting")

    @property
    def tally_params(self):
        return self._api_get(f"/gov/parameters/tallying")
