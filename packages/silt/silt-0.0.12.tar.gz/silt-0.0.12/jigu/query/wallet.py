from __future__ import annotations
from typing import Optional, List, Union, Type

import base64

import jigu.terra
from jigu.core import UnsignedTx, SignedTx, Fee, StdTx, Message, Signature
from jigu.key import Key
from jigu.query.account import AccountQuery
from jigu.util import abbreviate


class Wallet(AccountQuery):
    """A Wallet is an augmented AccountQuery, and provides `chain_id`, `account_number`,
    and `sequence` information for signing transactions, which is performed by a Key."""

    def __init__(self, terra: jigu.terra.Terra, key: Type[Key]):
        AccountQuery.__init__(self, terra, key.acc_address)
        self.key = key
        self.terra = terra
        self._account_number = 0

    def __repr__(self):
        return f"Wallet({abbreviate(self.address)} --> {self.terra.chain_id} via {self.terra.node_uri})"

    @property
    def account_number(self):
        if self._account_number == 0:
            self._account_number = self.info().account_number
        return self._account_number

    @property
    def sequence(self) -> int:
        return self.info().sequence

    def create_tx(
        self,
        msgs: Union[Message, List[Message]],
        fee: Optional[Fee] = None,
        memo: str = "",
    ) -> UnsignedTx:
        if type(msgs) != list:
            msgs = [msgs]  # singular
        if not fee:
            # estimate our fee if fee not supplied
            tx = StdTx(msg=msgs, memo=memo)
            fee = self.terra.estimate_tx_fee(tx)
        return UnsignedTx(
            chain_id=self.terra.chain_id,
            account_number=self.account_number,
            sequence=self.sequence,
            fee=fee,
            msgs=msgs,
            memo=memo,
        )

    def create_signature(self, tx: Union[SignedTx, UnsignedTx]) -> Signature:
        sig_data = self.key.sign(tx.to_json(sort=True).strip())
        return Signature(
            signature=base64.b64encode(sig_data).decode(),
            pub_key_value=base64.b64encode(self.key.public_key).decode(),
        )

    def sign_tx(self, tx: Union[UnsignedTx, SignedTx]) -> SignedTx:
        signature = self.create_signature(tx)
        if isinstance(tx, SignedTx):
            tx.signatures.append(signature)
            return tx
        else:
            return SignedTx(
                fee=tx.fee, msg=tx.msgs, signatures=[signature], memo=tx.memo
            )

