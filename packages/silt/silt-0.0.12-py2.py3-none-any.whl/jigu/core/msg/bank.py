from __future__ import annotations
from typing import List, Dict, Any, Union
from jigu.util import JSONSerializable, JSONDeserializable
from jigu.util.validation import validate_acc_address, validate_val_address
from jigu.core import Coin, Coins, AccAddress

from jigu.core.msg import Message
from collections import defaultdict


class MsgSend(Message):

    type = "bank/MsgSend"
    action = "send"

    def __init__(
        self,
        from_address: AccAddress,
        to_address: AccAddress,
        amount: Union[Coins, List[Coin]],
    ):
        validate_acc_address(from_address)
        validate_acc_address(to_address)
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount

    def msg_value(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "from_address": self.from_address,
            "to_address": self.to_address,
        }

    @classmethod
    def from_msg_dict(cls, data: dict) -> MsgSend:
        amount = Coins.from_dict(data["amount"])
        return cls(
            from_address=data["from_address"],
            to_address=data["to_address"],
            amount=amount,
        )


_coin = Dict[str, str]  # for type-hint


class MsgMultiSend(Message):

    type = "bank/MsgMultiSend"
    action = "multisend"

    def __init__(
        self, inputs: Dict[AccAddress, Coins], outputs: Dict[AccAddress, Coins],
    ):
        for addr in inputs:
            validate_acc_address(addr)
        for addr in outputs:
            validate_acc_address(addr)
        self.inputs = inputs
        self.outputs = outputs

    # List(Dict(
    #   address -> List of coins
    # ))
    def msg_value(self) -> Dict[str, List[dict]]:
        inputs_list = []
        outputs_list = []
        for addr in self.inputs:
            inputs_list.append({"address": addr, "amount": self.inputs[addr]})
        for addr in self.outputs:
            outputs_list.append({"address": addr, "amount": self.outputs[addr]})
        return {"inputs": inputs_list, "outputs": outputs_list}

    @classmethod
    def from_msg_dict(cls, data: dict) -> MsgMultiSend:
        inputs = defaultdict(lambda: Coins([]))
        outputs = defaultdict(lambda: Coins([]))
        for input in data["inputs"]:
            inputs[input["address"]] += Coins.from_dict(input["coins"])
        for output in data["outputs"]:
            outputs[output["address"]] += Coins.from_dict(output["coins"])
        return cls(inputs=inputs, outputs=outputs)
