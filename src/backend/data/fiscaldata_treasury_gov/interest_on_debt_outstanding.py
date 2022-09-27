import datetime

import matplotlib.pyplot as plt

from src.backend.data.fiscaldata_treasury_gov.treasury_api import TreasuryAPI


class InterestOnDebtOutstanding(TreasuryAPI):
    """
    A class to interact with Debt To The Penny

    Ref: https://fiscaldata.treasury.gov/datasets/interest-expense-debt-outstanding/interest-expense-on-the-public-debt-outstanding

        available_fields = ['record_date',
                            'expense_catg_desc',
                            'expense_group_desc',
                            'expense_type_desc',
                            'month_expense_amt',
                            'fytd_expense_amt',
                            ]

        Updated: Monthly

    """

    def __init__(self):
        _default_fields = ['record_date',
                           'expense_catg_desc',
                           'expense_group_desc',
                           'expense_type_desc',
                           'month_expense_amt',
                           'fytd_expense_amt'
                           ]

        _end_point = 'v2/accounting/od/interest_expense'

        super().__init__(endpoint=_end_point,
                         default_fields=_default_fields)

    def print_list_of_expense_type_desc(self):
        start_date = datetime.datetime.now() - datetime.timedelta(days=60)
        end_date = datetime.datetime.now()

        data = self.get_all_data_between_dates(start_date=start_date, end_date=end_date)

        for security_desc in sorted(data['expense_type_desc'].unique()):
            print(f'\t {security_desc}')

    def get_expense_type_data_between_dates(self, start_date, end_date, expense_type_desc):
        data = self.get_all_data_between_dates(start_date=start_date,
                                                end_date=end_date)

        assert expense_type_desc in data['expense_type_desc'].unique()

        data = data[data['expense_type_desc'] == expense_type_desc]
        data = data.drop(columns=['expense_group_desc', 'expense_type_desc'])  # Drop columns that aren't needed
        group_data = data.groupby(['expense_catg_desc', 'date']).sum()
        flat_data = group_data.reset_index()
        assert len(flat_data['expense_catg_desc'].unique()) == 1
        flat_data = flat_data.drop(columns=['expense_catg_desc'])
        return flat_data


if __name__ == '__main__':

    iodo = InterestOnDebtOutstanding()

    _start_date = datetime.datetime(year=2000, month=1, day=1)
    _end_date = datetime.datetime(year=2022, month=9, day=1)

    iodo.print_list_of_expense_type_desc()
    _data = iodo.get_expense_type_data_between_dates(start_date=_start_date,
                                                     end_date=_end_date,
                                                     expense_type_desc='Treasury Bonds')

    plt.subplot(2, 1, 1)
    plt.plot(_data['date'], _data['month_expense_amt'])
    plt.title('Month Expense Amount')
    plt.subplot(2, 1, 2)
    plt.plot(_data['date'], _data['fytd_expense_amt'])
    plt.title('FYTD Expense Amount')
    plt.show()
