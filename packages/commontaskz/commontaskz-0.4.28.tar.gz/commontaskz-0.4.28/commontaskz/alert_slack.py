import slack
import logging

from datamodelz.error import Error
from prefect import Task
from datetime import date, timedelta, datetime
from prefect.utilities.tasks import defaults_from_attrs


def get_field(dct: dict, name):
    """
    Will check & get field via name
    :param dct: dict
    :param name: any key stored in a dictionary
    :return: any value stored in a dictionary
    """
    if type(dct) == dict and name in dct:
        return dct[name]
    return


def get_errors(errors, i) -> list:
    error_list = get_field(errors[i], "error")
    if type(error_list) == str:
        return [error_list]
    return error_list


def get_service_id(service_ids, i) -> str:
    service_id = ""
    if len(service_ids) > i and "error" not in service_ids[i]:
        service_id = service_ids[i]
    return service_id


class MakeErrorTask(Task):
    def __init__(self, token, titles=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        """
        :param titles:
        :param key: Slack Token to be used in slack.WebClient()
        """
        super().__init__(max_retries, retry_delay)
        self.name = "Make Error"
        self.titles = titles
        self.slack_client = slack.WebClient(token=token)

        # set automatically
        self.problems = []
        self.date = str(date.today())
        self.time = str(datetime.now().time())
        self.file = "results.csv"
        self.file_header = "Central Authority ID, Service ID, Errors"
        self.length = 0

    def make_file_name(self, titles: list) -> None:
        """
        Creates file name ex: datasys_kelvin_set_20190803.csv
        :param titles: list of strings
        :return: None
        """
        if titles:
            self.titles = titles
        title = "_".join(self.titles).lower().replace(" ", "_")
        self.file = "{}_{}.csv".format(title, self.date.replace("-", ""))
        return

    def make_list(self, errors: list, ca_ids: list, service_ids=[]) -> None:
        """
        :param errors: list of strings
        :param ca_ids: list of strings
        :param service_ids: list of strings (optional)
        :return: None
        """
        self.length = len(errors)  # so we how out of how many
        for i in range(0, len(errors)):
            error_list = get_errors(errors, i)
            if not error_list:
                continue
            service_id = get_service_id(service_ids, i)
            lst = [ca_ids[i], service_id] + error_list
            self.problems.append(lst)
        return

    def make_file(self) -> None:
        """
        requires: self.file, self.file_header, self.problems
        :return: None
        """
        if not self.problems:
            return
        with open(self.file, "w+") as csv:
            csv.write("Date, Time, Set Description\n")
            csv.write(','.join([self.date, self.time, ' '.join(self.titles), "\n\n"]))
            csv.write(self.file_header)
            for lst in self.problems:
                try:
                    csv.write("\n")
                    csv.write(",".join(lst))
                except:
                    logging.error("cannot print problems list {}".format(lst))
                    continue
        return

    def success_alert(self) -> bool:
        """
        :return: bool: ran ok
        """
        response = self.slack_client.chat_postMessage(
            channel='#prefect-data-alerts',
            text=":smile: New Alert from `{}` there are {} errors (out of {})"
                .format(" ".join(self.titles), len(self.problems), self.length),
        )
        return response["ok"]

    def failure_alert(self) -> bool:
        """
        :return: bool: ran ok
        """
        response = self.slack_client.files_upload(
            channels='#prefect-data-alerts',
            file=self.file,
            filename=self.file,
            filetype="csv",
            initial_comment=":frowning: New Alert from `{}` there are {} errors (out of {})"
                .format(" ".join(self.titles), len(self.problems), self.length),
            title=self.file
        )
        return response["ok"]

    @defaults_from_attrs('titles')
    def run(self, titles=None, errors=[], ca_ids=[], service_ids=[]) -> bool:
        """
        :param key: slack key
        :param titles:
        :param errors: list of strings
        :param ca_ids: list of strings
        :param service_ids: list of strings (optional)
        :return: bool: the run was successful & no errors
        """
        self.make_file_name(titles)
        self.make_list(errors, ca_ids, service_ids)
        if self.problems:
            self.make_file()
            self.failure_alert()
            return False
        else:
            self.success_alert()
            return True


class MakeGenericErrorTask(MakeErrorTask):
    def __init__(self, token, titles=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        """
        :param titles: list of strings describing the check
        :param key: slack key
        """
        super().__init__(token, titles, max_retries, retry_delay)
        self.name = "Make Generic Error"
        self.titles = titles
        self.slack_client = slack.WebClient(token=token)

        # set automatically
        self.problems = []
        self.date = str(date.today())
        self.time = str(datetime.now().time())
        self.file = "results.csv"
        self.file_header = "Service ID, Errors"

    def make_list(self, errors: list, service_ids=[]) -> None:
        """
        :param errors: list of strings
        :param service_ids: list of strings
        :return: None
        """
        self.length = len(errors)  # so we how out of how many
        for i in range(0, len(errors)):
            error_list = get_errors(errors, i)
            if not error_list:
                continue
            service_id = get_service_id(service_ids, i)
            lst = [service_id] + error_list
            self.problems.append(lst)
        return

    @defaults_from_attrs('titles')
    def run(self, titles=None, errors=[], service_ids=[]) -> bool:
        """
        :param titles:
        :param headers:
        :param errors: list of strings
        :param service_ids: list of strings (optional)
        :return: bool
        """
        self.make_file_name(titles)
        self.make_list(errors, service_ids)
        if self.problems:
            self.make_file()
            self.failure_alert()
            return False
        self.success_alert()
        return True


class MakeUserFriendlyErrorTask(MakeErrorTask):
    def __init__(self, token, titles=None, headers=None, headers_values=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        """
        needs to generate excel with 2 tabs and post to slack

        :param titles:
        :param key: Slack Token to be used in slack.WebClient()
        """
        super().__init__(max_retries, retry_delay)
        self.name = "Make User Friendly Error"
        self.titles = titles
        self.slack_client = slack.WebClient(token=token)

        # set automatically
        self.problems = []
        self.summary = []

        self.date = str(date.today())
        self.time = str(datetime.now().time())
        self.file = ""
        self.headers = headers
        self.headers_values = headers_values
        self.length = 0

    @staticmethod
    def build_errors_from_dct(error_dict: dict, ca_id: str, headers: list):
        """
        Uses a list of headers to build an organized error list for 1 error_dict.
        Should only be run when errors exist.
        :param error_dict:
        :param ca_id:
        :param headers:
        :return:
        """
        errors = [ca_id]
        for h in headers:  # go through names & creating error columns per name
            msg = ""  # empty if no error
            if h in error_dict and error_dict[h]:
                print(error_dict[h])
                msg = "; ".join(error_dict[h])
            errors += [msg]
        return errors

    def organize_errors(self, errors: list, ca_ids: list, headers: list) -> None:
        """
        :param self:
        :param headers:
        :param errors: list of strings
        :param ca_ids: list of strings
        :param service_ids: list of strings (optional)
        :return: None
        """
        if not errors:
            return
        self.length = len(errors)  # so we how out of how many
        for i in range(self.length):
            error_dict = get_errors(errors, i)
            if error_dict is None:  # skip if no errors for that company
                continue
            lst = self.build_errors_from_dct(error_dict=error_dict, ca_id=ca_ids[i], headers=headers)
            self.problems.append(lst)
        return

    def percent(self, x):
        return str(round(x/self.length*100))+"%"

    def build_summary(self, headers):
        counts = [0] * (len(headers) + 1)  # offset due to names column
        for errors in self.problems:
            for idx in range(len(errors)):
                if not errors[idx]:
                    continue
                counts[idx] += 1
        print(self.length)
        print(counts)
        self.summary = ["Summary of Errors"] + [self.percent(x) for x in counts[1:]]
        return self.summary

    @staticmethod
    def build_headers(headers, headers_values):
        lst = []
        for idx in range(len(headers)):
            lst.append("{} = {}".format(headers[idx], headers_values[idx]))
        return lst

    @staticmethod
    def writeable_list(lst, offset=False):
        if not lst:
            return ""
        writeable = ",".join(lst) + '\n'
        if offset:
            writeable = "," + writeable
        return writeable

    def make_file(self, titles, headers, headers_values) -> None:
        """
        requires: self.file, self.file_header, self.problems
        :return: None
        """
        if not self.problems:
            return
        with open(self.file, "w+") as csv:
            csv.write("Date, Time, Set Description\n")
            csv.write(self.writeable_list([self.date, self.time, ' '.join(titles), '\n']))
            csv.write(self.writeable_list(self.build_headers(headers, headers_values), offset=True))
            csv.write(self.writeable_list(self.summary))
            for lst in self.problems:
                try:
                    csv.write(self.writeable_list(lst))
                except:
                    logging.error("cannot print problems list {}".format(lst))
                    continue
        return

    @defaults_from_attrs('titles', 'headers', 'headers_values')
    def run(self, titles=None, headers=None, headers_values=None, errors=[], ca_ids=[]) -> bool:
        """
        :param headers_values:
        :param ca_ids:
        :param titles:
        :param headers:
        :param errors: list of strings
        :param service_ids: list of strings (optional)
        :return: bool
        """
        self.make_file_name(titles)
        self.organize_errors(errors, ca_ids, headers)
        if self.problems:
            self.build_summary(headers)
            self.make_file(titles, headers, headers_values)
            self.failure_alert()
            return False
        self.success_alert()
        return True


class MakePivotErrorTask(MakeErrorTask):
    def __init__(self, token, titles=None, max_retries=3, retry_delay=timedelta(minutes=1)):
        """
        needs to generate excel with 2 tabs and post to slack

        :param titles:
        :param key: Slack Token to be used in slack.WebClient()
        """
        super().__init__(token, titles, max_retries, retry_delay)
        self.name = "Make Pivot Error"
        self.counts = dict()
        self.formatted_counts = ""

    @staticmethod
    def writeable_list(lst, offset=False):
        if not lst:
            return ""
        writeable = ",".join(lst) + '\n'
        if offset:
            writeable = "," + writeable
        return writeable

    def make_error_list(self, errors: list) -> None:
        # error has type Error
        for i in range(len(errors)):
            error = get_errors(errors, i)
            for obj in error:
                if obj.empty():
                    continue
                self.problems.append(obj.excel_format())
        return

    def get_counts(self, errors):
        self.length = len(errors)
        counts = {}
        for row in self.problems:
            key = row[2]
            if key in counts:
                counts[key] = counts[key] + 1
            else:
                counts[key] = 1
        self.counts = counts
        return

    def format_counts(self):
        lst1 = []
        lst2 = []
        for k in self.counts:
            lst1.append(k)
            lst2.append(str(self.counts[k]))
        self.formatted_counts = self.writeable_list(lst1) + self.writeable_list(lst2)
        return

    def make_error_file(self, titles, collapse, aggregate) -> None:
        """
        requires: self.file, self.file_header, self.problems
        :return: None
        """
        if not self.problems:
            return
        with open(self.file, "w+") as csv:
            csv.write("Date, Time, Set Description, Collapse, Aggregate\n")
            csv.write(self.writeable_list([self.date, self.time, ' '.join(titles), collapse, aggregate, '\n']))
            csv.write("Timeseries Code, Company, Check, Date, Value, Business Rule, Reference Link, API Call\n")
            csv.write(self.formatted_counts)
            for lst in self.problems:
                try:
                    csv.write(lst)
                    csv.write('\n')
                except:
                    logging.error("cannot print problems list {}".format(lst))
                    continue
        return

    @defaults_from_attrs('titles')
    def run(self, titles=None, errors=[], collapse="", aggregate="") -> bool:
        """
        :param aggregate:
        :param collapse:
        :param titles:
        :param errors: list of strings
        :return: bool
        """
        self.make_file_name(titles)
        self.make_error_list(errors)
        if self.problems:
            self.get_counts(errors)
            self.format_counts()
            self.make_error_file(titles, collapse, aggregate)
            self.failure_alert()
            return False
        self.success_alert()
        return True

