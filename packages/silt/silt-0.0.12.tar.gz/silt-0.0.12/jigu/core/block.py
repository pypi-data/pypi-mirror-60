from __future__ import annotations
from typing import List

import jigu.terra
from jigu.core import TxInfo
from jigu.util import JSONDeserializable, hash_amino, pretty_repr


class Block(JSONDeserializable):
    def __init__(self, header: dict, txs: List[TxInfo]):
        self.header = header
        self.txs = txs

    def __repr__(self) -> str:
        return pretty_repr("Block", ("TXs:", self.txs))

    @classmethod
    def from_dict(cls, data: dict, terra: jigu.terra.Terra) -> Block:
        transactions = data["data"]["txs"] or []
        txs = []
        for tx in transactions:
            txs.append(terra.get_tx_info(hash_amino(tx)))  # populate each txn
        return cls(header=data["header"], txs=txs)

