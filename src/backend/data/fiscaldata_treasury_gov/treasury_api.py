import json
import hashlib
import datetime
import os.path

import requests
import pandas as pd

from src.backend.data.api_base import DataAPIBase


class TreasuryAPI(DataAPIBase):

    """
    This is the base class to interact with the Treasury API.

    Ref: https://fiscaldata.treasury.gov/api-documentation/

    """

    def __init__(self, endpoint, default_fields):
        super().__init__()
        self.base_url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service'
        self.endpoint = endpoint

        # Remove trailing '/' if present
        if self.endpoint[-1] == '/':
            self.endpoint = self.endpoint[:-1]

        self._default_fields = default_fields

    def get_all_data_between_dates(self, start_date, end_date, fields=None):
        assert isinstance(start_date, datetime.datetime)
        assert isinstance(end_date, datetime.datetime)

        if fields is None:
            fields = self.default_fields

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        start_filter = self.create_filter(field_name='record_date', operator='gte', value=start_date_str)
        end_filter = self.create_filter(field_name='record_date', operator='lte', value=end_date_str)
        filters = [start_filter, end_filter]

        return self.send_request(fields=fields, filters=filters)

    def get_col_data_between_dates(self, start_date, end_date, search_column, search_str, fields=None):
        data = self.get_all_data_between_dates(start_date=start_date, end_date=end_date, fields=fields)
        assert search_str in data[search_column].unique()
        return data[data[search_column] == search_str].reset_index(drop=True)

    def send_request(self, fields, filters):
        data = self._send_request(fields=fields, filters=filters)

        if data['meta']['total-pages'] == 0:
            print('Warning: No Pages Received')

        if data['meta']['total-pages'] > 1:
            page_size = data['meta']['total-count']
            data = self._send_request(fields=fields, filters=filters, page_size=page_size)

        # Ensure that the total number of pages == 1 - this ensures we have all the data
        assert data['meta']['total-pages'] <= 1

        formatted_data = self._format_data(data)
        return formatted_data

    @property
    def default_fields(self):
        return self._default_fields

    @staticmethod
    def create_date(year, month, day):
        return datetime.datetime(year=year, month=month, day=day)

    @staticmethod
    def create_filter(field_name, operator, value):
        assert operator in ['lt', 'lte', 'gt', 'gte', 'eq', 'in']
        return f'{field_name}:{operator}:{value}'

    # Internal Functions
    def _send_request(self, fields, filters, page_size=1000):
        req_str = self._create_request_str(fields=fields, filters=filters, page_size=page_size)

        data = None
        if self._from_cache:
            data = self._load_data_from_cache(req_str)

        if data is None:
            print('Requesting Data from Treasury API')
            data = requests.get(req_str).json()

            # Add API Usage data
            data['api_usage_info'] = {}
            data['api_usage_info']['fields'] = fields
            data['api_usage_info']['filters'] = filters
            data['api_usage_info']['request_str'] = req_str
            data['api_usage_info']['request_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self._save_to_cache(req_str, data)

        return data

    def _create_request_str(self, fields, filters, page_size):
        base_str = f'{self.base_url}/'
        base_str += f'{self.endpoint}'
        base_str += f'{self._add_fields(fields)}'

        if filters is not None:
            base_str += f'&{self._add_filters(filters)}'

        # Add Page Size
        base_str += f', &page[number]=1&page[size]={page_size}'
        return base_str

    @staticmethod
    def _add_fields(fields):
        _base_str = '?fields='
        for field in fields:
            _base_str += f'{field},'
        return _base_str[:-1]

    @staticmethod
    def _add_filters(filters):
        _base_str = 'filter='
        for field in filters:
            _base_str += f'{field},'
        return _base_str[:-1]

    def _format_data(self, raw_data):

        df = pd.DataFrame(raw_data['data'])

        for i, col in enumerate(df.columns):
            data_type = raw_data['meta']['dataTypes'][col]

            if col == 'record_date':
                assert raw_data['meta']['dataFormats'][col] == 'YYYY-MM-DD'
                df['record_date'] = pd.to_datetime(df['record_date'], format='%Y-%m-%d')

            elif data_type == 'CURRENCY':
                multiplier = 1
                # Handle Columns that are expressed in Millions, e.g. [Debt Held by the Public (in Millions)]
                if '_mil_' in col:
                    multiplier = 1e6
                df[col] = pd.to_numeric(df[col], errors='coerce') * multiplier

            elif data_type == 'PERCENTAGE':
                df[col] = pd.to_numeric(df[col], errors='coerce') / 100

            elif data_type == 'NUMBER':
                df[col] = pd.to_numeric(df[col], errors='coerce')

            elif data_type == 'STRING':
                continue

            else:
                raise NotImplementedError

        df = df.rename(columns={'record_date': self.date_col_name})
        return df


if __name__ == '__main__':
    treasury_api = TreasuryAPI(endpoint='v1/accounting/od/rates_of_exchange', default_fields=[])

    _fields = ['country_currency_desc', 'exchange_rate', 'record_date']
    _filters = [treasury_api.create_filter(field_name='record_date', operator='gte', value='2015-01-01')]
    treasury_api.send_request(fields=_fields, filters=_filters)
