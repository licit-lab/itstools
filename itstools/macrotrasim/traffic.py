"""
    Traffic information
"""

# ==============================================================================
# Imports
# ==============================================================================

from dataclasses import dataclass, field
from itertools import count
from typing import Iterable

import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from .constants import K_X, W_I, U_I
import holoviews as hv
import hvplot.pandas

hv.extension("bokeh")

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


@dataclass
class Demand:
    sampling_time: float = 15
    fd: FundamentalDiagram = FundamentalDiagram()
    cycle_time: float = 90

    def __init__(self, network, simulation_steps=50):
        self._entry_roads = network.get_entry_roads()
        time_vector = np.arange(
            0, simulation_steps * self.cycle_time, self.sampling_time
        )
        self._demand = pd.DataFrame(
            data=0, columns=network.roads, index=time_vector
        )
        self.set_burst_value(self.fd.C)

    def set_burst_value(self, burst_value):
        """ Sets the burst values for incomming roads"""
        self._demand[self._entry_roads] = burst_value

    def plot(self):
        return self._demand.hvplot.heatmap()

    def __iter__(self):
        self._it = self._demand.iterrows()
        return self._it

    def __next__(self):
        yield next(self._it)
