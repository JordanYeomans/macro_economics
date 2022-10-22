# https://stackoverflow.com/questions/50439506/dragging-points-in-matplotlib-interactive-plot

import numpy as np
import scipy.interpolate as inter

from matplotlib import pyplot as plt
from matplotlib.widgets import Button

func = lambda x: 0.1 * x ** 2

# get a list of points to fit a spline to as well
N = 10
xmax = 10
xvals = np.linspace(0, 10, N)
yvals = func(xvals)
spline = inter.InterpolatedUnivariateSpline(xvals, yvals)

# set up a plot
fig, axes = plt.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
plt.subplots_adjust(right=0.8)
ax1 = axes

pind = None  # active point
epsilon = 5  # max pixel distance


def reset(event):
    global xvals
    global yvals
    global spline
    # reset the values
    xvals = np.linspace(0, 10, N)
    yvals = func(xvals)

    spline = inter.InterpolatedUnivariateSpline(xvals, yvals)
    l.set_xdata(xvals)
    l.set_ydata(yvals)
    m.set_ydata(spline(X))
    # redraw canvas while idle
    fig.canvas.draw_idle()


def button_press_callback(event):
    'whenever a mouse button is pressed'
    global pind
    if event.inaxes is None:
        return
    if event.button != 1:
        return

    pind = get_ind_under_point(event)


def button_release_callback(event):
    'whenever a mouse button is released'
    global pind
    if event.button != 1:
        return
    pind = None


def get_ind_under_point(event):
    'get the index of the vertex under point if within epsilon tolerance'

    tinv = ax1.transData

    xr = np.reshape(xvals, (np.shape(xvals)[0], 1))
    yr = np.reshape(yvals, (np.shape(yvals)[0], 1))
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
    'on mouse movement'
    global xvals
    global yvals
    if pind is None:
        return
    if event.inaxes is None:
        return
    if event.button != 1:
        return

    xvals[pind] = event.xdata
    yvals[pind] = event.ydata

    l.set_ydata(yvals)
    l.set_xdata(xvals)

    spline = inter.InterpolatedUnivariateSpline(xvals, yvals)
    m.set_ydata(spline(X))

    fig.canvas.draw_idle()


X = np.arange(0, xmax + 1, 0.1)
ax1.plot(X, func(X), 'k--', label='original')
l, = ax1.plot(xvals, yvals, color='k', linestyle='none', marker='o', markersize=8)
m, = ax1.plot(X, spline(X), 'r-', label='spline')

ax1.set_yscale('linear')
ax1.set_xlim(0, xmax)
ax1.set_ylim(0, xmax)
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.grid(True)
ax1.yaxis.grid(True, which='minor', linestyle='--')
ax1.legend(loc=2, prop={'size': 22})


axres = plt.axes([0.84, 0.8 - ((N) * 0.05), 0.12, 0.02])
bres = Button(axres, 'Reset')
bres.on_clicked(reset)

fig.canvas.mpl_connect('button_press_event', button_press_callback)
fig.canvas.mpl_connect('button_release_event', button_release_callback)
fig.canvas.mpl_connect('motion_notify_event', motion_notify_callback)

plt.show()