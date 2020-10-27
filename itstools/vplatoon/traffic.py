"""
    Traffic information
"""

# ==============================================================================
# Imports
# ==============================================================================

import numpy as np
from bokeh.plotting import figure, show
from .vehicles import K_X, W_I, U_I

# ==============================================================================
# Clases
# ==============================================================================


class FundamentalDiagram:
    def __init__(self, w=W_I, u=U_I, k_x=K_X):
        self.w = w
        self.k_x = k_x
        self.u = u

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

    def __repr__(self):
        return f"{self.__class__.__name__}({self.w},{self.u},{self.k_x})"

    def __str__(self):
        return f"Fundamental diagram w: {self.w}, u:{self.u}, k_x:{self.k_x}"
