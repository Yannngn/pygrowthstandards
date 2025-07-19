from matplotlib.axes import Axes
from matplotlib.figure import Figure

SD_STYLES = {
    "user": {"color": "#9A0E9A", "marker": "o", "linestyle": "solid", "linewidth": 2},
    "sd5neg": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.5},
    "sd4neg": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.7},
    "sd3neg": {"color": "#e53935", "linestyle": "dashed", "linewidth": 1.5},
    "sd2neg": {"color": "#fb8c00", "linestyle": "dashed", "linewidth": 1.5},
    "sd1neg": {"color": "#43a047", "linestyle": "dashdot", "linewidth": 1.5},
    "sd0": {"color": "#1e88e5", "linestyle": "solid", "linewidth": 2},
    "sd1": {"color": "#43a047", "linestyle": "dashdot", "linewidth": 1.5},
    "sd2": {"color": "#fb8c00", "linestyle": "dashed", "linewidth": 1.5},
    "sd3": {"color": "#e53935", "linestyle": "dashed", "linewidth": 1.5},
    "sd4": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.7},
    "sd5": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.5},
}

PERCENTILE_STYLES = {
    "user": {"color": "#93078A", "linestyle": "solid", "linewidth": 2},
    "p01": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.5},
    "p1": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.7},
    "p3": {"color": "#e53935", "linestyle": "dashed", "linewidth": 1.5},
    "p5": {"color": "#fb8c00", "linestyle": "dashed", "linewidth": 1.5},
    "p10": {"color": "#43a047", "linestyle": "dashdot", "linewidth": 1.5},
    "p25": {"color": "#1e88e5", "linestyle": "solid", "linewidth": 2},
    "p50": {"color": "#8e24aa", "linestyle": "solid", "linewidth": 2.5},
    "p75": {"color": "#1e88e5", "linestyle": "solid", "linewidth": 2},
    "p90": {"color": "#43a047", "linestyle": "dashdot", "linewidth": 1.5},
    "p95": {"color": "#fb8c00", "linestyle": "dashed", "linewidth": 1.5},
    "p97": {"color": "#e53935", "linestyle": "dashed", "linewidth": 1.5},
    "p99": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.7},
    "p999": {"color": "#424242", "linestyle": "dotted", "linewidth": 1, "alpha": 0.5},
}

FIG_AXES_STYLE = {
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#f9f9f9",
    "axes.edgecolor": "#cccccc",
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.8,
    "axes.labelcolor": "#333333",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "font.size": 12,
    "legend.frameon": False,
    "legend.fontsize": 11,
    "lines.antialiased": True,
}


def set_style(fig: Figure, ax: Axes, style: dict = FIG_AXES_STYLE):
    """Apply the style dictionary to a matplotlib figure and axes."""
    fig.patch.set_facecolor(style.get("figure.facecolor", "#ffffff"))
    ax.set_facecolor(style.get("axes.facecolor", "#f9f9f9"))
    for spine in ax.spines.values():
        spine.set_edgecolor(style.get("axes.edgecolor", "#cccccc"))
    ax.grid(
        style.get("axes.grid", True),
        color=style.get("grid.color", "#e0e0e0"),
        linestyle=style.get("grid.linestyle", "--"),
        linewidth=style.get("grid.linewidth", 0.8),
        axis="both",
    )
    ax.set_axisbelow(style.get("axes.axisbelow", True))
    ax.xaxis.label.set_color(style.get("axes.labelcolor", "#333333"))
    ax.yaxis.label.set_color(style.get("axes.labelcolor", "#333333"))
    ax.tick_params(
        axis="x",
        colors=style.get("xtick.color", "#333333"),
        direction=style.get("xtick.direction", "out"),
    )
    ax.tick_params(
        axis="y",
        colors=style.get("ytick.color", "#333333"),
        direction=style.get("ytick.direction", "out"),
    )

    fig.set_tight_layout(True)  # type: ignore


def get_label_name(key: int | float):
    if isinstance(key, int):
        return f"sd{key}" if key >= 0 else f"sd{-key}neg"

    if isinstance(key, float):
        if key == 0.001:
            return "p01"
        elif key == 0.999:
            return "p999"
        return f"p{int(key * 100)}"


def get_label_style(key):
    """Return style dict for a given SD or percentile key."""
    if key in SD_STYLES:
        return SD_STYLES[key]
    if key in PERCENTILE_STYLES:
        return PERCENTILE_STYLES[key]
    return {"color": "#cccccc", "linestyle": "solid", "linewidth": 1}
