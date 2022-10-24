import time
import scipy
import datetime

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from src.backend.analysis.balance_sheet_projection import BalanceSheetHistorical


class ClickableFig:

    def __init__(self, list_of_calculators):

        # Variables
        epsilon = 25  # Radius limit to select point

        # Setup the Figure
        self.fig, self.axes = plt.subplots(3, 1)

        # Setup plot dict - Used to store the individual calculators and their respective plots
        self.plot_dict = dict()
        for i in range(len(list_of_calculators)):
            self.plot_dict[i] = dict()
            self.plot_dict[i]['calc'] = list_of_calculators[i]
            self.plot_dict[i]['calc'].run()

        # Internal Variables
        self._pind = None  # active point

        # Dynamic plot Functions
        def get_ax_idx(event):

            if event.xdata is None:
                return

            # Identify axis
            ax_idx = None
            for ax_idx, ax_name in enumerate(self.axes):
                if str(ax_name) == str(event.inaxes):
                    break
            return ax_idx

        def reset(event):

            for _i in range(len(list_of_calculators)):
                _calc = self.plot_dict[_i]['calc']
                _calc.reset()

                self.plot_dict[_i]['l'].set_xdata(_calc.xvals)
                self.plot_dict[_i]['l'].set_ydata(_calc.yvals)
                self.plot_dict[_i]['m'].set_ydata(_calc.spline(spline_x))

            self.fig.canvas.draw_idle()

        def button_press_callback(event):
            """whenever a mouse button is pressed"""

            if event.inaxes is None:
                return
            if event.button != 1:
                return

            self._pind = get_ind_under_point(event)

        def button_release_callback(event):
            """whenever a mouse button is released"""

            if event.button != 1:
                return
            self._pind = None

        def get_ind_under_point(event):
            """get the index of the vertex under point if within epsilon tolerance"""
            ax_idx = get_ax_idx(event)
            ax = self.axes[ax_idx]
            _calc = self.plot_dict[ax_idx]['calc']

            xr = np.reshape(_calc.xvals, (np.shape(_calc.xvals)[0], 1))
            yr = np.reshape(_calc.yvals, (np.shape(_calc.yvals)[0], 1))
            xy_vals = np.append(xr, yr, 1)

            tinv = ax.transData
            xyt = tinv.transform(xy_vals)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.hypot(xt - event.x, yt - event.y)
            indseq, = np.nonzero(d == d.min())
            ind = indseq[0]
            if d[ind] >= epsilon:
                ind = None

            return ind

        def motion_notify_callback(event):
            """ on mouse movement """
            start_time = time.time()
            ax_idx = get_ax_idx(event)
            if ax_idx is None:
                return

            if self._pind is None:
                return
            if event.inaxes is None:
                return
            if event.button != 1:
                return

            # Retrieve the calculator and lines
            _calc = self.plot_dict[ax_idx]['calc']
            _l = self.plot_dict[ax_idx]['l']
            _m = self.plot_dict[ax_idx]['m']

            # Prevent the first point from being moved, it should be fixed to the end of the previous series
            if self._pind == 0:
                return

            # Prevent the point from being dragged too far left
            if event.xdata <= _calc.xvals[self._pind - 1]:
                return

            # Prevent the point from being dragged too far right
            if self._pind != len(_calc.xvals) - 1 and event.xdata >= _calc.xvals[self._pind + 1]:
                return

            # Prevent the first or last point being moved left/right
            if self._pind != 0 and self._pind != len(_calc.xvals) - 1:
                # Calculate and plot the x-value
                _calc.xvals[self._pind] = event.xdata
                _l.set_xdata(_calc.xvals)

            # Calculate and plot the y-value
            _calc.yvals[self._pind] = event.ydata
            _l.set_ydata(_calc.yvals)

            # Calculate and plot the spline
            _calc.spline = _calc.create_spline()
            _m.set_ydata(_calc.spline(spline_x))

            self.fig.canvas.draw_idle()

        # create_plots
        for i in range(len(list_of_calculators)):
            ax1 = self.axes[i]
            calc = self.plot_dict[i]['calc']

            spline_intervals = 1000
            spline_x = np.linspace(min(calc.xvals), max(calc.xvals), spline_intervals)

            self.plot_dict[i]['l'],  = ax1.plot(calc.xvals, calc.yvals, color='k', linestyle='none', marker='o', markersize=8)
            self.plot_dict[i]['m'], = ax1.plot(spline_x, calc.spline(spline_x), 'r-', label=f'Future {calc.col}')

            # Set the x-axis to be the dates
            xaxis_min = min(convert_dates_to_floats(calc.df['date']))
            xaxis_max = max(calc.xvals)
            one_yr_ts = datetime.timedelta(days=365.25).total_seconds()  # account for leap years
            xaxis_vals = np.arange(xaxis_min, xaxis_max, one_yr_ts)
            xaxis_labels = [datetime.datetime.fromtimestamp(x).strftime('%d/%m/%Y') for x in xaxis_vals]
            ax1.set_xticks(xaxis_vals, xaxis_labels, rotation=90)

            max_val = np.max([max(calc.spline(spline_x)), max(calc.df[calc.col])])
            min_val = np.min([min(calc.spline(spline_x)), min(calc.yvals), 0])

            print(max_val, min_val)
            ax1.set_ylim(min_val * 1.1, max_val * 1.1)
            ax1.set_ylabel(calc.col)

            # Plot the historical data
            ax1.plot(convert_dates_to_floats(calc.df['date']), calc.df[calc.col])

            ax1.grid(True)
            ax1.yaxis.grid(True, which='minor', linestyle='--')
            ax1.legend(loc=2, prop={'size': 12})

            axres = plt.axes([0.84, 0.9, 0.12, 0.02])  # left, bottom, width, height
            bres = Button(axres, 'Reset')
            bres.on_clicked(reset)

        self.fig.canvas.mpl_connect('button_press_event', button_press_callback)
        self.fig.canvas.mpl_connect('button_release_event', button_release_callback)
        self.fig.canvas.mpl_connect('motion_notify_event', motion_notify_callback)

        plt.show()


