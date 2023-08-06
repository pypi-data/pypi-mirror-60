from typing import List, Dict, Union

from jigu.api import BaseAPI
from jigu.core import Dec, Coin, UnsignedTx, SignedTx, StdTx, Fee, TxInfo
from jigu.error import ValidationError

from jigu.util import serialize_to_json

_coin = Dict[str, str]


class TxAPI(BaseAPI):
    def get_info(self, hash: str) -> TxInfo:
        tx_info = self._api_get(f"/txs/{hash}", unwrap=False)
        return TxInfo.from_dict(tx_info)

    def estimate_fee(
        self,
        tx: Union[UnsignedTx, SignedTx],
        gas_adjustment: Union[float, str],
        gas_prices: List[Coin],
    ):
        data = {
            "tx": tx,
            "gas_adjustment": str(gas_adjustment),
            "gas_prices": gas_prices,
        }
        res = self._api_post("/txs/estimate_fee", data=data)
        gas = int(res["gas"])
        fees = [Coin.from_dict(coin) for coin in res["fees"]]
        return Fee(gas=gas, amount=fees)

    def encode(self, tx: StdTx):
        data = {"value": tx, "type": "core/StdTx"}
        res = self._api_post("/txs/encode", data=data, unwrap=False)
        return res["tx"]

    def broadcast(self, tx: SignedTx, mode: str = "block"):
        if mode not in ["block", "sync", "async"]:
            raise ValueError(
                f"mode '{mode}' is not legal; mode can only be 'block', 'sync', or 'async'."
            )
        data = {"tx": tx, "mode": mode}
        res = self._api_post("/txs", data=data, unwrap=False)
        tx_info = TxInfo.from_dict(res)
        tx_info.tx = tx
        return tx_info
