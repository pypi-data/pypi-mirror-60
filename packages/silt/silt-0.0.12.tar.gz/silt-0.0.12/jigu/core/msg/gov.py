from __future__ import annotations
from typing import List, Dict, Any, Union
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address
from jigu.core import Coin, Coins, AccAddress

from jigu.core.msg import Message
from jigu.core.gov import (
    Content,
    TextProposal,
    CommunityPoolSpendProposal,
    ParameterChangeProposal,
    RewardWeightUpdateProposal,
    TaxRateUpdateProposal,
)


class MsgSubmitProposal(Message):

    type = "gov/MsgSubmitProposal"
    action = "submit_proposal"

    def __init__(
        self, content: Type[Content], initial_deposit: Coins, proposer: AccAddress
    ):
        validate_acc_address(proposer)
        self.content = content
        self.initial_deposit = initial_deposit
        self.proposer = proposer

    def msg_value(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "initial_deposit": self.initial_deposit,
            "proposer": self.proposer,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, Any]) -> MsgSubmitProposal:
        p_type = PROPOSAL_TYPES[data["content"]["type"]]
        content = p_type.from_dict(data["content"])
        return cls(
            content=content,
            initial_deposit=Coins.from_dict(data["initial_deposit"]),
            proposer=data["proposer"],
        )


class MsgDeposit(Message):

    type = "gov/MsgGovDeposit"
    action = "deposit"

    def __init__(self, proposal_id: int, depositor: AccAddress, amount: Coins):
        validate_acc_address(depositor)
        self.proposal_id = proposal_id
        self.depositor = depositor
        self.amount = amount

    def msg_value(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "depositor": self.depositor,
            "amount": self.amount,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, Any]) -> MsgDeposit:
        return cls(
            proposal_id=int(data["proposal_id"]),
            depositor=data["depositor"],
            amount=Coins.from_dict(data["amount"]),
        )


class MsgVote(Message):

    type = "gov/MsgVote"
    action = "vote"

    def __init__(self, proposal_id: int, voter: AccAddress, option: str):
        validate_acc_address(voter)
        self.proposal_id = proposal_id
        self.voter = voter
        self.option = option

    def msg_value(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "voter": self.voter,
            "option": self.option,
        }

    @classmethod
    def from_msg_dict(cls, data: Dict[str, Any]) -> MsgVote:
        return cls(
            proposal_id=int(data["proposal_id"]),
            voter=data["voter"],
            option=data["option"],
        )
