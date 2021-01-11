import abc
import networkx as nx
from dataclasses import dataclass


@dataclass
class NetworkAbs(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def supply(self):
        pass

    def demand(self):
        return 2
