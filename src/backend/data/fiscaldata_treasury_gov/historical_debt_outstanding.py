import datetime

from src.backend.data.fiscaldata_treasury_gov.treasury_api import TreasuryAPI


class HistoricalDebtOutstanding(TreasuryAPI):

    """
    A class to interact with Historical Debt Outstanding.

    Ref: https://fiscaldata.treasury.gov/datasets/historical-debt-outstanding/historical-debt-outstanding

        available_fields = ['record_date',
                        'debt_outstanding_amt',
                        'src_line_nbr',
                        'record_fiscal_year',
                        'record_fiscal_quarter']

        Updated: Annually

    """

    def __init__(self):

        _default_fields = ['record_date',
                           'debt_outstanding_amt']

        _end_point = 'v2/accounting/od/debt_outstanding'

        super().__init__(endpoint=_end_point,
                         default_fields=_default_fields)


if __name__ == '__main__':
    hist_debt = HistoricalDebtOutstanding()

    start_date = datetime.datetime(year=2017, month=1, day=1)
    end_date = datetime.datetime(year=2022, month=9, day=1)

    data = hist_debt.get_all_data_between_dates(start_date=start_date, end_date=end_date)
    