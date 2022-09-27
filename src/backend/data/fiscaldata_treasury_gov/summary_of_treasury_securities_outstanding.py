import datetime

from src.backend.data.fiscaldata_treasury_gov.treasury_api import TreasuryAPI


class SummaryOfTreasurySecuritiesOutstanding(TreasuryAPI):
    """
    A class to interact with Summary Of Treasury Securities Outstanding

    Ref: https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/summary-of-treasury-securities-outstanding

        available_fields = ['record_date',
                            'security_type_desc',
                            'security_class_desc',
                            'debt_held_public_mil_amt',
                            'intragov_hold_mil_amt',
                            'total_mil_amt']

        Updated: Monthly

    """

    def __init__(self):
        _default_fields = ['record_date',
                           'security_class_desc',
                           'debt_held_public_mil_amt',
                           'intragov_hold_mil_amt',
                           'total_mil_amt']

        _end_point = 'v1/debt/mspd/mspd_table_1'

        super().__init__(endpoint=_end_point,
                         default_fields=_default_fields)

    def print_list_of_security_class_desc(self):
        start_date = datetime.datetime(year=2021, month=1, day=1)
        end_date = datetime.datetime.now()

        data = self.get_all_data_between_dates(start_date=start_date, end_date=end_date)

        for security_desc in data['security_class_desc'].unique():
            print(security_desc)

    def get_security_data_between_dates(self, start_date, end_date, security_desc):
        return self.get_col_data_between_dates(start_date=start_date,
                                               end_date=end_date,
                                               search_column='security_class_desc',
                                               search_str=security_desc)


if __name__ == '__main__':
    sotso = SummaryOfTreasurySecuritiesOutstanding()

    _start_date = datetime.datetime(year=1990, month=1, day=1)
    _end_date = datetime.datetime(year=2022, month=9, day=1)

    sotso.print_list_of_security_class_desc()

    # Plot the historical summary of treasury securities outstanding
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
    for sec in ['Bills', 'Notes', 'Bonds',
                'Treasury Inflation-Protected Securities', 'Floating Rate Notes', 'Federal Financing Bank']:

        _data = sotso.get_security_data_between_dates(start_date=_start_date,
                                                      end_date=_end_date,
                                                      security_desc=sec)

        axes[0].plot(_data['date'], _data['debt_held_public_mil_amt'], label=sec)
        axes[1].plot(_data['date'], _data['intragov_hold_mil_amt'], label=sec)
        axes[2].plot(_data['date'], _data['total_mil_amt'], label=sec)

    axes[0].set_title('Public Debt Held')
    axes[1].set_title('Intragov Hold')
    axes[2].set_title('Total')

    axes[0].legend()
    axes[1].legend()
    axes[2].legend()

    plt.show()
