import os

import hashlib
import datetime
import pickle


class DataAPIBase:

    def __init__(self):
        self._from_cache = True
        self._cache_folder = '/data/tmp/cache/'
        self._date_col_name = 'date'

    @property
    def date_col_name(self):
        return self._date_col_name

    def get_all_data_between_dates(self, start_date, end_date):
        raise NotImplementedError

    def get_col_data_between_dates(self, start_date, end_date, search_column, search_str):
        raise NotImplementedError

    @staticmethod
    def create_date(year, month, day):
        return datetime.datetime(year=year, month=month, day=day)

    # -- Cache Functions --
    def _load_data_from_cache(self, unique_str):
        unique_fp = self._get_cache_path(unique_str)
        if os.path.exists(unique_fp):
            with open(unique_fp, 'rb') as handle:
                return pickle.load(handle)
        else:
            return None

    def _save_to_cache(self, unique_str, data):
        unique_fp = self._get_cache_path(unique_str)
        with open(unique_fp, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def _get_cache_path(self, unique_str):
        hex_str = hashlib.sha256(unique_str.encode()).hexdigest()
        hex_str += f'.pickle'
        filepath = os.path.join(self._cache_folder, hex_str)
        return filepath
