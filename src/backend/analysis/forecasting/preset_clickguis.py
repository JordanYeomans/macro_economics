import datetime

from src.backend.analysis.balance_sheet_projection import BalanceSheetHistorical
from src.backend.analysis.forecasting.clickable_gui import ClickableCalculator, ClickableFig

bsh = BalanceSheetHistorical()


class ClickableGUiAvgInterestRateBills(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_bills']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.0 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=0.25 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3.0 * 365), val=0.5 / 100)
        self.run()


class ClickableGUiAvgInterestRateNotes(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_notes']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=2.1 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=2.5 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=2.8 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.6 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.4 / 100)


class ClickableGUiAvgInterestRateBonds(ClickableCalculator):
    def __init__(self):
        super().__init__(df=bsh.df[['date', 'avg_interest_rate_bonds']])
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.1 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.2 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=3.4 / 100)
        self.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=3.8 / 100)


if __name__ == '__main__':

    multi_cgui = ClickableFig(list_of_calculators=[ClickableGUiAvgInterestRateBills(),
                                                   ClickableGUiAvgInterestRateNotes(),
                                                   ClickableGUiAvgInterestRateBonds()], load_scenario=None)
