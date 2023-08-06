from __future__ import annotations
from typing import Optional, List, Dict, Union

from jigu.util import abbreviate
import jigu.query
import jigu.terra
from jigu.core import *


class ProposalQuery(object):
    def __init__(self, terra: jigu.terra.Terra, proposal_id: int):
        self.terra = terra
        self.proposal_id = proposal_id

    def __repr__(self):
        return f"Proposal(id={self.proposal_id})"

    def info(self) -> Proposal:
        return self.terra.gov.proposals(id=self.proposal_id)

    def proposer(self) -> AccAddress:
        return self.terra.gov.get_proposal_proposer(id=self.proposal_id)

    def deposits(self):
        return self.terra.gov.get_proposal_deposits(id=self.proposal_id)

    def votes(self):
        return self.terra.gov.get_proposal_votes(id=self.proposal_id)

    def tally(self):
        return self.terra.gov.get_proposal_tally(id=self.proposal_id)
