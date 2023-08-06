from jigu.api import BaseAPI


class TendermintAPI(BaseAPI):
    def get_node_info(self):
        return self._api_get("/node_info", unwrap=False)

    def get_syncing(self) -> bool:
        res = self._api_get("/syncing", unwrap=False)
        return res["syncing"]

    def get_block(self, height=None):
        if height:
            res = self._api_get(f"/blocks/{height}", unwrap=False)
        else:
            res = self._api_get("/blocks/latest", unwrap=False)
        return res["block"]

    def get_validatorset(self, height=None):
        if height:
            res = self._api_get(f"/validatorsets/{height}")
        else:
            res = self._api_get("/validatorsets/latest")
        vs = res['validators']
        results = []
        for v in vs:
            results.append({
                "address": v['address'],
                "pub_key": v['pub_key'],
                "proposer_priority": int(v['proposer_priority']),
                "voting_power": int(v['voting_power'])
            })
        return results
