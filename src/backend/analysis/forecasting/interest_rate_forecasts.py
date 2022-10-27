import datetime

from src.backend.analysis.balance_sheet.bs_historical import BalanceSheetHistorical
from src.backend.analysis.forecasting.clickable_gui import ClickableCalculator, ClickableFig

bsh = BalanceSheetHistorical()


class ForecastAvgInterestRateBills(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_bills']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.0 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3.0 * 365), val=0.5 / 100)
        self.run()


class ForecastAvgInterestRateNotes(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_notes']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=2.1 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=2.5 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=2.8 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.6 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.4 / 100)
        self.run()


class ForecastAvgInterestRateBonds(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_bonds']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.1 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.2 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=3.4 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=3.8 / 100)
        self.run()


class InterestRateForecaster:
    def __init__(self, load_scenario=None):

        self._bills = ForecastAvgInterestRateBills()
        self._notes = ForecastAvgInterestRateNotes()
        self._bonds = ForecastAvgInterestRateBonds()

        list_of_calculators = [self._bills, self._notes, self._bonds]

        ClickableFig(list_of_calculators=list_of_calculators,
                     load_scenario=load_scenario)

    @property
    def forecast_dict(self):
        return {'bills': self.bills,
                'notes': self.notes,
                'bonds': self.bonds}

    @property
    def bills(self):
        return self._bills

    @property
    def notes(self):
        return self._notes

    @property
    def bonds(self):
        return self._bonds


if __name__ == '__main__':

    irf = InterestRateForecaster(load_scenario='Scenario 1')

    # 3. Example how to sample data from a ClickableGui
    sample_dates = [datetime.datetime.now() + datetime.timedelta(days=x) for x in range(0, 365 * 3, 1)]
    sample_vals = irf.bills.sample(list_of_dates=sample_dates)

    import matplotlib.pyplot as plt
    plt.plot(sample_dates, sample_vals, linestyle='-', c='black')
    plt.show()
