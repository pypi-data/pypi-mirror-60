from typing import Callable, Optional
import requests
import wrapt
import jigu.error


class BaseAPI(object):
    def __init__(self, client):
        self._c = client

    def _api_get(self, path, unwrap=True, **kwargs):
        return self._handle_response(self._c.get(path, **kwargs), unwrap)

    def _api_post(self, path, unwrap=True, **kwargs):
        return self._handle_response(self._c.post(path, **kwargs), unwrap)

    def _handle_response(self, response: requests.Response, unwrap=True):
        try:
            res = response.json()
            if str(response.status_code).startswith("5"):
                if type(res) == dict:
                    raise jigu.error.TerraAPIError(res.get("error", None))
                else:
                    raise jigu.error.TerraAPIError(
                        f"an error occured: {str(response.content)}"
                    )
            if str(response.status_code).startswith("2"):
                if unwrap:
                    return res["result"]
                else:
                    return res
        except ValueError:
            raise jigu.error.ClientError(f"invalid response {str(response.content)}")


from .modules.auth import AuthAPI
from .modules.bank import BankAPI
from .modules.supply import SupplyAPI
from .modules.distribution import DistributionAPI
from .modules.staking import StakingAPI
from .modules.slashing import SlashingAPI
from .modules.oracle import OracleAPI
from .modules.market import MarketAPI
from .modules.treasury import TreasuryAPI
from .modules.gov import GovAPI

from .tendermint import TendermintAPI
from .tx import TxAPI

from .response import Response
