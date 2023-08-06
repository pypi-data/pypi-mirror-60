from datetime import timedelta
from prefect.utilities.tasks import defaults_from_attrs
from .query_service import Query


class QueryDatasysCompany(Query):
    def __init__(self, key, url=None, max_retries=3, retry_delay=timedelta(minutes=1), **kwargs):
        super().__init__(key, url, max_retries, retry_delay, **kwargs)
        self.name = "Datasys"
        self.log_prefix = self.build_log_prefix()

    @staticmethod
    def prep(datasys_id: dict, url: str):
        if "biid" not in datasys_id:
            return
        biid = datasys_id["biid"]
        return "{}/repository/company/{}?trace=false".format(url, biid)

    @defaults_from_attrs('url')
    def run(self, data, url=None, **kwargs):
        if "error" in data:
            return data
        full_url = self.prep(datasys_id=data, url=url)
        response = self.query(data=data, full_url=full_url)
        result = self.process(data=data, full_url=full_url, response=response)
        result = self.add_api_call(full_url=full_url, result=result)
        return result
