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

    def prep(self, url: str, ca_id):
        return "{url}/entity/{ca_id}?includeUnverified=true".format(url=url, ca_id=ca_id)

    def query(self, full_url, data):
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
        except:
            return self.error("Bad Request")

    @defaults_from_attrs('url', 'service')
    def run(self, data, url=None, service=None):
        full_url = self.prep(url, data)
        response = self.query(full_url)
        result = self.process(response)
        return result


class QueryCACompany(QueryCA):
    """
    Query to get datasys or rankings id.
    """

    def __init__(self, url=None, key=None, service=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(url, key, max_retries, retry_delay)
        self.name = "Central Authority Get Company"
        self.log_prefix = self.build_log_prefix()
        self.url = url
        self.key = key
        self.service = service

    def prep(self, url: str, ca_id):
        return "{url}/entity/{ca_id}?includeUnverified=true".format(url=url, ca_id=ca_id)

    def query(self, full_url, data):
        if "error" in full_url:
            return full_url
        logging.debug("{}: url {}".format(self.log_prefix, full_url))
        try:
            response = requests.get(
                url=full_url,
                params={},
                headers={'Authorization': self.key},
            )
            if response is not None:
                return response
            return self.error([Error(check_name="QueryCACompany", value=errors.bad_response, company=data,
                                    api_call=full_url)])
        except Exception as err:
            return self.error([Error(check_name="QueryCACompany", value="Bad request: {}".format(err), company=data,
                                    api_call=full_url)])

    def post_process(self, result, service, full_url, data):
        if "error" in result:
            return result
        if "biids" not in result:
            return self.error([Error(check_name="QueryCACompany", value=errors.service_name_dne("biids"), company=data,
                                api_call=full_url)])
        lst = result["biids"]
        for item in lst:
            if item["service"] == service:
                return item["value"]
        return self.error([Error(check_name="QueryCACompany", value=errors.service_name_dne(service), company=data,
                                api_call=full_url)])

    @defaults_from_attrs('url', 'service')
    def run(self, data, url=None, service=None):
        full_url = self.prep(url, data)
        response = self.query(full_url, data)
        result = self.process(response)
        biid = self.post_process(result, service, full_url, data)
        return biid
