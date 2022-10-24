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
        self.fig, self.axes = plt.subplots(3, 1, figsize=(16, 12), dpi=100)

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
            """ Get the index of the axis that was clicked on """
            ax_idx = None
            for ax_idx, ax_name in enumerate(self.axes):
                if str(ax_name) == str(event.inaxes):
                    break
            return ax_idx

        def reset(event):
            """ Reset the plot if the reset button is clicked """
            for _i in range(len(list_of_calculators)):
                _calc = self.plot_dict[_i]['calc']
                _calc.reset()

                self.plot_dict[_i]['l'].set_xdata(_calc.xvals)
                self.plot_dict[_i]['l'].set_ydata(_calc.yvals)
                self.plot_dict[_i]['m'].set_ydata(_calc.spline(spline_x))

            self.fig.canvas.draw_idle()

        def button_press_callback(event):
            """ When the mouse is clicked assign the _pind"""

            if event.inaxes is None:
                return
            if event.button != 1:
                return

            self._pind = get_ind_under_point(event)

        def button_release_callback(event):
            """ When the mouse is released un-assign the _pind"""

            if event.button != 1:
                return
            self._pind = None

        def get_ind_under_point(event):
            """get the index of the vertex under point if within epsilon tolerance"""
            ax_idx = get_ax_idx(event)
            _ax = self.axes[ax_idx]
            _calc = self.plot_dict[ax_idx]['calc']

            xr = np.reshape(_calc.xvals, (np.shape(_calc.xvals)[0], 1))
            yr = np.reshape(_calc.yvals, (np.shape(_calc.yvals)[0], 1))
            xy_vals = np.append(xr, yr, 1)

            tinv = _ax.transData
            xyt = tinv.transform(xy_vals)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.hypot(xt - event.x, yt - event.y)
            indseq, = np.nonzero(d == d.min())
            ind = indseq[0]
            if d[ind] >= epsilon:
                ind = None
            return ind

        def motion_notify_callback(event):
            """ Move the point under the mouse and update the plot """
            ax_idx = get_ax_idx(event)
            if ax_idx is None or self._pind is None:
                return

            # Retrieve the calculator and lines
            _calc = self.plot_dict[ax_idx]['calc']
            _l = self.plot_dict[ax_idx]['l']
            _m = self.plot_dict[ax_idx]['m']
            _bg = self.plot_dict[ax_idx]['bg']

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

            _ax = self.axes[ax_idx]
            self.fig.canvas.restore_region(_bg)
            _ax.draw_artist(_l)
            _ax.draw_artist(_m)
            self.fig.canvas.blit(_ax.bbox)

        # Create Axes Backgrounds
        for i in range(len(list_of_calculators)):
            ax1 = self.axes[i]
            calc = self.plot_dict[i]['calc']

            spline_intervals = 1000
            spline_x = np.linspace(min(calc.xvals), max(calc.xvals), spline_intervals)
            self.plot_dict[i]['spline_x'] = spline_x

            # Note: This is where we would typical plot the lines. However, we plot them later to allow for the dynamic
            #       plotting of the lines. We need to store a raw background for each axis before adding the lines.

            # Set the x-axis to be the dates
            xaxis_min = min(convert_dates_to_floats(calc.df['date']))
            xaxis_max = max(calc.xvals)
            one_yr_ts = datetime.timedelta(days=365.25).total_seconds()  # account for leap years
            xaxis_vals = np.arange(xaxis_min, xaxis_max, one_yr_ts)
            xaxis_labels = [datetime.datetime.fromtimestamp(x).strftime('%d/%m/%Y') for x in xaxis_vals]
            ax1.set_xticks(xaxis_vals, xaxis_labels, rotation=90)

            max_yval = np.max([max(calc.spline(spline_x)), max(calc.df[calc.col])])
            min_yval = np.min([min(calc.spline(spline_x)), min(calc.yvals), 0])

            ax1.set_xlim(xaxis_min, xaxis_max)
            ax1.set_ylim(min_yval * 1.1, max_yval * 1.1)
            ax1.set_ylabel(calc.col)

            # Plot the historical data
            ax1.plot(convert_dates_to_floats(calc.df['date']), calc.df[calc.col])

            ax1.grid(True)
            ax1.yaxis.grid(True, which='minor', linestyle='--')

        # Draw backgrounds
        self.fig.canvas.draw()

        # Capture the raw background, and then plot the data
        for i in range(len(list_of_calculators)):
            ax1 = self.axes[i]
            calc = self.plot_dict[i]['calc']
            spline_x = self.plot_dict[i]['spline_x']
            self.plot_dict[i]['bg'] = self.fig.canvas.copy_from_bbox(ax1.bbox)
            self.plot_dict[i]['l'],  = ax1.plot(calc.xvals, calc.yvals, color='k', linestyle='none', marker='o', markersize=8)
            self.plot_dict[i]['m'], = ax1.plot(spline_x, calc.spline(spline_x), 'r-', label=f'Future {calc.col}')

        # Assign the callbacks
        self.fig.canvas.mpl_connect('button_press_event', button_press_callback)
        self.fig.canvas.mpl_connect('button_release_event', button_release_callback)
        self.fig.canvas.mpl_connect('motion_notify_event', motion_notify_callback)

        # Add reset button
        axres = plt.axes([0.84, 0.9, 0.12, 0.02])  # left, bottom, width, height
        bres = Button(axres, 'Reset')
        bres.on_clicked(reset)

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

    cgui_2 = ClickableCalculator(df=bsh.df[['date', 'avg_interest_rate_notes']])
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.5 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.25 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.25 / 100)
    cgui_2.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.5 / 100)

    cgui_3 = ClickableCalculator(df=bsh.df[['date', 'avg_interest_rate_bonds']])
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1.5 * 365), val=3.5 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=3.25 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2.5 * 365), val=2.25 / 100)
    cgui_3.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=2.5 / 100)

    multi_cgui = ClickableFig(list_of_calculators=[cgui_1, cgui_2, cgui_3])

    sample_dates = [datetime.datetime.now() + datetime.timedelta(days=x) for x in range(0, 365 * 3, 1)]
    sample_vals = cgui_1.sample_data(sample_dates)

    plt.plot(sample_dates, sample_vals, linestyle='-', c='black')
    plt.show()
