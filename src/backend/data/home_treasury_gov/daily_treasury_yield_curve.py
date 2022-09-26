import datetime

import pandas as pd
from src.backend.data.api_base import DataAPIBase


class DailyTreasuryYieldCurve(DataAPIBase):

    def __init__(self):
        super().__init__()

    def get_all_data_between_dates(self, start_date, end_date):
        return self._request_data(start_date, end_date)

    def get_col_data_between_dates(self, start_date, end_date, search_column, search_str):
        data = self.get_all_data_between_dates(start_date=start_date, end_date=end_date)
        assert search_str in data[search_column].unique()
        return data[data[search_column] == search_str].reset_index(drop=True)

    def get_yield_curve_for_date(self, date):

        df = self.get_all_data_between_dates(start_date=dtyc.create_date(year=date.year,
                                                                         month=date.month,
                                                                         day=date.day),
                                             end_date=dtyc.create_date(year=date.year,
                                                                       month=date.month,
                                                                       day=date.day))

        # Isolate day and transpose dataframe
        df = df.loc[df['Date'] == datetime.datetime(year=date.year, month=date.month, day=date.day)]
        df = df.drop(columns=['Date'])
        df = df.transpose()
        df.columns = ['Yield (%)']

        # Add column for maturity in days
        for i, row in df.iterrows():
            num = int(i.split(' ')[0])

            if 'Mo' in i:
                days = num * 30
            elif 'Yr' in i:
                days = num * 365
            else:
                raise ValueError(f'Unknown date format: {i}')
            df.loc[i, 'Days'] = days

        df = df[['Days', 'Yield (%)']]
        df = df.reset_index(drop=False)
        df = df.rename(columns={'index': 'Maturity'})
        return df

    def _request_data(self, start_date, end_date):
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
            df = self._load_data_from_cache(unique_str)

        if df is None:
            print(f'Requesting data from treasury.gov for {year}')
            df = pd.read_csv('https://home.treasury.gov/resource-center/data-chart-center/interest-rates/'
                             'daily-treasury-rates.csv/'
                             f'{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv')
            self._save_to_cache(unique_str=unique_str, data=df)

        df = self.format_data(df)

        return df

    @staticmethod
    def format_data(df):
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        return df


if __name__ == '__main__':
    dtyc = DailyTreasuryYieldCurve()

    all_data = dtyc.get_all_data_between_dates(start_date=dtyc.create_date(year=2021, month=1, day=1),
                                               end_date=dtyc.create_date(year=2022, month=1, day=1))

    import matplotlib.pyplot as plt

    # # Plot Historical Yield Data
    # plt.plot(all_data['Date'], all_data['1 Yr'])
    # plt.plot(all_data['Date'], all_data['2 Yr'])
    # plt.plot(all_data['Date'], all_data['5 Yr'])
    # plt.plot(all_data['Date'], all_data['10 Yr'])
    # plt.plot(all_data['Date'], all_data['30 Yr'])
    # plt.show()

    # Plot the Yield Curve for 26/09/2022
    yc_data = dtyc.get_yield_curve_for_date(date=datetime.datetime(year=2022, month=9, day=26))
    print(yc_data)
    plt.plot(yc_data['Days'], yc_data['Yield (%)'])
    plt.show()
