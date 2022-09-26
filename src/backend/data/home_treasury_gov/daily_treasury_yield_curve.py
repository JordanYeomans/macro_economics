import pandas as pd
from src.backend.data.api_base import DataAPIBase


class DailyTreasuryYieldCurve(DataAPIBase):

    def __init__(self):
        super().__init__()

    def get_all_data_between_dates(self, start_date, end_date):
        pass

    def get_col_data_between_dates(self, start_date, end_date, search_column, search_str):
        pass

    def request_data(self, start_date, end_date):
        min_year = start_date.year
        max_year = end_date.year

        _all_df = list()
        for year in range(min_year, max_year + 1):
            _df = self._request_data_for_year(year)
            _all_df.append(_df)
        _all_df = pd.concat(_all_df, axis=0).reset_index(drop=True)
        _all_df = _all_df.sort_values(by='Date', ascending=True).reset_index(drop=True)
        return _all_df

    def _request_data_for_year(self, year):

        unique_str = f'DailyTreasuryYieldCurve{year}'

        df = None
        if self._from_cache:
            df = self._load_data_from_cache(unique_str, filetype='csv')

        if df is None:
            print(f'Requesting data from treasury.gov for {year}')
            df = pd.read_csv('https://home.treasury.gov/resource-center/data-chart-center/interest-rates/'
                             'daily-treasury-rates.csv/'
                             f'{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv')
            self._save_to_cache(unique_str=unique_str, data=df, filetype='csv')

        df = self.format_data(df)

        return df

    @staticmethod
    def format_data(df):
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        return df


if __name__ == '__main__':
    dtyc = DailyTreasuryYieldCurve()

    start_date = dtyc.create_date(year=2000, month=1, day=1)
    end_date = dtyc.create_date(year=2022, month=1, day=1)

    data = dtyc.request_data(start_date, end_date)

    import matplotlib.pyplot as plt

    # Plot Historical Yield Data
    plt.plot(data['Date'], data['1 Yr'])
    plt.plot(data['Date'], data['2 Yr'])
    plt.plot(data['Date'], data['5 Yr'])
    plt.plot(data['Date'], data['10 Yr'])
    plt.plot(data['Date'], data['30 Yr'])

    # Plot the Yield Curve for 26/09/2022
    data = data.loc[data['Date'] == '2022-09-26']
    data = data.drop(columns=['Date'])
    data = data.transpose()

    plt.plot(data)
    plt.show()