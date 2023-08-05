import datetime
import json
import time
from socket import timeout
from urllib import request, parse, error

import numpy as np

from aegis_data.database.database_factory import database_factory
from aegis_data.util.ansi_code import AnsiEscapeCode as ansi
from aegis_data.util.config import ConfigFileReader
from aegis_data.util import aux_functions

DB_TYPE = 'DB_TYPE'
DATE_FORMAT = 'DATE_FORMAT'
NA_ACCOUNT_LIMIT_LO = 'NA_ACCOUNT_LIMIT_LO'
NA_ACCOUNT_LIMIT_HI = 'NA_ACCOUNT_LIMIT_HI'
ID_STEP = 'ID_STEP'
SIZE_PER_WRITE = 'SIZE_PER_WRITE'
URL_REQ_DELAY = 'URL_REQ_DELAY'
URL_REQ_TIMEOUT = 'URL_REQ_TIMEOUT'
URL_REQ_TRYNUM = 'URL_REQ_TRYNUM'

APPLICATION_ID = 'application_id'
ACCOUNT_URL = 'account_url'
STATS_BY_DATE_URL = 'stats_by_date_url'


class WowsAPIRequest(object):
    def __init__(self, config_file):
        # *************CRUCIAL PARAMETERS**************
        self._init_params(config_file)
        self._db = database_factory(db_type=self._db_type, config_file=config_file)
        print("API initialized from {}!".format(config_file))

    def _init_params(self, config_file):
        params = ConfigFileReader().read_api_config(config_file=config_file)
        self.size_per_write = params[SIZE_PER_WRITE]
        self._request_delay = params[URL_REQ_DELAY]
        self._account_id_upperbound = params[NA_ACCOUNT_LIMIT_HI]
        self._account_id_lowerbound = params[NA_ACCOUNT_LIMIT_LO]
        self._account_id_step = params[ID_STEP]
        self._date_format = params[DATE_FORMAT]
        self._application_id = params[APPLICATION_ID]
        self._account_url = params[ACCOUNT_URL]
        self._stats_by_date_url = params[STATS_BY_DATE_URL]
        self._url_req_try_number = params[URL_REQ_TRYNUM]
        self._url_req_timeout = params[URL_REQ_TIMEOUT]
        self._db_type = params[DB_TYPE]
        self.failed_urls = list()
        self._date = datetime.datetime.now().strftime("%Y-%m-%d")

    def request_all_ids(self):
        """
        Request all ids by enumerating (WOWS currently does not provide API to list all ids)

        Account ID range
            if ($id <  500000000) return 'RU';
            elseif ($id < 1000000000) return 'EU';
            elseif ($id < 2000000000) return 'NA';
            elseif ($id < 3000000000) return 'ASIA';
            elseif ($id >= 3000000000) return 'KR';
        """
        requested_id_list = list()
        print('Task: Requesting all IDs...')
        for account_id in range(self._account_id_lowerbound, self._account_id_upperbound, self._account_id_step):
            id_list = aux_functions.list_to_url_params(self.generate_id_list_by_range(account_id))
            params = parse.urlencode({'application_id': self._application_id, 'account_id': id_list})
            url = "{}?{}".format(self._account_url, params)
            requested_id_list += self.return_from_url_request(url=url)
            requested_id_list = self.write_database_and_clear(data_list=requested_id_list, type_detail=False)
            print("Requested id length in buffer: {}".format(len(requested_id_list)))
            time.sleep(self._request_delay)

    def request_stats_by_id(self):
        self.failed_urls = list()
        id_list = self.get_id_list(get_entire_list=True)
        total_count = len(id_list)
        count = 0
        sub_id_list = list()
        result_list = list()
        print('Task: Total request number to be executed: %s%d%s' % (
            ansi.BLUE, int(np.ceil(total_count / self._account_id_step)), ansi.ENDC))
        for account_id in id_list:
            sub_id_list.append(account_id)
            if len(sub_id_list) == self._account_id_step or total_count - count < self._account_id_step:
                result_list = self.get_stats_from_api(result_list=result_list, id_list=sub_id_list)
                sub_id_list = list()
                count += self._account_id_step
        while self.failed_urls:
            self.get_stats_from_failed_api()
        print('Stats by id request finished!')

    def request_stats_by_date(self, date_list):
        self.failed_urls = list()
        id_list = self.get_id_list(get_entire_list=False)
        print('Task: Total request number to be executed: %s%d%s. Covering dates: %s%s%s to %s%s%s' % (
            ansi.BLUE, len(id_list), ansi.ENDC, ansi.BLUE, date_list[0], ansi.ENDC, ansi.BLUE,
            date_list[len(date_list) - 1], ansi.ENDC))
        result_list = list()
        count = 0
        time_usage_total = datetime.timedelta()
        for account_id in id_list:
            timer_start = datetime.datetime.now()
            pseudo_id_list = [account_id]
            result_list = self.get_stats_from_api(result_list=result_list, id_list=pseudo_id_list,
                                                  date_list=date_list)
            count += 1
            time_usage = datetime.datetime.now() - timer_start
            time_usage_total += time_usage
            if count % self.size_per_write == 0:
                print('\n%s%s%s/%s ids requested, time usage: %s%s%s, ETA: %s%s%s\n' % (
                    ansi.BLUE, count, ansi.ENDC, len(id_list), ansi.BLUE, time_usage,
                    ansi.ENDC, ansi.BLUE, time_usage_total * (len(id_list) - count) / count, ansi.ENDC))
                result_list = self.write_database_and_clear(data_list=result_list, force_write=True)

        while self.failed_urls:
            self.get_stats_from_failed_api()
        print('Stats by date request finished!')

    def get_stats_from_api(self, result_list=list(), id_list=list(), date_list=list()):
        if not date_list:
            id_list = aux_functions.list_to_url_params(id_list)
            parameter = parse.urlencode({'application_id': self._application_id, 'account_id': id_list})
            main_url = self._account_url
        else:
            assert len(id_list) == 1
            date_para = aux_functions.list_to_url_params(date_list)
            parameter = parse.urlencode(
                {'application_id': self._application_id, 'account_id': id_list[0], 'date_list': date_para})
            main_url = self._stats_by_date_url

        url = main_url + '?' + parameter
        result_list += self.return_from_url_request(url=url)
        time.sleep(self._request_delay)
        return self.write_database_and_clear(data_list=result_list)

    def get_stats_from_failed_api(self, result_list=list()):
        print('Start requesting failed APIs...')
        failed_url_list = self.failed_urls
        self.failed_urls = list()
        for url in failed_url_list:
            result_list += self.return_from_url_request(url=url)
        self.write_database_and_clear(data_list=result_list, force_write=True)

    def return_from_url_request(self, url):
        number_of_try = self._url_req_try_number
        json_returned = {'status': 'ini', 'data': {}}
        while number_of_try > 0:
            try:
                while json_returned['status'] != 'ok':
                    if json_returned['status'] is not 'ini':
                        print('%s API error message: %s%s' % (ansi.RED, json_returned['error'], ansi.ENDC))
                    json_returned = json.loads(
                        request.urlopen(url, timeout=self._url_req_timeout).read().decode('utf-8'))
                break
            except (error.URLError, timeout, ConnectionResetError) as e:  # API url request failed
                print('%sAPI request failed!%s %s' % (ansi.RED, e, ansi.ENDC))
                if e is timeout:
                    time.sleep(self._request_delay)
                number_of_try -= 1
                if number_of_try == 0:
                    self.failed_urls.append(url)
        json_list = list()
        for account_id_item in json_returned['data'].items():
            json_list.append(json.dumps(account_id_item))
        return json_list

    def write_database_and_clear(self, data_list, type_detail=True, force_write=False):
        msg = 'Start recording details...' if type_detail else 'Start recording ids...'
        if len(data_list) >= self.size_per_write or force_write:
            print(msg)
            if type_detail:
                self._db.write_detail(data_list)
            else:
                self._db.write_account_id(data_list)
            data_list = list()
        return data_list

    def update_database_winrate(self, start=datetime.date.today(), end=datetime.date.today()):
        self._db.update_win_rate(start=start, end=end)

    def get_id_list(self, get_entire_list=True):
        print('Reading ID list...')
        idlist = self._db.get_id_list(get_all_ids=get_entire_list)
        print('%sID list read finished%s' % (ansi.GREEN, ansi.ENDC))
        return idlist

    def generate_id_list_by_range(self, account_ID):
        ids = []
        for i in range(self._account_id_step):
            ids.append(int(account_ID + i))
        return ids

    def request_historical_stats_all_accounts(self, date):
        timer_start = datetime.datetime.now()
        aux_functions.check_ip()
        self._date = date
        date_list = aux_functions.generate_date_list_of_ten_days(date=date)
        self.request_stats_by_date(date_list=date_list)
        self.update_database_winrate(start=date, end=date)

        time_usage = datetime.datetime.now() - timer_start
        print('\n%s%s%s data update finished, time usage: %s%s%s\n' % (
            ansi.BLUE, date.strftime(self._date_format), ansi.ENDC, ansi.DARKGREEN, time_usage,
            ansi.ENDC))
        return time_usage

    def request_historical_stats_all_accounts_last_month(self, start_date=None, days=28):
        if start_date is not None:
            start = datetime.datetime.strptime(start_date, self._date_format).date()
        else:
            start = datetime.date.today()
        days_limit = 10
        while days > 0:
            self.request_historical_stats_all_accounts(date=start)
            days -= days_limit
            start -= datetime.timedelta(days=days_limit)
        print('Main request finished!')


if __name__ == '__main__':
    # WowsAPIRequest().request_all_ids()
    WowsAPIRequest("config.json").request_historical_stats_all_accounts_last_month(start_date='2019-04-01')