class ClickableCalculator:
    def __init__(self, df):
        # Format DF
        self.df = df.reset_index(drop=True)
        assert len(self.df.columns) == 2
        assert 'date' in self.df.columns
        self.col = [x for x in self.df.columns if x != 'date'][0]

        # Init internal variables
        self._list_of_points = list()
        self.xvals = None
        self.yvals = None
        self.spline = None
        self._pind = None  # active point

        # Set Start Point of GUI
        self.start_val = self.df.iloc[-1][self.col]
        self.start_date = self.df.iloc[-1]['date']
        self.add_point(date=self.start_date, val=self.start_val)

    @property
    def list_of_points(self):
        xvals = np.array(self._list_of_points)[:, 0]
        xvals = convert_dates_to_floats(xvals)
        sort_order = np.argsort(xvals, axis=0)
        list_of_points = np.array(self._list_of_points)[sort_order]
        return list(list_of_points)

    def add_point(self, date, val):
        self._list_of_points.append([date, val])

    def create_spline(self):
        return scipy.interpolate.InterpolatedUnivariateSpline(self.xvals, self.yvals)

    def run(self):
        self.reset()

    def reset(self):
        # reset the values
        self.xvals = self._reset_xvals()
        self.yvals = self._reset_yvals()
        self.spline = self.create_spline()

    def _reset_xvals(self):
        xvals = np.array(self.list_of_points)[:, 0]
        xvals = np.array([x.timestamp() for x in xvals])
        xvals = np.array(xvals).astype(float)
        return xvals

    def _reset_yvals(self):
        return np.array(np.array(self.list_of_points)[:, 1]).astype(float)

    def create_plot(self):
        assert len(self.list_of_points) >= 4, 'Must have at least 4 points to create plot, use add_point()'

        self.xvals = self._reset_xvals()
        self.yvals = self._reset_yvals()
        self.spline = self.create_spline()

        # set up a plot
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 8.0))
        plt.subplots_adjust(right=0.95, left=0.07, bottom=0.15)

        self._pind = None  # active point
        epsilon = 25  # max pixel distance

        def reset(event):

            # reset the values
            self.reset()

            l.set_xdata(self.xvals)
            l.set_ydata(self.yvals)
            m.set_ydata(self.spline(spline_x))
            fig.canvas.draw_idle()

        def button_press_callback(event):
            """whenever a mouse button is pressed"""

            if event.inaxes is None:
                return
            if event.button != 1:
                return

            self._pind = get_ind_under_point(event)

        def button_release_callback(event):
            """whenever a mouse button is released"""

            if event.button != 1:
                return
            self._pind = None

        def get_ind_under_point(event):
            """get the index of the vertex under point if within epsilon tolerance"""

            tinv = ax1.transData

            xr = np.reshape(self.xvals, (np.shape(self.xvals)[0], 1))
            yr = np.reshape(self.yvals, (np.shape(self.yvals)[0], 1))
            xy_vals = np.append(xr, yr, 1)
            xyt = tinv.transform(xy_vals)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.hypot(xt - event.x, yt - event.y)
            indseq, = np.nonzero(d == d.min())
            ind = indseq[0]

            if d[ind] >= epsilon:
                ind = None

            return ind

        def motion_notify_callback(event):
            """ on mouse movement """

            if self._pind is None:
                return
            if event.inaxes is None:
                return
            if event.button != 1:
                return

            # You can't select the first point
            if self._pind == 0:
                return

            # Prevent the point from being dragged too far left
            if event.xdata <= self.xvals[self._pind - 1]:
                return

            if self._pind != len(self.xvals) - 1 and event.xdata >= self.xvals[self._pind + 1]:
                return

            if self._pind != 0 and self._pind != len(self.xvals) - 1:
                self.xvals[self._pind] = event.xdata
                l.set_xdata(self.xvals)

            self.yvals[self._pind] = event.ydata
            l.set_ydata(self.yvals)

            self.spline = self.create_spline()
            m.set_ydata(self.spline(spline_x))

            fig.canvas.draw_idle()

        spline_intervals = 1000
        spline_x = np.linspace(min(self.xvals), max(self.xvals), spline_intervals)

        l, = ax1.plot(self.xvals, self.yvals, color='k', linestyle='none', marker='o', markersize=8)
        m, = ax1.plot(spline_x, self.spline(spline_x), 'r-', label=f'Future {self.col}')

        # Set the x-axis to be the dates
        xaxis_min = min(convert_dates_to_floats(self.df['date']))
        xaxis_max = max(self.xvals)
        one_yr_ts = datetime.timedelta(days=365.25).total_seconds()  # account for leap years
        xaxis_vals = np.arange(xaxis_min, xaxis_max, one_yr_ts)
        xaxis_labels = [datetime.datetime.fromtimestamp(x).strftime('%d/%m/%Y') for x in xaxis_vals]
        ax1.set_xticks(xaxis_vals, xaxis_labels, rotation=90)

        ax1.set_ylim(0, max(self.spline(spline_x)) * 1.1)
        ax1.set_ylabel(self.col)

        # Plot the historical data
        ax1.plot(convert_dates_to_floats(self.df['date']), self.df[self.col])

        ax1.grid(True)
        ax1.yaxis.grid(True, which='minor', linestyle='--')
        ax1.legend(loc=2, prop={'size': 12})

        axres = plt.axes([0.84, 0.9, 0.12, 0.02])  # left, bottom, width, height
        bres = Button(axres, 'Reset')
        bres.on_clicked(reset)

        fig.canvas.mpl_connect('button_press_event', button_press_callback)
        fig.canvas.mpl_connect('button_release_event', button_release_callback)
        fig.canvas.mpl_connect('motion_notify_event', motion_notify_callback)

        plt.close()

    def sample_data(self, list_of_dates):
        dates_as_floats = convert_dates_to_floats(list_of_dates)
        assert max(dates_as_floats) <= max(self.xvals), f'Date is too far in the future, max date allowed ' \
                                                        f'= {convert_floats_to_dates(max(self.xvals)).date()}'
        return self.spline(dates_as_floats)


