"""
Manhattan Network
=================
"""

import networkx as nx
from networkx.readwrite.edgelist import write_weighted_edgelist


def create_manhattan_intersections(m: int = 10, n: int = 10):
    """ Build a manhattan grid road graph of n by m roads
        
        Args:
            m (int): number of rows
            n (int): number of columns
             
        N,W,E,S: North,Weast,East,South
    """
    nodes = tuple((i, j) for i in range(m) for j in range(n))
    vert_edgesSN = tuple(
        (o, d) for o, d in zip(nodes, nodes[1:]) if o[1] != n - 1 and o[0] % 2
    )
    vert_edgesNS = tuple(
        (d, o) for o, d in zip(nodes, nodes[1:]) if o[1] != n - 1 and ~o[0] % 2
    )
    vert_edges = vert_edgesSN + vert_edgesNS

    # Suplementary external nodes/edges South
    nodes_S = tuple((-1, i) for i in range(n))
    edges_S = tuple(((-1, i), (0, i)) for i in range(n) if i % 2) + tuple(
        ((0, i), (-1, i)) for i in range(n) if ~i % 2
    )

    # Suplementary external nodes/edges North
    nodes_N = tuple((m, i) for i in range(n))
    edges_N = tuple(((m, i), (m - 1, i)) for i in range(n) if ~i % 2) + tuple(
        ((m - 1, i), (m, i)) for i in range(n) if i % 2
    )

    nodes = nodes + nodes_S + nodes_N

    nodes_transposed = tuple((i, j) for j in range(n) for i in range(m))
    horz_edgesEW = tuple(
        (o, d)
        for o, d in zip(nodes_transposed, nodes_transposed[1:])
        if o[0] != m - 1 and o[1] % 2
    )
    horz_edgesWE = tuple(
        (d, o)
        for o, d in zip(nodes_transposed, nodes_transposed[1:])
        if o[0] != m - 1 and ~o[1] % 2
    )
    horz_edges = horz_edgesEW + horz_edgesWE

    # Suplementary external nodes/edges West
    nodes_W = tuple((i, -1) for i in range(m))
    edges_W = tuple(((i, -1), (i, 0)) for i in range(n) if i % 2) + tuple(
        ((i, 0), (i, -1)) for i in range(n) if ~i % 2
    )

    # Suplementary external nodes/edges East
    nodes_E = tuple((i, n) for i in range(m))
    edges_E = tuple(((i, n), (i, n - 1)) for i in range(n) if ~i % 2) + tuple(
        ((i, n - 1), (i, n)) for i in range(n) if i % 2
    )

    nodes = nodes + nodes_W + nodes_E
    K = 10  # Scale factor
    # Positions
    nodesnpos = tuple((n,) + ({"pos": (K * n[0], K * n[1])},) for n in nodes)

    edges = horz_edges + vert_edges + edges_S + edges_N + edges_E + edges_W
    weightededges = tuple(e + (0,) for e in edges)

    G = nx.DiGraph()
    G.add_nodes_from(nodesnpos)
    G.add_weighted_edges_from(weightededges, weight="density")

    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    return G, pos
