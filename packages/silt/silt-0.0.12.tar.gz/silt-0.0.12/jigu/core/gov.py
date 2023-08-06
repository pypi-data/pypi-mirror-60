from __future__ import annotations
from typing import Dict, Optional, List, Type, Any

import abc
from jigu.util import JSONSerializable, JSONDeserializable, pretty_repr
from jigu.core import Timestamp, Coin, Coins, AccAddress, Dec
from jigu.core.denoms import uLuna
import json


class ProposalStatus(str):
    NIL = ""
    DEPOSIT_PERIOD = "DepositPeriod"
    VOTING_PERIOD = "VotingPeriod"
    PASSED = "Passed"
    REJECTED = "Rejected"
    FAILED = "Failed"


class Content(JSONSerializable, JSONDeserializable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def proposal_value(self):
        raise NotImeplementedError("Proposal Content must implement proposal_value()")

    @classmethod
    @abc.abstractmethod
    def from_proposal_dict(cls, data: dict):
        raise NotImplementedError(
            "Proposal Content must implement from_proposal_dict()"
        )

    @property
    @abc.abstractmethod
    def type(self):
        raise NotImplementedError("Proposal Content must implement type property")

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.proposal_value()}

    @classmethod
    def from_dict(cls, data: dict) -> Type[Content]:
        data = data["value"]
        return cls.from_proposal_dict(data)


class TextProposal(Content):

    type = "gov/TextProposal"

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return pretty_repr(
            "TextProposal", ("Title:", self.title), ("Description:", self.description)
        )

    def proposal_value(self) -> Dict[str, Any]:
        return {"title": self.title, "description": self.description}

    @classmethod
    def from_proposal_dict(cls, data: dict) -> TextProposal:
        return cls(title=data["title"], description=data["description"])


class ParameterChangeProposal(Content):

    type = "params/ParameterChangeProposal"

    def __init__(self, title: str, description: str, changes: List[dict]):
        self.title = title
        self.description = description
        self.changes = changes

    def __repr__(self) -> str:
        return (
            pretty_repr(
                "ParameterChangeProposal",
                ("Title:", self.title),
                ("Description:", self.description),
            )
            + "Changes:\n"
            + json.dumps(self.changes, indent=2)
        )

    def proposal_value(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "changes": self.changes,
        }

    @classmethod
    def from_proposal_dict(cls, data: dict) -> ParameterChangeProposal:
        return cls(
            title=data["title"],
            description=data["description"],
            changes=data["changes"],
        )


class CommunityPoolSpendProposal(Content):

    type = "distribution/CommunityPoolSpendProposal"

    def __init__(
        self, title: str, description: str, recipient: AccAddress, amount: Coins
    ):
        self.title = title
        self.description = description
        self.recipient = recipient
        self.amount = amount

    def __repr__(self) -> str:
        return pretty_repr(
            "CommunityPoolSpendProposal",
            ("Title:", self.title),
            ("Recipient:", self.recipient),
            ("Amount:", self.amount),
            ("Description:", self.description),
        )

    def proposal_value(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "recipient": self.recipient,
            "amount": self.amount,
        }

    @classmethod
    def from_proposal_dict(cls, data: dict) -> CommunityPoolSpendProposal:
        return cls(
            title=data["title"],
            description=data["description"],
            recipient=data["recipient"],
            amount=Coins.from_dict(data["amount"]),
        )


class TaxRateUpdateProposal(Content):

    type = "treasury/TaxRateUpdateProposal"

    def __init__(self, title: str, description: str, tax_rate: Dec):
        self.title = title
        self.description = description
        self.tax_rate = tax_rate

    def __repr__(self) -> str:
        return pretty_repr(
            ("Title:", self.title),
            ("Tax Rate ->", self.tax_rate),
            ("Description:", self.description),
        )

    def proposal_value(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "tax_rate": self.tax_rate,
        }

    @classmethod
    def from_proposal_dict(cls, data: dict) -> TaxRateUpdateProposal:
        return cls(
            title=data["title"],
            description=data["description"],
            tax_rate=Dec(data["tax_rate"]),
        )


class RewardWeightUpdateProposal(Content):

    type = "treasury/RewardWeightUpdateProposal"

    def __init__(self, title: str, description: str, reward_weight: Dec):
        self.title = title
        self.description = description
        self.reward_weight = reward_weight

    def __repr__(self) -> str:
        return pretty_repr(
            ("Title:", self.title),
            ("Reward Weight ->", self.tax_rate),
            ("Description:", self.description),
        )

    def proposal_value(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "reward_weight": self.reward_weight,
        }

    @classmethod
    def from_proposal_dict(cls, data: dict) -> RewardWeightUpdateProposal:
        return cls(
            title=data["title"],
            description=data["description"],
            reward_weight=Dec(data["reward_weight"]),
        )


PROPOSAL_TYPES = {
    "gov/TextProposal": TextProposal,
    "params/ParameterChangeProposal": ParameterChangeProposal,
    "distribution/CommunityPoolSpendProposal": CommunityPoolSpendProposal,
    "treasury/TaxRateUpdateProposal": TaxRateUpdateProposal,
    "treasury/RewardWeightUpdateProposal": RewardWeightUpdateProposal,
}


class Proposal(JSONDeserializable):
    def __init__(
        self,
        content: Type[Content],
        id: int,
        proposal_status: ProposalStatus,
        final_tally_result: Dict[str, Coin],
        submit_time: Timestamp,
        deposit_end_time: Timestamp,
        total_deposit: Coins,
        voting_start_time: Timestamp,
        voting_end_time: Timestamp,
    ):
        self.content = content
        self.id = id
        self.proposal_status = proposal_status
        self.final_tally_result = final_tally_result
        self.submit_time = submit_time
        self.deposit_end_time = deposit_end_time
        self.total_deposit = total_deposit
        self.voting_start_time = voting_start_time
        self.voting_end_time = voting_end_time

    def __repr__(self) -> str:
        return (
            pretty_repr(
                f"Proposal {self.id}",
                ("Type:", self.content.type),
                ("Status:", self.proposal_status),
                ("Submit Time:", self.submit_time),
                ("Deposit End Time:", self.deposit_end_time),
                ("Voting Start Time:", self.voting_start_time),
                ("Voting End Time:", self.voting_end_time),
            )
            + "\n"
            + repr(self.content)
        )

    @classmethod
    def from_dict(cls, data: dict) -> Proposal:
        final_tally_result = data["final_tally_result"]
        for key in final_tally_result:
            final_tally_result[key] = Coin(uLuna, int(final_tally_result[key]))
        p_type = PROPOSAL_TYPES[data["content"]["type"]]
        content = p_type.from_dict(data["content"])
        return cls(
            content=content,
            id=int(data["id"]),
            proposal_status=ProposalStatus(data["proposal_status"]),
            final_tally_result=final_tally_result,
            submit_time=Timestamp.from_dict(data["submit_time"]),
            deposit_end_time=Timestamp.from_dict(data["deposit_end_time"]),
            total_deposit=Coins.from_dict(data["total_deposit"]),
            voting_start_time=Timestamp.from_dict(data["voting_start_time"]),
            voting_end_time=Timestamp.from_dict(data["voting_end_time"]),
        )

