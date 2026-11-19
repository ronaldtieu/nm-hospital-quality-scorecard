"""Shared chart style for the NM hospital scorecard notebooks.

Colors are the dataviz skill's validated, colorblind-safe default palette
(light mode). Keeping them here means every figure in reports/figures/ looks
like one system. Import and call apply_style() at the top of each notebook.
"""
import matplotlib.pyplot as plt

# categorical hues, fixed order (never cycle past 8)
CATEGORICAL = [
    "#2a78d6",  # blue
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
    "#e87ba4",  # magenta
    "#eb6834",  # orange
]

# diverging / status roles (Better <-> Worse, with a neutral middle)
BETTER = "#2a78d6"       # blue pole
WORSE = "#d03b3b"        # red pole
NO_DIFFERENT = "#c9c7c0"  # neutral gray midpoint
GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

# one-hue sequential blue ramp (light -> dark) for magnitude
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]

# ink / chrome
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"


def apply_style():
    """Set matplotlib rcParams to the shared look."""
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })
