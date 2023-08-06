import requests
import logging
from datetime import timedelta

from datamodelz.error import Error
from prefect.engine.result_handlers import JSONResultHandler
from prefect.utilities.tasks import defaults_from_attrs
from .query import Query
from . import errors


class QueryCA(Query):
    """
    Base Query.
    """

    def __init__(self, url=None, key=None, service=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(url, key, max_retries, retry_delay)
        self.name = "Central Authority Get Company"
        self.log_prefix = self.build_log_prefix()
        self.url = url
        self.key = key
        self.service = service

    def prep(self, ca_id, url: str):
        return "{url}/entity/{ca_id}?includeUnverified=true".format(url=url, ca_id=ca_id)

    def query(self, data, full_url):
        if "error" in full_url:
            return full_url
        logging.debug("{}: url {}".format(self.log_prefix, full_url))
        try:
            response = requests.get(
                url=full_url,
                params={},
                headers={'Authorization': self.key},
            )
            return response
        except Exception as err:
            return self.error(Error(check_name="QueryCACompany", value="Bad request: {}".format(err), company=data,
                                    api_call=full_url))

    @defaults_from_attrs('url', 'service')
    def run(self, data, url=None, service=None):
        full_url = self.prep(data, url)
        response = self.query(data, full_url)
        result = self.process(data, full_url, response)
        result = self.add_api_call(full_url, result)
        return result


class QueryCACompany(QueryCA):
    """
    Query to get datasys or rankings id.
    """

    def __init__(self, url=None, key=None, service=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(url, key, max_retries, retry_delay)
        self.name = "Query CA Company"
        self.log_prefix = self.build_log_prefix()
        self.url = url
        self.key = key
        self.service = service

    def prep(self, ca_id, url: str):
        return "{url}/entity/{ca_id}?includeUnverified=true".format(url=url, ca_id=ca_id)

    def query(self, data, full_url):
        if "error" in full_url:
            return full_url
        print(full_url)
        logging.debug("{}: url {}".format(self.log_prefix, full_url))
        try:
            response = requests.get(
                url=full_url,
                params={},
                headers={'Authorization': self.key},
            )
            if response is not None:
                return response
            return self.error(Error(check_name="QueryCACompany", value="Bad request", company=data,
                                    api_call=full_url))
        except Exception as err:
            return self.error(Error(check_name="QueryCACompany", value="Bad request: {}".format(err), company=data,
                                    api_call=full_url))

    def post_process(self, data, full_url, result, service):
        if "error" in result:
            return result
        if "biids" not in result:
            return self.error(Error(check_name="QueryCACompany", value=errors.service_name_dne("biids"), company=data,
                                    api_call=full_url))
        lst = result["biids"]
        for item in lst:
            if item["service"] == service:
                return item["value"]
        return self.error(Error(check_name="QueryCACompany", value=errors.service_name_dne(service), company=data,
                                api_call=full_url))

    @defaults_from_attrs('url', 'service')
    def run(self, data, url=None, service=None):
        full_url = self.prep(data, url)
        response = self.query(data, full_url)
        result = self.process(data, full_url, response)
        biid = self.post_process(data, full_url, result, service)
        return biid
