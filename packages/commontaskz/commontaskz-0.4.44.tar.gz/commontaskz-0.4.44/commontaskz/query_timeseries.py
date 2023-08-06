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
    def __init__(self, key, url=None, order=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(key, url, max_retries, retry_delay)
        self.name = "QueryTimeseries"
        self.url = url
        self.key = "apiKey {}".format(key)
        self.order = order
        self.log_prefix = self.build_log_prefix()

    def prep(self,
             ca_id: str,
             url: str,
             timeseries: str,
             skip: int,
             limit: int,
             order: str,
             collapse: str,
             aggregate: str,
             transform: str):
        new_url = "{url}/timeseries/{timeseries}/{ca_id}?skip={skip}&limit={limit}"\
            .format(url=url, ca_id=ca_id.lower(), timeseries=timeseries.lower(), skip=skip, limit=limit)
        if order:
            new_url += "&order={}".format(order.lower())
        if collapse:
            new_url += "&collapse={}".format(collapse.lower())
        if aggregate:
            new_url += "&aggregate={}".format(aggregate.lower())
        if transform:
            new_url += "&transform={}".format(transform.lower())
        return new_url

    def query(self, company, url, timeseries):
        logging.debug("{}: querying {}".format(self.log_prefix, url))
        print("querying...", url)
        try:
            response = requests.get(
                url=url,
                params={},
                headers={'Authorization': self.key},
            )
            return response
        except Exception as err:
            logging.debug("{}: querying {} failed with error {}".format(self.log_prefix, url, err))
            return {"error": [Error(check_name="QueryTimeseries", value=err, timeseries_code=timeseries, company=company,
                                    api_call=url)]}

    @staticmethod
    def process(response, company, url, timeseries):
        if "error" in response:
            return response
        try:
            if response.status_code != 200:
                return {"error": [Error(check_name="QueryTimeseries", value=str(response.status_code),
                                        timeseries_code=timeseries, company=company, api_call=url)]}
            doc = response.json()
            if doc is None or not doc or doc == {}:
                return {"error": [Error(check_name="QueryTimeseries", value="Empty Response",
                                        timeseries_code=timeseries, company=company, api_call=url)]}
            return doc
        except:
            return {"error": [Error(check_name="QueryTimeseries", value="Bad Response",
                                    timeseries_code=timeseries, company=company, api_call=url)]}

    @staticmethod
    def join(final, result):
        if "error" in result:
            return result
        if "data" in result:
            final["data"] = final["data"] + result["data"]
        return final

    def done(self, final, result, skip):
        # make data dict
        if "data" not in final:
            final = result
        else:
            final = self.join(final, result)
        if "error" in result or skip >= result["totalCount"]:  # stop because bad response or done getting results
            return final, True
        return final, False  # still more to go and no errors

    @defaults_from_attrs('url', 'order')
    def run(self, data, timeseries=None, url=None, order=None, collapse=None, aggregate=None, transform=None):
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
        if "error" in data:
            return data
        final = {}
        skip, limit = 0, 500
        done = False
        while not done:  # runs until no more data
            full_url = self.prep(data, url, timeseries, skip, limit, order, collapse, aggregate, transform)
            response = self.query(data, full_url, timeseries)
            result = self.process(response, data, full_url, timeseries)
            skip += limit  # adding offset for next query
            final, done = self.done(final, result, skip)
            final["apiCall"] = full_url
        return final  # will return error or final results


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
