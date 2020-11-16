# ==============================================================================
# STANDARD IMPORTS
# ==============================================================================

from typing import ItemsView

from networkx.algorithms.link_prediction import within_inter_cluster
from .metaclass import NetworkAbs
import networkx as nx
from dataclasses import dataclass
import pandas as pd

from .lights import Light
from .traffic import RoadLink
from .manhattan import create_manhattan_intersections

# ==============================================================================
# CLASS AND DEFINITIONS
# ==============================================================================


@dataclass
class Network(NetworkAbs):
    sampleTime: int = 1
    period: int = 90
    lights: int = 0
    isControlled: bool = True
    rTurning: float = 0.65
    m: int = 2
    n: int = 2

    def __post_init__(self):
        print(f"Initializing network: {self.n} x {self.m}")
        self.network, self._netpos = create_manhattan_intersections(
            m=self.m, n=self.n
        )
        self.populate_road_objects()
        self.create_adjacency_road_xssing_matrix()
        self.create_road_graph()

    def populate_road_objects(self):
        """ Populate with road objects and traffic lights 
        """
        self._roadObjects = {
            i: {"id": n, "road": RoadLink(), "light": Light()}
            for n, i in enumerate(self.network.edges())
        }
        self._roads = tuple(v["id"] for i, v in self._roadObjects.items())
        self._roadinter_map = {v["id"]: k for k, v in self._roadObjects.items()}

    @property
    def roads(self):
        """ Return road identifiers 
        """
        return self._roads

    def create_adjacency_road_xssing_matrix(self):
        """ Creates the road-intersection adajacency matrix noted by
            m x n : m roads / n intersections 

            i->j means road i is upstream of intersection j. eq intersection j is downstream of road i 

            j->i means road i is downstream of intersection j. eq intersection j is upstream of road i 

            (i,j): -1 if i->j , 1 if j-> i, 0 elsewhere
        """
        self._intersectionMatrix = pd.DataFrame(
            index=self.roads, columns=self.network.nodes(), data=0
        )
        for road in self.roads:
            origin, destination = self._roadinter_map[road]
            self._intersectionMatrix.loc[road, origin] = -1
            self._intersectionMatrix.loc[road, destination] = 1

    def create_road_graph(self):
        """ Creates a graph for roads only with the only purpose to reduce   
            online computational burden 

            Adjacency matrix: 
            i->j means road i is upstream of road j. eq road j is downstream of road i 
        """

        def road_positions(roadid):
            data = self._roadinter_map[roadid]
            origin = self.network.nodes[data[0]]["pos"]
            destination = self.network.nodes[data[1]]["pos"]
            x = (destination[0] + origin[0]) / 2
            y = (destination[1] + origin[1]) / 2
            return x, y

        self.roadgraph = nx.DiGraph()
        self._roadpos = [road_positions(road) for road in self.roads]
        self.roadgraph.add_nodes_from(
            [
                (road, {"pos": road_positions(road), "density": 0.0})
                for road in self.roads
            ]
        )

        # Adding edges

        edges = []
        for road in self.roads:
            downstream, ratios = self.get_downstream_roads(road)
            [
                self.roadgraph.add_edge(road, d, ratio=r)
                for d, r in zip(downstream, ratios)
            ]
            upstream, ratios = self.get_upstream_roads(road)
            [
                self.roadgraph.add_edge(u, road, ratio=r)
                for u, r in zip(upstream, ratios)
            ]

    def get_downstream_roads(self, road):
        """ Returns the downstream roads of road i
        """
        upstream_xssing, downstream_xssing = self._roadinter_map[road]
        downstream = self._intersectionMatrix[
            self._intersectionMatrix[downstream_xssing].eq(-1)
        ].index.tolist()

        if downstream:

            # Downstream xssings
            dst_xssings = [self.get_downstream_xssing(d) for d in downstream]

            ratios = []
            for d in dst_xssings:
                o = upstream_xssing
                if o[0] == d[0] or o[1] == d[1]:
                    ratios.append(self.rTurning)
                else:
                    ratios.append(1 - self.rTurning)
        else:
            ratios = []

        return downstream, ratios

    def get_upstream_roads(self, road):
        """ Returns the upstream roads of road i
        """
        upstream_xssing, downstream_xssing = self._roadinter_map[road]
        upstream = self._intersectionMatrix[
            self._intersectionMatrix[upstream_xssing].eq(1)
        ].index.tolist()

        if upstream:

            # Upstream xssings
            ust_xssings = [self.get_upstream_xssing(d) for d in upstream]

            ratios = []
            for o in ust_xssings:
                d = downstream_xssing
                if o[0] == d[0] or o[1] == d[1]:
                    ratios.append(self.rTurning)
                else:
                    ratios.append(1 - self.rTurning)
        else:
            ratios = []

        return upstream, ratios

    def get_downstream_xssing(self, road):
        """Return downstream intersection of road i 
        """
        return self._roadinter_map[road][1]

    def get_upstream_xssing(self, road):
        """Return upstream intersection of road i 
        """
        return self._roadinter_map[road][0]

    def get_entry_roads(self):
        """ Return entry roads ids"""
        return [x for x in self.roads if not self.get_downstream_roads(x)[0]]

    def get_exit_roads(self):
        """ Return exit roads ids"""
        return [x for x in self.roads if not self.get_upstream_roads(x)[0]]

    def plot_road_network(
        self, xssing_labels=False, road_labels=False, figsize=(20, 10)
    ):
        """ Plots the road graph 
        """
        from matplotlib import pyplot as plt

        f, ax = plt.subplots(1, 2, figsize=figsize)
        options = {"node_size": 500, "alpha": 0.5}
        nx.draw(
            self.network,
            pos=self._netpos,
            with_labels=xssing_labels,
            ax=ax[0],
            font_size=8,
            **options,
        )
        nx.draw_networkx_nodes(
            self.roadgraph,
            pos=self._roadpos,
            node_color="red",
            ax=ax[0],
            node_size=10,
        )
        ax[0].set_title("Intersection Graph")
        nx.draw(
            self.roadgraph,
            pos=self._roadpos,
            node_color="red",
            with_labels=road_labels,
            ax=ax[1],
            font_size=8,
            **options,
        )
        ax[1].set_title("Road Graph")

    def supply(self):
        pass
