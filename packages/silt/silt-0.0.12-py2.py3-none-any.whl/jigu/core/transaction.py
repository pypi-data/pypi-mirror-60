from __future__ import annotations
from typing import List, Dict, Union, Any, Optional

from jigu.core import Coin, Timestamp
from jigu.core.msg import Message, MSGTYPES
from jigu.util import JSONSerializable, JSONDeserializable, pretty_repr

_coin = Dict[str, str]  # for type-hint


class StdFee(JSONSerializable, JSONDeserializable):
    def __init__(self, gas: int = 0, amount: List[Coin] = []):
        self.gas = gas
        self.amount = amount

    def __repr__(self) -> str:
        return f"Fee(gas={self.gas}, amount={self.amount})"

    def to_dict(self) -> Dict[str, Union[str, List[Coin]]]:
        return {"gas": str(self.gas), "amount": self.amount}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StdFee:
        amount = [Coin.from_dict(coin) for coin in data["amount"]]
        return cls(gas=int(data["gas"]), amount=amount)


class StdSignature(JSONSerializable, JSONDeserializable):
    def __init__(
        self,
        signature: str,
        pub_key_value: str,
        pub_key_type: str = "tendermint/PubKeySecp256k1",
    ):
        self.signature = signature
        self.pub_key = {"type": pub_key_type, "value": pub_key_value}

    def __str__(self) -> str:
        return self.signature

    def __repr__(self) -> str:
        return pretty_repr(
            "StdSignature",
            ("Signature:", self.signature),
            ("PubKey Type:", self.pub_key["type"]),
            ("PubKey Value:", self.pub_key["value"]),
        )

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {"signature": self.signature, "pub_key": self.pub_key}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StdSignature:
        pub_key = data["pub_key"]
        return cls(
            signature=data["signature"],
            pub_key_value=pub_key["value"] if pub_key else None,
            pub_key_type=pub_key["type"] if pub_key else None,
        )


class StdSignMsg(JSONSerializable):
    def __init__(
        self,
        chain_id: Optional[str] = None,
        account_number: Optional[int] = None,
        sequence: int = None,
        fee: StdFee = None,
        msgs: List[Message] = [],
        memo: str = "",
    ):
        self.chain_id = chain_id
        self.account_number = account_number
        self.sequence = sequence
        self.fee = fee
        self.msgs = msgs
        self.memo = memo

    def __repr__(self) -> str:
        return pretty_repr(
            "StdSignMsg",
            ("Chain ID:", self.chain_id),
            ("Account Number:", self.account_number),
            ("Sequence:", self.sequence),
            (f"Messages ({len(self.msgs)}):", ",".join(msg.type for msg in self.msgs)),
            ("Fee:", self.fee),
            ("Memo:", self.memo),
        )

    def to_dict(self) -> Dict[str, Any]:  # too lazy :P
        return {
            "chain_id": self.chain_id,
            "account_number": str(self.account_number),
            "sequence": str(self.sequence),
            "fee": self.fee,
            "msgs": self.msgs,
            "memo": self.memo,
        }


class StdTx(JSONSerializable, JSONDeserializable):

    # NOTE: msg is not plural, and is NOT a typo. This may change later for consistency.
    def __init__(
        self,
        fee: Optional[StdFee] = None,
        msg: List[Message] = [],
        signatures: List[StdSignature] = [],
        memo: str = "",
    ):
        self.fee = fee
        self.msg = msg
        self.signatures = signatures
        self.memo = memo

    def __repr__(self) -> str:
        abbr_sigs = [f"{s.signature[:5]}...{s.signature[-5:]}" for s in self.signatures]
        return pretty_repr(
            "StdTx",
            (f"Messages ({len(self.msg)}):", ",".join(msg.type for msg in self.msg)),
            ("Fee:", self.fee),
            (f"Signatures: ({len(self.signatures)})", ",".join(abbr_sigs)),
            ("Memo:", self.memo),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fee": self.fee,
            "msg": self.msg,
            "signatures": self.signatures,
            "memo": self.memo,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StdTx:
        fee = StdFee.from_dict(data["fee"])
        # deserialize the messages
        msg = []
        for m in data["msg"]:
            msg_type = MSGTYPES[m["type"]]
            msg.append(msg_type.from_dict(m))
        signatures = [StdSignature.from_dict(s) for s in data["signatures"]]
        return cls(fee=fee, msg=msg, signatures=signatures, memo=data["memo"])


class TxInfo(JSONDeserializable):
    def __init__(
        self,
        height: Optional[int] = None,
        txhash: Optional[str] = None,
        logs: Optional[List[Dict[str, Any]]] = None,
        gas_wanted: Optional[int] = None,
        gas_used: Optional[int] = None,
        timestamp: Optional[Timestamp] = None,
        tx: Optional[StdTx] = None,
    ):
        self.height = height
        self.txhash = txhash
        self.logs = logs
        self.gas_wanted = gas_wanted
        self.gas_used = gas_used
        self.timestamp = timestamp
        self.tx = tx

    def __repr__(self) -> str:
        ratio = str(self.gas_used / self.gas_wanted * 100)[:4]
        return pretty_repr(
            "Transaction Info",
            ("Height:", self.height),
            ("TX Hash:", self.txhash),
            ("Gas Used / Wanted:", f"{self.gas_used}/{self.gas_wanted} ({ratio}%)"),
            ("Timestamp:", self.timestamp),
            (f"Logs ({len(self.logs) if self.logs else None})", "(use txinfo.logs)"),
            (f"TX", "(use txinfo.tx for more)"),
            (
                f"TX Messages ({len(self.tx.msg)})",
                ", ".join(msg.type for msg in self.tx.msg),
            ),
        )

    @classmethod
    def from_dict(cls, data: dict) -> TxInfo:
        height = int(data["height"]) if "height" in data else None
        txhash = data.get("txhash", None)
        logs = data.get("logs", None)  # TODO: make logs easier to work with
        gas_wanted = int(data["gas_wanted"]) if "gas_wanted" in data else None
        gas_used = int(data["gas_used"]) if "gas_used" in data else None
        tx = StdTx.from_dict(data["tx"]["value"]) if "tx" in data else None
        timestamp = (
            Timestamp.from_dict(data["timestamp"]) if "timestamp" in data else None
        )
        return cls(
            height=height,
            txhash=txhash,
            logs=logs,
            gas_wanted=gas_wanted,
            gas_used=gas_used,
            tx=tx,
            timestamp=timestamp,
        )
