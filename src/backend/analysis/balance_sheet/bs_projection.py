import datetime

import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter
from src.backend.analysis.balance_sheet.bs_historical import BalanceSheetHistorical
from src.backend.analysis.forecasting.interest_rate_forecasts import InterestRateForecaster


class BalanceSheetFuture:
    def __init__(self, balance_sheet_historical, interest_rate_forecaster):
        self.bs_historical = balance_sheet_historical
        self.irf = interest_rate_forecaster

        self.debt_list = self.bs_historical.debt_list
        self.debt_dict = dict()
        for debt_type in self.debt_list:
            print(debt_type)
            self.debt_dict[debt_type] = dict()
            self.debt_dict[debt_type]['AvgInterestCalculator'] = self.irf.forecast_dict[debt_type]

        self.new_issuance = NewIssuanceCalculator(debt_list=self.debt_list)
        self.fiscal_calc = FiscalCalculator()

        self.df = self.bs_historical.df.tail(1).reset_index(drop=True)

        end_date = irf.bills.end_date

        new_date = datetime.datetime.today() + datetime.timedelta(days=1)

        while new_date < end_date:
            self.add_date(new_date)
            new_date += datetime.timedelta(days=31)

        self.df.to_csv('test.csv')

    def add_date(self, date):
        _row = dict()

        _row['date'] = date

        # Calculate Annual Deficit
        tax_receipts = self.fiscal_calc.get_tax_receipts(date=date)
        gov_spend_no_interest = self.fiscal_calc.get_gov_spending_no_interest(date=date)
        annual_deficit_no_interest = (tax_receipts - gov_spend_no_interest) * -1  # -1 to invert
        monthly_interest = self.df.iloc[-1]['monthly_interest']
        annual_interest = monthly_interest * 12
        annual_deficit_w_interest = annual_deficit_no_interest + annual_interest

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

            interest_rate = self.debt_dict[debt_type]['AvgInterestCalculator'].sample(list_of_dates=[date])[0]
            total_debt = new_issuance_amount + self.df.iloc[-1][f'total_debt_{debt_type}']
            monthly_interest = self.calc_monthly_interest(avg_rate=interest_rate,
                                                          debt_amt=total_debt)

            new_total_debt += total_debt
            new_monthly_interest += monthly_interest

            _row[f'new_issuance_split_{debt_type}'] = new_issuance_split
            _row[f'new_issuance_amount_{debt_type}'] = new_issuance_amount
            _row[f'total_debt_{debt_type}'] = total_debt
            _row[f'avg_interest_rate_{debt_type}'] = interest_rate
            _row[f'monthly_interest_{debt_type}'] = monthly_interest

        _row['total_debt'] = new_total_debt
        _row['monthly_interest'] = new_monthly_interest

        _row = pd.DataFrame(_row, index=[1])

        self.df = pd.concat([self.df, _row], axis=0, ignore_index=True)

    @staticmethod
    def calc_monthly_interest(avg_rate, debt_amt):
        return avg_rate / 12 * debt_amt


class BalanceSheetCombine:
    def __init__(self, interest_rate_forecaster):
        self.bs_historical = BalanceSheetHistorical()
        self.bs_future = BalanceSheetFuture(balance_sheet_historical=self.bs_historical,
                                            interest_rate_forecaster=interest_rate_forecaster)
        self.plot_results()

    def plot_results(self):
        fig, axes = plt.subplots(3, 2, figsize=(15, 10), dpi=150)

        self.plot_projection_vlines(axes)
        self.plot_interest_rates(ax=axes[0, 0])
        self.plot_monthly_interest(ax=axes[1, 0])
        self.plot_total_debt(ax=axes[2, 0])

        self.plot_annual_deficit(ax=axes[1, 1])

        fig.show()
        plt.pause(0.1)
        fig.waitforbuttonpress()

    def plot_interest_rates(self, ax):
        self._plot_multi_col(ax=ax, col='avg_interest_rate')
        ax.yaxis.set_major_formatter(FuncFormatter(percent))

    def plot_monthly_interest(self, ax):
        self._plot_multi_col(ax=ax, col='monthly_interest')
        ax.yaxis.set_major_formatter(FuncFormatter(billions))

    def plot_total_debt(self, ax):
        self._plot_multi_col(ax=ax, col='total_debt')
        ax.yaxis.set_major_formatter(FuncFormatter(trillions))

    def plot_annual_deficit(self, ax):
        ax.plot(self.bs_future.df['date'], self.bs_future.df['annual_deficit_w_interest'], linestyle='--',)
        ax.yaxis.set_major_formatter(FuncFormatter(trillions))

    def plot_projection_vlines(self, axes):
        for ax in axes.flatten():
            ax.axvline(x=self.bs_historical.df['date'].iloc[-1], c='grey', linestyle='--', linewidth=1)
            ax.grid(True)
            ax.yaxis.grid(True, which='minor', linestyle='--')

    def _plot_multi_col(self, ax, col):
        for debt_type in self.bs_future.debt_list:
            self._plot_col(ax=ax, col=f'{col}_{debt_type}', label=debt_type)
        ax.legend()

    def _plot_col(self, ax, col, label):
        p = ax.plot(self.bs_historical.df['date'], self.bs_historical.df[col], label=label)
        ax.plot(self.bs_future.df['date'], self.bs_future.df[col], linestyle='--', c=p[0].get_color())


def percent(x, pos):
    """The two args are the value and tick position"""
    # return '%1.2f' % (x * 1e2)
    return f'{x * 1e2:.2f}%'


def millions(x, pos):
    """The two args are the value and tick position"""
    return '%1.1fM' % (x * 1e-6)


def billions(x, pos):
    """The two args are the value and tick position"""
    return '%1.1fB' % (x * 1e-9)


def trillions(x, pos):
    """The two args are the value and tick position"""
    return '%1.1fT' % (x * 1e-12)


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


if __name__ == '__main__':

    scenario = 'Scenario 1'
    # scenario = None
    irf = InterestRateForecaster(load_scenario=scenario)

    BalanceSheetCombine(interest_rate_forecaster=irf)
