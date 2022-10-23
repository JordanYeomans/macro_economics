import datetime
import scipy

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button


class ClickableGUI:
    def __init__(self, start_val, default_end_val, start_date, end_date):
        self.start_val = start_val
        self.default_end_val = default_end_val
        self.start_date = start_date
        self.end_date = end_date

        self._list_of_points = list()
        self._spline = None

        self.add_point(date=start_date, val=start_val)
        self.add_point(date=end_date, val=default_end_val)

    @property
    def list_of_points(self):
        xvals = np.array(self._list_of_points)[:, 0]
        xvals = [x.timestamp() for x in xvals]
        sort_order = np.argsort(xvals, axis=0)
        list_of_points = np.array(self._list_of_points)[sort_order]
        return list(list_of_points)

    def add_point(self, date, val):
        self._list_of_points.append([date, val])

    def _create_spline(self):
        return scipy.interpolate.InterpolatedUnivariateSpline(self.xvals, self.yvals)

    def create_plot(self):

        def get_xvals():
            xvals = np.array(self.list_of_points)[:, 0]
            xvals = np.array([x.timestamp() for x in xvals])
            xvals = np.array(xvals).astype(float)
            return xvals

        def get_yvals():
            return np.array(np.array(self.list_of_points)[:, 1]).astype(float)

        self.xvals = get_xvals()
        self.yvals = get_yvals()

        self.spline = self._create_spline()

        # set up a plot
        fig, ax1 = plt.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
        plt.subplots_adjust(right=0.8)

        self.pind = None  # active point
        epsilon = 5  # max pixel distance

        def reset(event):

            # reset the values
            self.xvals = get_xvals()
            self.yvals = get_yvals()
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

            self.xvals[self.pind] = event.xdata
            self.yvals[self.pind] = event.ydata

            l.set_xdata(self.xvals)
            l.set_ydata(self.yvals)

            spline = self._create_spline()
            m.set_ydata(spline(spline_x))

            fig.canvas.draw_idle()

        spline_intervals = 1000
        spline_x = np.linspace(min(self.xvals), max(self.xvals), spline_intervals)

        l, = ax1.plot(self.xvals, self.yvals, color='k', linestyle='none', marker='o', markersize=8)
        m, = ax1.plot(spline_x, self.spline(spline_x), 'r-', label='spline')

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


if __name__ == '__main__':
    cgui = ClickableGUI(start_val=2,
                        default_end_val=4,
                        start_date=datetime.datetime.now(),
                        end_date=datetime.datetime.now() + datetime.timedelta(days=365))

    cgui.add_point(date=datetime.datetime.now() + datetime.timedelta(days=30), val=2.5)
    cgui.add_point(date=datetime.datetime.now() + datetime.timedelta(days=320), val=4)
    cgui.create_plot()
