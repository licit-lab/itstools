"""
    Traffic information
"""

# ==============================================================================
# Imports
# ==============================================================================

from dataclasses import dataclass
from itertools import count
from typing import Iterable

import numpy as np
from bokeh.plotting import figure, show
from .constants import K_X, W_I, U_I

# ==============================================================================
# Clases
# ==============================================================================


@dataclass
class FundamentalDiagram:

    w: float = W_I
    k_x: float = K_X
    u: float = U_I

    @property
    def C(self):
        """ Capacity"""
        return self.u * self.k_c

    @property
    def k_c(self):
        """ Critical density"""
        return self.w * self.k_x / (self.w + self.u)

    @property
    def s_x(self):
        """ Critical spacing"""
        return 1 / self.k_x

    def compute_flow(self, k):
        free_branch = lambda x: self.u * x
        cong_branch = lambda x: -(x - self.k_x) * self.w
        flow = np.piecewise(
            k, [k < self.k_c, k >= self.k_c], [free_branch, cong_branch]
        )
        return flow

    def plot_diagram(self):
        k = np.linspace(0, self.k_x, 100)
        q = self.compute_flow(k)

        title = f"Fundamental diagram w: {self.w}, u:{self.u}, k_x:{self.k_x}"
        xlabel = "Density [veh/km]"
        ylabel = "Flow [veh/h]"

        p = figure(title=title, tools=[], plot_height=500, plot_width=500)
        p.line(k, q)
        p.xaxis.axis_label = xlabel
        p.yaxis.axis_label = ylabel
        return p


@dataclass
class RoadLink:
    _idx: Iterable[int] = count(0)

    def __post_init__(self):
        self.idx = next(self.__class__._idx)
