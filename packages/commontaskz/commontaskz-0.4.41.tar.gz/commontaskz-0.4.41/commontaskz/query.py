import requests
import logging
from prefect import task, Task
from prefect.utilities.tasks import defaults_from_attrs
from prefect.client import Secret
from prefect.utilities.notifications import slack_notifier
from prefect.engine.state import Failed
from datetime import timedelta
from . import errors


def camel_case(words: str) -> str:
    if words:
        return words.title().replace(' ', '')
    return ''

class Query(Task):
    def __init__(self, name=None, url=None, key=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        super().__init__(max_retries, retry_delay)
        self.name = name
        self.url = url
        self.key = key

        self.log_prefix = self.build_log_prefix()

    def query(self, url, data):
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
            return self.error([Error(check_name="QueryCACompany", value="Bad request", company=data,
                                api_call=full_url)])

    def process(self, response, data, full_url):
        if "error" in response:
            return response
        try:
            if response.status_code != 200:
                return self.error([Error(check_name="QueryCACompany", value=errors.response_code(response.status_code),
                                    company=data, api_call=full_url)])
            doc = response.json()
            if doc is None or not doc or doc == {}:
                return self.error([Error(check_name="QueryCACompany", value=errors.bad_response, company=data, api_call=full_url)])
            return doc
        except:
            return self.error(errors.bad_response)

    def error(self, lst: list) -> dict:
        full_msg = "{}: {}".format(self.log_prefix, lst)
        logging.error(full_msg)
        return {"error": lst}

    def build_log_prefix(self) -> str:
        return "Query{}".format(camel_case(self.name))

    @defaults_from_attrs('url')
    def run(self, data, url=None):
        full_url = self.prep(url, data)
        response = self.query(full_url)
        result = self.process(response)
        return result

