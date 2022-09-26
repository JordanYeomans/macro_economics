import os
import json
import hashlib
import datetime
import pandas as pd


class DataAPIBase:

    def __init__(self):
        self._from_cache = True

    def get_all_data_between_dates(self, start_date, end_date):
        raise NotImplementedError

    def get_col_data_between_dates(self, start_date, end_date, search_column, search_str):
        raise NotImplementedError

    @staticmethod
    def create_date(year, month, day):
        return datetime.datetime(year=year, month=month, day=day)

    # -- Cache Functions --
    def _load_data_from_cache(self, unique_str, filetype):
        assert filetype in ['json', 'csv']
        unique_str_hash = self._get_cache_path(unique_str, filetype=filetype)
        data = None
        if os.path.exists(unique_str_hash):
            if filetype == 'json':
                with open(unique_str_hash, 'r') as f:
                    data = json.load(f)

            elif filetype == 'csv':
                data = pd.read_csv(unique_str_hash)
            else:
                raise NotImplementedError

        return data

    def _save_to_cache(self, unique_str, data, filetype):
        assert filetype in ['json', 'csv']
        unique_str_hash = self._get_cache_path(unique_str, filetype)
        if filetype == 'json':
            with open(unique_str_hash, 'w') as f:
                json.dump(data, f, indent=4)
        elif filetype == 'csv':
            data.to_csv(unique_str_hash, index=False)
        else:
            raise NotImplementedError

    @staticmethod
    def _get_cache_path(unique_str, filetype):
        base_folder = '/data/tmp/cache/'
        hex_str = hashlib.sha256(unique_str.encode()).hexdigest()
        hex_str += f'.{filetype}'
        filepath = os.path.join(base_folder, hex_str)
        return filepath
