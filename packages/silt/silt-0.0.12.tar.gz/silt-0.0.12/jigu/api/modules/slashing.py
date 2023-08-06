from typing import Dict, Union, Optional
from jigu.api import BaseAPI

from jigu.core import Dec


class SlashingAPI(BaseAPI):
    def get_signing_info(self, validatorPubKey: str):
        return self._api_get(f"/slashing/validators/{validatorPubKey}/signing_info")

    def get_signing_infos(self):
        return self._api_get("/slashing/signing_infos")

    def params(self, key: Optional[str] = None) -> Union[int, Dec, dict]:
        p = self._api_get("/slashing/parameters")
        p["max_evidence_age"] = int(p["max_evidence_age"])
        p["signed_blocks_window"] = int(p["signed_blocks_window"])
        p["min_signed_per_window"] = Dec(p["min_signed_per_window"])
        p["downtime_jail_duration"] = int(p["downtime_jail_duration"])
        p["slash_fraction_double_sign"] = Dec(p["slash_fraction_double_sign"])
        p["slash_fraction_downtime"] = Dec(p["slash_fraction_downtime"])
        if key is None:
            return p
        else:
            return p[key]