def convert_dates_to_floats(dates):
    return np.array([x.timestamp() for x in dates])


def convert_floats_to_dates(floats):
    # check if floats is a list
    if isinstance(floats, list):
        return np.array([datetime.datetime.fromtimestamp(x) for x in floats])
    # check if floats is a numpy array
    elif isinstance(floats, np.ndarray):
        return np.array([datetime.datetime.fromtimestamp(x) for x in floats])
    else:
        return datetime.datetime.fromtimestamp(floats)


if __name__ == '__main__':
    bsh = BalanceSheetHistorical()

    cgui_1 = ClickableCalculator(df=bsh.df[['date', 'avg_interest_rate_bills']])
    cgui_1.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui_1.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=0.25 / 100)
    cgui_1.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=0.25 / 100)
    cgui_1.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=0.25 / 100)
    cgui_1.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=0.5 / 100)
    # cgui_1.create_plot()

    cgui_2 = ClickableCalculator(df=bsh.df[['date', 'avg_interest_rate_notes']])
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.5 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.25 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.25 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.5 / 100)
    # cgui_2.create_plot()

    cgui_3 = ClickableCalculator(df=bsh.df[['date', 'avg_interest_rate_bonds']])
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.5 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.25 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.25 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.5 / 100)
    # cgui_3.create_plot()

    multi_cgui = ClickableFig(list_of_calculators=[cgui_1, cgui_2, cgui_3])

    # sample_dates = [datetime.datetime.now() + datetime.timedelta(days=x) for x in range(0, 365 * 3, 1)]
    # sample_vals = cgui.sample_data(sample_dates)
    #
    # plt.plot(sample_dates, sample_vals, linestyle='-', c='black')
    # plt.show()
