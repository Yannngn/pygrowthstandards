import numpy as np
from matplotlib.axes import Axes

from ..constants import MONTH, WEEK, YEAR


# Helper to set ticks and labels
def set_xticks(ax: Axes, ticks, fmt):
    ax.set_xticks(ticks)
    ax.set_xticklabels([fmt(val) for val in ticks], rotation=45, ha="right")


def set_xticks_by_range(ax: Axes, x_min: float, x_max: float):
    # Decide tick interval and format based on range
    if x_max <= (MONTH * 10):  # up to ~3 months, show every week
        interval = WEEK
        ticks = np.arange(x_min, x_max + WEEK, interval)
        set_xticks(ax, ticks, lambda d: f"{int(d//WEEK)}w")
        return

    if x_max <= (YEAR * 2):  # up to 2 years, show every month
        interval = MONTH
        ticks = np.arange(x_min, x_max + MONTH, interval)
        set_xticks(ax, ticks, lambda d: f"{int(d//MONTH)}m")
        return

    if x_max <= (YEAR * 5):  # up to 5 years, show every 3 months
        interval = MONTH * 3
        ticks = np.arange(x_min, x_max + MONTH, interval)
        set_xticks(ax, ticks, lambda d: f"{int(d//YEAR)}y {int((d%YEAR)//MONTH)}m")
        return

    if x_max <= (YEAR * 10):  # up to 10 years, show every year
        interval = YEAR
        ticks = np.arange(x_min, x_max + YEAR, interval)
        set_xticks(ax, ticks, lambda d: f"{int(d//YEAR)}y")
        return

    # more than 10 years, show every 2 years
    interval = YEAR * 2
    ticks = np.arange(x_min, x_max + YEAR, interval)
    set_xticks(ax, ticks, lambda d: f"{int(d//YEAR)}y")
