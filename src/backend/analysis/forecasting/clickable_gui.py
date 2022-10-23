import scipy
import datetime

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from src.backend.analysis.balance_sheet_projection import BalanceSheetHistorical


class ClickableGUI:
    def __init__(self, df, default_end_val, end_date):
        self.df = df.reset_index(drop=True)
        assert len(self.df.columns) == 2
        assert 'date' in self.df.columns
        self.col = [x for x in self.df.columns if x != 'date'][0]

        self.start_val = self.df.iloc[-1][self.col]
        self.start_date = self.df.iloc[-1]['date']

        # self.default_end_val = default_end_val
        # self.end_date = end_date

        self._list_of_points = list()
        self.add_point(date=self.start_date, val=self.start_val)
        # self.add_point(date=end_date, val=default_end_val)

    @property
    def list_of_points(self):
        xvals = np.array(self._list_of_points)[:, 0]
        xvals = convert_dates_to_floats(xvals)
        sort_order = np.argsort(xvals, axis=0)
        list_of_points = np.array(self._list_of_points)[sort_order]
        return list(list_of_points)

    def add_point(self, date, val):
        self._list_of_points.append([date, val])

    def _create_spline(self):
        return scipy.interpolate.InterpolatedUnivariateSpline(self.xvals, self.yvals)

    def _reset_xvals(self):
        xvals = np.array(self.list_of_points)[:, 0]
        xvals = np.array([x.timestamp() for x in xvals])
        xvals = np.array(xvals).astype(float)
        return xvals

    def _reset_yvals(self):
        return np.array(np.array(self.list_of_points)[:, 1]).astype(float)

    def create_plot(self):

        self.xvals = self._reset_xvals()
        self.yvals = self._reset_yvals()
        self.spline = self._create_spline()

        # set up a plot
        fig, ax1 = plt.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
        plt.subplots_adjust(right=0.8)

        self.pind = None  # active point
        epsilon = 5  # max pixel distance

        def reset(event):

            # reset the values
            self.xvals = self._reset_xvals()
            self.yvals = self._reset_yvals()
            self.spline = self._create_spline()

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

            self.pind = get_ind_under_point(event)

        def button_release_callback(event):
            """whenever a mouse button is released"""

            if event.button != 1:
                return
            self.pind = None

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

            if self.pind is None:
                return
            if event.inaxes is None:
                return
            if event.button != 1:
                return

            # You can't select the first point
            if self.pind == 0:
                return

            # Prevent the point from being dragged too far left
            if event.xdata <= self.xvals[self.pind - 1]:
                return

            if self.pind != len(self.xvals) - 1 and event.xdata >= self.xvals[self.pind + 1]:
                return

            if self.pind != 0 and self.pind != len(self.xvals) - 1:
                self.xvals[self.pind] = event.xdata
                l.set_xdata(self.xvals)

            self.yvals[self.pind] = event.ydata
            l.set_ydata(self.yvals)

            spline = self._create_spline()
            m.set_ydata(spline(spline_x))

            fig.canvas.draw_idle()

        spline_intervals = 1000
        spline_x = np.linspace(min(self.xvals), max(self.xvals), spline_intervals)

        l, = ax1.plot(self.xvals, self.yvals, color='k', linestyle='none', marker='o', markersize=8)
        m, = ax1.plot(spline_x, self.spline(spline_x), 'r-', label='spline')

        ax1.plot(convert_dates_to_floats(self.df['date']), self.df[self.col])
        ax1.set_ylim(0, max(self.spline(spline_x)) * 1.1)
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')

        ax1.grid(True)
        ax1.yaxis.grid(True, which='minor', linestyle='--')
        ax1.legend(loc=2, prop={'size': 22})

        axres = plt.axes([0.84, 0.3, 0.12, 0.02])
        bres = Button(axres, 'Reset')
        bres.on_clicked(reset)

        fig.canvas.mpl_connect('button_press_event', button_press_callback)
        fig.canvas.mpl_connect('button_release_event', button_release_callback)
        fig.canvas.mpl_connect('motion_notify_event', motion_notify_callback)

        plt.show()


def convert_dates_to_floats(dates):
    return np.array([x.timestamp() for x in dates])


def convert_floats_to_dates(floats):
    return np.array([datetime.datetime.fromtimestamp(x) for x in floats])


if __name__ == '__main__':

    bsh = BalanceSheetHistorical()

    cgui = ClickableGUI(df=bsh.df[['date', 'avg_interest_rate_bills']],
                        default_end_val=4.00 / 100,
                        end_date=datetime.datetime.now() + datetime.timedelta(days=5 * 365))

    cgui.add_point(date=datetime.datetime.now() + datetime.timedelta(days=1 * 365), val=3.00 / 100)
    cgui.add_point(date=datetime.datetime.now() + datetime.timedelta(days=2 * 365), val=4.00 / 100)
    cgui.add_point(date=datetime.datetime.now() + datetime.timedelta(days=3 * 365), val=5.00 / 100)
    cgui.create_plot()
