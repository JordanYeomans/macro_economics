import datetime

from src.backend.data.fiscaldata_treasury_gov.treasury_api import TreasuryAPI


class AvgInterestRates(TreasuryAPI):
    """
    A class to interact with Debt To The Penny

    Ref: https://fiscaldata.treasury.gov/datasets/average-interest-rates-treasury-securities/average-interest-rates-on-u-s-treasury-securities

        available_fields = ['record_date',
                            'security_type_desc',
                            'security_desc',
                            'avg_interest_rate_amt',
                            'src_line_nbr']

        Updated: Monthly

    """

    def __init__(self):
        _default_fields = ['record_date',
                           'security_desc',
                           'avg_interest_rate_amt']

        _end_point = 'v2/accounting/od/avg_interest_rates'

        super().__init__(endpoint=_end_point,
                         default_fields=_default_fields)

    def print_list_of_security_desc(self):
        start_date = datetime.datetime(year=2021, month=1, day=1)
        end_date = datetime.datetime.now()

        data = self.get_all_data_between_dates(start_date=start_date, end_date=end_date)

        for security_desc in data['security_desc'].unique():
            print(security_desc)

    def get_security_data_between_dates(self, start_date, end_date, security_desc):
        return self.get_col_data_between_dates(start_date=start_date,
                                               end_date=end_date,
                                               search_column='security_desc',
                                               search_str=security_desc)


if __name__ == '__main__':
    avg_interest_rates = AvgInterestRates()

    _start_date = datetime.datetime(year=2021, month=1, day=1)
    _end_date = datetime.datetime(year=2022, month=9, day=1)

    avg_interest_rates.print_list_of_security_desc()
    _data = avg_interest_rates.get_security_data_between_dates(start_date=_start_date,
                                                               end_date=_end_date,
                                                               security_desc='Treasury Bills')
