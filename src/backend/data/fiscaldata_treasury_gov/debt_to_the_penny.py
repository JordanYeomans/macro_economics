import datetime

from src.backend.data.fiscaldata_treasury_gov.treasury_api import TreasuryAPI


class DebtToThePenny(TreasuryAPI):
    """
    A class to interact with Debt To The Penny

    Ref: https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/debt-to-the-penny

        available_fields = ['record_date',
                            'debt_held_public_amt',
                            'intragov_hold_amt',
                            'tot_pub_debt_out_amt',
                            'src_line_nbr']

        Updated: Daily

    """

    def __init__(self):
        _default_fields = ['record_date',
                           'debt_held_public_amt',
                           'intragov_hold_amt',
                           'tot_pub_debt_out_amt']

        _end_point = 'v2/accounting/od/debt_to_penny'

        super().__init__(endpoint=_end_point,
                         default_fields=_default_fields)


if __name__ == '__main__':
    debt_to_penny = DebtToThePenny()

    start_date = datetime.datetime(year=1990, month=1, day=1)
    end_date = datetime.datetime(year=2022, month=9, day=1)

    data = debt_to_penny.get_all_data_between_dates(start_date=start_date, end_date=end_date, save_to_json=True)

    import matplotlib.pyplot as plt
    plt.plot(data['record_date'], data['debt_held_public_amt'])
    plt.plot(data['record_date'], data['intragov_hold_amt'])
    plt.plot(data['record_date'], data['tot_pub_debt_out_amt'])
    plt.show()
