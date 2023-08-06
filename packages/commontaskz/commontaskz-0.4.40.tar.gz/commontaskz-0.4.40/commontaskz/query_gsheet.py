import requests
import logging
from datetime import timedelta

from prefect.engine.result_handlers import JSONResultHandler
from prefect.utilities.tasks import defaults_from_attrs
from .query import Query


class QueryGSheet(Query):
    """
    Base class for querying CA
    """
    def __init__(self, key=None, url=None, a_range=None, sheet_id=None, sheet_name=None,
                 max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "GSheet"
        self.key = key
        self.url = url
        self.a_range = a_range
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.log_prefix = self.build_log_prefix()

    def prep(self, url, key, a_range, sheet_id, sheet_name):
        url = "{url}/{sheet_id}/values/{sheet_name}!{a_range}?key={key}" \
            .format(url=url, sheet_id=sheet_id, sheet_name=sheet_name, a_range=a_range, key=key)
        return url

    def query(self, url):
        return requests.get(url, params={}, headers={})

    def post_process(self, result, collapse=True):
        companies = []
        if "values" not in result:
            return []
        values = result["values"]
        if not collapse:  # return early & don't collapse lists
            return values
        for company in values:
            companies += company
        logging.debug("{}: {} companies returned".format(self.log_prefix, len(companies)))
        companies = [x for x in companies if x != ""]
        return companies

    @defaults_from_attrs('url', 'key', 'a_range', 'sheet_id', 'sheet_name')
    def run(self, url=None, key=None, a_range=None, sheet_id=None, sheet_name=None, collapse=True):
        full_url = self.prep(url, key, a_range, sheet_id, sheet_name)
        response = self.query(full_url)
        result = self.process(response)
        ids = self.post_process(result, collapse)
        return ids

class WriteGSheet(QueryGSheet):
    """
    Base class for querying CA
    """
    def __init__(self, key=None, url=None, a_range=None, sheet_id=None, sheet_name=None,
                 max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, a_range, sheet_id, sheet_name, max_retries, retry_delay)
        self.name = "GSheet"
        self.log_prefix = self.build_log_prefix()

    def prep(self, url, key, a_range, sheet_id, sheet_name):
        url = "{url}spreadsheets/{sheet_id}/values/{sheet_name}!{a_range}:append?valueInputOption=USER_ENTERED?" \
              "key={key}".format(url=url, sheet_id=sheet_id, sheet_name=sheet_name, a_range=a_range, key=key)
        return url

    def query(self, url, values):
        return requests.put(url, params=values, headers={})

    def post_process(self, result):
        if "spreadsheetId" in result:
            return result["spreadsheetId"]
        return ""


    @defaults_from_attrs('url', 'key', 'a_range', 'sheet_id', 'sheet_name')
    def run(self, url=None, key=None, a_range=None, sheet_id=None, sheet_name=None, values=None):
        full_url = self.prep(url, key, a_range, sheet_id, sheet_name)
        response = self.query(full_url, values)
        result = self.process(response)
        sheet_id = self.post_process(result)
        return sheet_id
