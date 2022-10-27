from src.backend.analysis.debt_type_summary import DebtTypeSummary
from src.backend.analysis.balance_sheet.functions import rename_debt_type


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
