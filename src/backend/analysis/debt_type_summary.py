import datetime

import pandas as pd
import matplotlib.pyplot as plt

from src.backend.data.debt_column_matching import get_debt_matching_dict
from src.backend.data.fiscaldata_treasury_gov.avg_interest_rates import AvgInterestRates
from src.backend.data.fiscaldata_treasury_gov.summary_of_treasury_securities_outstanding import \
    SummaryOfTreasurySecuritiesOutstanding
from src.backend.data.fiscaldata_treasury_gov.interest_on_debt_outstanding import \
    InterestOnDebtOutstanding


class DebtTypeSummary:

    def __init__(self, debt_type):
        self.start_date = datetime.datetime(year=2010, month=1, day=1)
        self.end_date = datetime.datetime.today()

        self.debt_type = debt_type
        debt_match = get_debt_matching_dict()
        self.hometreasury_desc = debt_match[debt_type]['hometreasury']
        self.fiscaldata_desc = debt_match[debt_type]['fiscaldata']

        self.df = None
        self.air = AvgInterestRates()
        self.iodo = InterestOnDebtOutstanding()
        self.sotso = SummaryOfTreasurySecuritiesOutstanding()

        self.air_df = self.air.get_security_data_between_dates(start_date=self.start_date,
                                                               end_date=self.end_date,
                                                               security_desc=self.fiscaldata_desc)

        self.iodo_df = self.iodo.get_expense_type_data_between_dates(start_date=self.start_date,
                                                                     end_date=self.end_date,
                                                                     expense_type_desc=self.fiscaldata_desc)

        self.sotso_df = self.sotso.get_security_data_between_dates(start_date=self.start_date,
                                                                   end_date=self.end_date,
                                                                   security_desc=self.hometreasury_desc)

        self.combine_data()
        self.estimate_interest()

    # --- Analysis Steps
    def combine_data(self):
        self.df = pd.merge(self.air_df, self.sotso_df, on='date', how='outer')
        self.df = pd.merge(self.df, self.iodo_df, on='date', how='outer')
        self.df = self.df.sort_values(by='date').reset_index(drop=True)

    def estimate_interest(self):
        self.df['est_interest'] = self.df['avg_interest_rate_amt'] * self.df['total_amt'] / 12

    # --- Visualization
    def plot_est_vs_actual_interest(self, plot=False):
        plot_df = self.df[~self.df['month_expense_amt'].isna()]
        plot_df = plot_df[['date', 'est_interest', 'month_expense_amt']]
        if plot:
            fig, ax = plt.subplots(1, 2, figsize=(10, 10))

            fig.suptitle(f'Estimated vs Actual Interest - {self.debt_type}', fontsize=16)
            ax[0].plot(plot_df['date'], plot_df['est_interest'], label='Estimated Interest (Monthly)')
            ax[0].plot(plot_df['date'], plot_df['month_expense_amt'], label='Actual Interest (Monthly')

            ax[1].plot(plot_df['date'], plot_df['est_interest'].cumsum(), label='Estimated Interest Cumulative')
            ax[1].plot(plot_df['date'], plot_df['month_expense_amt'].cumsum(), label='Actual Interest Cumulative')

            ax[0].legend()
            ax[1].legend()
            plt.show()

        return plot_df


if __name__ == '__main__':
    debt_summary = DebtTypeSummary(debt_type='T-Bills')
    _plot_df = debt_summary.plot_est_vs_actual_interest(plot=True)
