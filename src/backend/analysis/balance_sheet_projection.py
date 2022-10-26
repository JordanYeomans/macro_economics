import datetime

import pandas as pd
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

        self._calc_total_debt()
        self._calc_interest()

    def _calc_total_debt(self):
        self._add_columns(df_col_name='total_debt')

    def _calc_interest(self):
        self._add_columns(df_col_name='monthly_interest')

    def _add_columns(self, df_col_name):
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

        self.df = self.bs_historical.df.tail(1).reset_index(drop=True)
        self.add_date(date=datetime.datetime.today() + datetime.timedelta(days=365.25 / 2))
        self.add_date(date=datetime.datetime.today() + datetime.timedelta(days=365.25))

        self.df.to_csv('test.csv')

    def add_date(self, date):
        _row = dict()

        date = date.date()
        _row['date'] = date

        # Calculate Annual Deficit
        tax_receipts = self.fiscal_calc.get_tax_receipts(date=date)
        gov_spend_no_interest = self.fiscal_calc.get_gov_spending_no_interest(date=date)
        annual_deficit_no_interest = (tax_receipts - gov_spend_no_interest) * -1  # -1 to invert
        annual_deficit_w_interest = annual_deficit_no_interest + self.df.iloc[-1]['monthly_interest']

        _row['tax_receipts'] = tax_receipts
        _row['gov_spending_no_interest'] = gov_spend_no_interest
        _row['annual_deficit_no_interest'] = annual_deficit_no_interest
        _row['annual_deficit_w_interest'] = annual_deficit_w_interest

        # Calculate New Issuance (based on number of days between rows)
        days_between_rows = (date - self.df.iloc[-1]['date']).days
        new_issuance = days_between_rows / 365.25 * annual_deficit_w_interest
        _row['new_issuance'] = new_issuance

        new_total_debt = 0
        new_monthly_interest = 0
        for debt_type in self.debt_dict:
            new_issuance_split = self.new_issuance.get_issuance_split(debt_type=debt_type)
            new_issuance_amount = new_issuance * new_issuance_split

            interest_rate = self.debt_dict[debt_type]['AvgInterestCalculator'].get_interest_rate_for_date(date=date)
            total_debt = new_issuance_amount + self.df.iloc[-1][f'total_debt_{debt_type}']
            monthly_interest = self.calc_monthly_interest(avg_rate=interest_rate,
                                                          debt_amt=total_debt)

            new_total_debt += total_debt
            new_monthly_interest += monthly_interest

            _row[f'new_issuance_split_{debt_type}'] = new_issuance_split
            _row[f'new_issuance_amount_{debt_type}'] = new_issuance_amount
            _row[f'total_debt_{debt_type}'] = total_debt
            _row[f'avg_interest_rate_{debt_type}'] = interest_rate
            _row[f'monthly_interest__{debt_type}'] = monthly_interest

        _row['total_debt'] = new_total_debt
        _row['monthly_interest'] = new_monthly_interest

        _row = pd.DataFrame(_row, index=[1])

        self.df = pd.concat([self.df, _row], axis=0, ignore_index=True)

    @staticmethod
    def calc_monthly_interest(avg_rate, debt_amt):
        return avg_rate / 12 * debt_amt


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
        return 5.5e12

    def get_tax_receipts(self, date):
        return 4.5e12


def rename_debt_type(debt_type):
    return debt_type.lower().replace('-', '')[1:]


if __name__ == '__main__':
    balance_sheet_historical = BalanceSheetHistorical().df.to_csv('balance_sheet_historical.csv')
    BalanceSheetCombine()
