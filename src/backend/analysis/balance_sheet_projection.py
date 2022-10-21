import datetime

import matplotlib.pyplot as plt

from src.backend.analysis.debt_type_summary import DebtTypeSummary


class BalanceSheetHistorical:

    def __init__(self):

        self.debt_list = ['T-Bonds', 'T-Notes', 'T-Bills']

        self.df = None
        for debt_type in self.debt_list:
            debt_info_df = self.get_debt_info_for_type(debt_type=debt_type)
            if self.df is None:
                self.df = debt_info_df
            else:
                self.df = self.df.merge(debt_info_df, on='date', how='inner')

        # Update debt list with new names
        for i, debt_type in enumerate(self.debt_list):
            self.debt_list[i] = rename_debt_type(debt_type=debt_type)

        self.add_total_debt()
        self.add_interest()

        # fig, axes = plt.subplots(1, 2)
        #
        # ax = axes[0]
        # ax.plot(self.df[f'total_debt_bills'], label='bills')
        # ax.plot(self.df[f'total_debt_notes'], label='notes')
        # ax.plot(self.df[f'total_debt_bonds'], label='bonds')
        # ax.plot(self.df['total_debt'], label='total')
        # ax.legend()
        #
        # ax = axes[1]
        # ax.plot(self.df[f'monthly_interest_bills'], label='bills')
        # ax.plot(self.df[f'monthly_interest_notes'], label='notes')
        # ax.plot(self.df[f'monthly_interest_bonds'], label='bonds')
        # ax.plot(self.df['monthly_interest'], label='total')
        # ax.legend()
        #
        # plt.show()

    def add_total_debt(self):
        self.add_columns(df_col_name='total_debt')

    def add_interest(self):
        self.add_columns(df_col_name='monthly_interest')

    def add_columns(self, df_col_name):
        list_of_cols = list()
        for debt_type in self.debt_list:
            list_of_cols.append(f'{df_col_name}_{debt_type}')
        self.df[df_col_name] = self.df[list_of_cols].sum(axis=1)

    @staticmethod
    def get_debt_info_for_type(debt_type):
        pi = DebtTypeSummary(debt_type=debt_type)

        keep_cols = ['date', 'avg_interest_rate_amt', 'total_amt', 'est_interest']

        pi.df = pi.df[keep_cols]
        pi.df = pi.df.rename(columns={'avg_interest_rate_amt': 'avg_interest_rate',
                                      'total_amt': 'total_debt',
                                      'est_interest': 'monthly_interest'})

        for col in pi.df.columns:
            if 'date' in col:
                continue
            new_col = col + '_' + rename_debt_type(debt_type=debt_type)
            pi.df.rename(columns={col: new_col}, inplace=True)

        return pi.df


class BalanceSheetFuture:
    def __init__(self, bs_historical):
        self.bs_historical = bs_historical
        self.debt_list = self.bs_historical.debt_list
        self.debt_dict = dict()
        for debt_type in self.debt_list:
            self.debt_dict[debt_type] = dict()

            # Add Interest Rate Calculator
            start_rate = self.bs_historical.df.iloc[-1][f'avg_interest_rate_{debt_type}']
            self.debt_dict[debt_type]['AvgInterestCalculator'] = AvgInterestRateCalculator(start_rate=start_rate)

        self.new_issuance = NewIssuanceCalculator(debt_list=self.debt_list)
        self.fiscal_calc = FiscalCalculator()

        self.df = self.bs_historical.df.iloc[-1]

        self.add_date(date=datetime.datetime.today() + datetime.timedelta(days=100))

    def add_date(self, date):
        print(date)
        new_row = self.df.keys()
        print(new_row)

        new_row_dict = dict()
        new_row_dict['date'] = date.date()

        for debt_type in self.debt_dict:
            # Sample Interest Rates
            interest_rate = self.debt_dict[debt_type]['AvgInterestCalculator'].get_interest_rate_for_date(date=date)
            monthly_interest = self.calc_monthly_interest(avg_rate=interest_rate,
                                                          debt_amt=self.df.iloc[-1][f'total_debt_{debt_type}'])

            new_row_dict[f'avg_interest_rate_{debt_type}'] = interest_rate
            new_row_dict[f'monthly_interest_{debt_type}'] = monthly_interest

            # Sample New Issuance
            new_issuance_split = self.new_issuance.get_issuance_split(debt_type=debt_type)
            new_row_dict[f'new_issuance_split_{debt_type}'] = new_issuance_split

        new_row_dict['tax_reciepts'] = self.fiscal_calc.get_tax_reciepts(date=date)
        new_row_dict['gov_spending_no_interest'] = self.fiscal_calc.get_gov_spending_no_interest(date=date)

        print(new_row_dict)
        pass

    def calc_monthly_interest(self, avg_rate, debt_amt):
        return avg_rate * debt_amt


class BalanceSheetCombine:
    def __init__(self):
        self.bs_historical = BalanceSheetHistorical()

        self.bs_future = BalanceSheetFuture(self.bs_historical)


class AvgInterestRateCalculator:
    def __init__(self, start_rate):
        self._start_rate = start_rate

    def get_interest_rate_for_date(self, date):
        return self._start_rate


class NewIssuanceCalculator:
    def __init__(self, debt_list):
        self.debt_issuance_dict = dict()

        for debt in debt_list:
            self.debt_issuance_dict[debt] = 1 / len(debt_list)

    def get_issuance_split(self, debt_type):
        assert debt_type in self.debt_issuance_dict, f'debt_type not in {self.debt_issuance_dict}'
        return self.debt_issuance_dict[debt_type]


class FiscalCalculator:
    def __init__(self):
        pass

    def get_gov_spending_no_interest(self, date):
        return -5.5e12

    def get_tax_reciepts(self, date):
        return 4.5e12


def rename_debt_type(debt_type):
    return debt_type.lower().replace('-', '')[1:]


if __name__ == '__main__':
    # balance_sheet_historical = BalanceSheetHistorical()
    BalanceSheetCombine()
