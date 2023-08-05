import logging
from datetime import timedelta

import requests
from prefect.engine.result_handlers import JSONResultHandler
from prefect.utilities.tasks import defaults_from_attrs

from commontaskz import errors
from .query import Query
from datamodelz.error import Error


class QueryTimeseries(Query):
    """
    Basic
    """
    def __init__(self, key, timeseries=None, url=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "Timeseries"
        self.url = url
        self.key = "apiKey {}".format(key)
        self.timeseries = timeseries
        self.log_prefix = self.build_log_prefix()

    def prep(self, url: str, ca_id: str, timeseries: str):
        if "error" in ca_id:
            return ca_id
        new_url = "{url}/timeseries/{timeseries}/{ca_id}" \
            .format(url=url, ca_id=ca_id, timeseries=timeseries, skip=self.skip, limit=self.limit)
        return new_url

    @defaults_from_attrs('url', 'timeseries')
    def run(self, data, timeseries=None, url=None):
        full_url = self.prep(url, data, timeseries)
        response = self.query(full_url)
        result = self.process(response)
        return result


class GetTimeseriesData(Query):
    def __init__(self, key, timeseries=None, url=None, order=None, collapse=None, aggregation=None, transform=None,
                 max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "QueryTimeseries"
        self.url = url
        self.full_url = ""
        self.key = "apiKey {}".format(key)
        self.timeseries = timeseries
        self.order = order
        self.collapse = collapse
        self.aggregation = aggregation
        self.transform = transform
        self.log_prefix = self.build_log_prefix()
        self.final = {}
        self.data = None
        self.errors = []

    def prep(self, ca_id: str, url: str, timeseries: str, skip: int, limit:int, order, collapse, aggregation, transform):
        if "error" in ca_id:
            return ca_id
        new_url = "{url}/timeseries/{timeseries}/{ca_id}?skip={skip}&limit={limit}"\
            .format(url=url, ca_id=ca_id.lower(), timeseries=timeseries.lower(), skip=skip, limit=limit)
        if order:
            new_url += "&order={}".format(order.lower())
        if collapse:
            new_url += "&collapse={}".format(collapse.lower())
        if aggregation:
            new_url += "&aggregate={}".format(aggregation.lower())
        if transform:
            new_url += "&transform={}".format(transform.lower())
        self.full_url = new_url
        self.final["apiCall"] = new_url
        return new_url

    def query(self, url):
        if "error" in url:
            return url
        logging.debug("{}: url {}".format(self.log_prefix, url))
        try:
            response = requests.get(
                url=url,
                params={},
                headers={'Authorization': self.key},
            )
            return response
        except:
            return self.error(errors.query_failed(url))

    def process(self, response):
        if "error" in response:
            return response
        try:
            if response.status_code != 200:
                return self.error(str(response.status_code))
            doc = response.json()
            if doc is None or not doc or doc == {}:
                return self.error(errors.bad_response)
            return doc
        except:
            return self.error(errors.bad_response)

    @staticmethod
    def join(final, response):
        if "error" in response:
            return response
        if "data" in response:
            final["data"] = final["data"] + response["data"]
        return final

    def done(self, result, skip):
        # make data dict
        if "data" not in self.final:
            self.final = result
        else:
            self.final = self.join(self.final, result)
        if "error" in result:  # stop because bad response
            return True
        if skip >= result["totalCount"]:  # done getting results
            return True
        return False  # still more to go and no errors

    def error(self, msg: str) -> dict:
        logging.error("{}: {}".format(self.log_prefix, msg))
        self.errors.append(Error(timeseries_code=self.timeseries, company=self.data, check_name=self.name, value=msg,
                                 api_call=self.full_url))
        return

    @defaults_from_attrs('url', 'timeseries', 'order', 'collapse', 'aggregation', 'transform')
    def run(self, data, timeseries=None, url=None, order=None, collapse=None, aggregation=None, transform=None):
        """
        Repeats API call to get all data via paging for given timeseries type & company id
        :param order:
        :param data:
        :param timeseries:
        :param url:
        :param collapse:
        :param aggregation:
        :param transform:
        :return:
        """
        self.data = data
        skip, limit = 0, 500
        done = False
        while not done:  # runs until no more data
            full_url = self.prep(data, url, timeseries, skip, limit, order, collapse, aggregation, transform)
            response = self.query(full_url)
            result = self.process(response)
            skip += limit  # adding offset for next query
            done = self.done(result, skip)
        if self.errors:
            self.final["error"] = self.errors
        return self.final  # will return error or final results


class GetAllTimeseries(Query):
    def __init__(self, key, url=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "TimeseriesAllSignals"
        self.url = url
        self.key = "apiKey {}".format(key)
        self.log_prefix = self.build_log_prefix()

    @staticmethod
    def prep(url: str):
        return "{url}/timeseries".format(url=url)

    @staticmethod
    def post_process(result):
        if "data" in result:
            return result["data"]
        return []

    @defaults_from_attrs('url')
    def run(self, url=None):
        full_url = self.prep(url)
        response = self.query(full_url)
        result = self.process(response)
        timeseries = self.post_process(result)
        return timeseries


class SearchCompany(Query):
    def __init__(self, key, url=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "TimeseriesCompany"
        self.url = url
        self.key = "apiKey {}".format(key)
        self.log_prefix = self.build_log_prefix()

    @staticmethod
    def prep(timeseries_id: str, url: str):
        if "error" in timeseries_id:
            return timeseries_id
        return "{url}/companies?name={timeseries_id}".format(url=url, timeseries_id=timeseries_id)

    @defaults_from_attrs('url')
    def run(self, data, url=None):
        full_url = self.prep(data, url)
        response = self.query(full_url)
        result = self.process(response)
        return result
