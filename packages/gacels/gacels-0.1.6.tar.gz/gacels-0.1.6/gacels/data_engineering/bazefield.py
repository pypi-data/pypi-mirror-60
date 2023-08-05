# This functionality is courtesy of Thibaut Forest (@thif)
import datetime as dt
import json
import re
import requests
import pandas as pd
import numpy as np
import urllib3

from requests.auth import HTTPBasicAuth

from gacels.data_engineering import azure_tools as at

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BazefieldClient:
    def __init__(self,
                 keyvault: at.AzureKeyvaultHelper,
                 from_timestamp: dt.datetime,
                 to_timestamp: dt.datetime,
                 reg_ex_strings: list,
                 aggregates: str = 'Raw',#'Min,Max,Average,End,Standard deviation',
                 interval: str = '0', #'10',
                 destination: str = '.',
                 datetime_format: str = 'dd-MM-yyyy HH:mm:ss.fff',
                 calender_unit: str = 'Second',
                 use_asset_title: bool = False,
                 use_interval: bool = True,
                 export_in_utc: bool = True):
        self.keyvault = keyvault
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.reg_ex_strings = reg_ex_strings
        self.aggregates = aggregates
        self.interval = interval
        self.destination = destination
        self.datetime_format = datetime_format
        self.calender_unit = calender_unit
        self.use_asset_title = use_asset_title
        self.use_interval = use_interval
        self.export_in_utc = export_in_utc
        
    @staticmethod
    def _get_datetime_as_string(timestamp: dt.datetime.timestamp,
                                string_format="%Y_%m_%d_%H_%M_%S") -> str:
        time_stamp_as_datetime = dt.datetime.fromtimestamp(timestamp / 1000)
        return time_stamp_as_datetime.strftime(string_format)

    @staticmethod
    def _reduce_dataframe_size(df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, df.select_dtypes(include=np.float64).columns] \
            = df.select_dtypes(include=np.float64).astype(np.float32)
        return df

    @staticmethod
    def _get_bazefield_headers() -> dict:
        headers = {'Content-Type': 'application/json;charset=UTF-8',
                   'Accept': 'application/json, text/plain, */*'}
        return headers

    @staticmethod
    def _match_taglist_to_regular_expression(tag_list: list, regular_expression: str) -> list:
        tag_ids = [t["tagId"] for t in tag_list
                   if re.match(regular_expression, t["tagName"])]
        return tag_ids

    def _get_bazefield_authentication(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.keyvault.get_secret(secret_name='bazefield-api-key'), '')

    def get_full_tag_list(self):
        auth = self._get_bazefield_authentication()
        tag_list_url = self.keyvault.get_secret(secret_name='bazefield-tagid-url')
        tag_list = requests.get(url=tag_list_url, verify=False, auth=auth)
        return json.loads(tag_list.text)

    def get_transformed_tag_list_from_bazefield(self, reg_ex_strings: list):
        tag_list = self.get_full_tag_list()

        tag_ids = []

        for reg_ex in reg_ex_strings:
            tag_ids = tag_ids + self._match_taglist_to_regular_expression(tag_list=tag_list,
                                                                          regular_expression=reg_ex)

        tag_list_to_download = {"tagIds": str(tag_ids)[1:-1].replace(" ", "")}

        tag_list_to_download["dateTimeFormat"] = self.datetime_format
        if self.calender_unit:
            tag_list_to_download["calenderUnit"] = self.calender_unit
        #tag_list_to_download["useAssetTitle"] = self.use_asset_title
        if self.use_interval:
            tag_list_to_download["useInterval"] = self.use_interval
        tag_list_to_download["exportInUtc"] = self.export_in_utc
        return json.dumps(tag_list_to_download)

    def prepare_download(self,
                         from_timestamp: int,
                         aggregates: str,
                         interval: str,
                         reg_ex_strings: list,
                         download_file_resolution=1000*3600*24):

        from_timestamp_as_string = self._get_datetime_as_string(from_timestamp)
        end_timestamp = from_timestamp + download_file_resolution

        print("Downloading " + from_timestamp_as_string)

        url = self.keyvault.get_secret(secret_name='bazefield-data-export-url')
        auth = self._get_bazefield_authentication()
        headers = self._get_bazefield_headers()
        proxy = {'https': self.keyvault.get_secret(secret_name='equinor-proxy')}
        data = self.get_transformed_tag_list_from_bazefield(reg_ex_strings)

        res = requests.post(url=url.format(from_timestamp, end_timestamp, interval, aggregates),
                            auth=auth,
                            headers=headers,
                            verify=False,
                            proxies=proxy,
                            data=data)

        filename = res.text
        next_timestamp = end_timestamp

        return filename, next_timestamp, from_timestamp_as_string

    def download_file(self, filename: str, from_timestamp_as_string: str):
        csv_name = from_timestamp_as_string + '.csv'
        filename = filename.replace(".txt", "")

        url = self.keyvault.get_secret(secret_name='bazefield-get-file-url')
        auth = self._get_bazefield_authentication()
        proxy = {'https': self.keyvault.get_secret(secret_name='equinor-proxy')}

        res = requests.get(url=url.format(filename),
                           auth=auth,
                           verify=False,
                           proxies=proxy)

        file = res.content.decode()

        file_path = self.destination + csv_name

        with open(file_path, 'w') as f:
            f.write(file)
            print("Finished.")
            print("Downloaded to "+ str(file_path))

        df = pd.read_csv(file_path, sep=';')
        df = self._reduce_dataframe_size(df)

        df.to_csv(file_path, sep=';')

        return True


    def download_data_from_bazefield_as_csv(self):
        """Downloads data from Bazefield using the Bazefield API.
        
        Arguments:
            from_timestamp {dt.datetime} -- Download data from and including this time.
            to_timestamp {dt.datetime} -- Download data to and including this time.
            aggregates {str} -- Which aggregates to download as specified by Bazefield.
            interval {str} -- Data interval to download. Example: '10Min'.
            reg_ex_strings {list} -- A list of regular expressions to match tags against.
        """
        from_timestamp_int = int(self.from_timestamp.timestamp()) * 1000
        to_timestamp_int = int(self.to_timestamp.timestamp())

        while True:
            try:
                filename, next_timestamp, from_timestamp_as_string = \
                    self.prepare_download(from_timestamp=from_timestamp_int,
                                          aggregates=self.aggregates,
                                          interval=self.interval,
                                          reg_ex_strings=self.reg_ex_strings)
                print('Downloading ' + from_timestamp_as_string)
                print(filename)
                _ = self.download_file(filename, from_timestamp_as_string)
            except Exception as e:
                print(e)
                from_timestamp_int = next_timestamp
                continue
            
            if dt.datetime.fromtimestamp(next_timestamp / 1000) \
            > dt.datetime.fromtimestamp(to_timestamp_int):
                return
            else:
                from_timestamp_int = next_timestamp
