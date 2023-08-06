r"""
Stable graphs (and decorated versions).
"""

from sage.rings.all import ZZ
from sage.graphs.graph import Graph

def canonical_label(stg, k, algorithm=None):
    r"""
    """
    G, zeros = stg
    zeros = [(z, i) for (i, z) in enumerate(zeros)]
    zeros.sort(key = lambda (z, v): (sum(z) - k * G.degree(v), len(z), z))
    partition = [None] * len(zeros)
    partition[zeros[0][1]] = 0
    for i in range(1, len(zeros)):
        z, v = zeros[i]
        if z != zeros[i-1][0]:
            k += 1
        partition[v] = k

    Gcan, m = G.canonical_label(partition=partition, edge_labels=True, certificate=True, algorithm=algorithm)
    new_zeros = [None] * len(zeros)
    for z,v in zeros:
        new_zeros[m[v]] = z
    return (Gcan, tuple(new_zeros))

def differential_stable_graphs(k, zeros, algorithm=None):
    r"""
    Each stable graph consists of a graph (with loops) whose edges carry
    multiplicities and a list of vertex data (a partition of the zeros).

    Warning: for getting cylinder diagram there are some positivity condition
    to be respected... (residues have to sum up to zero)

    INPUT:

    - ``k`` - degree of the differential

    - ``zeros`` - a list of zero degrees that should sum up to `k (2g - 2)`
    """
    k = ZZ(k)
    if k < 0:
        raise ValueError("k must be a positive integer")
    zeros = list(map(ZZ, zeros))
    if any(x <= -k for x in zeros):
        raise ValueError("the poles must have order at most k={}".format(k))

    # we color the vertices according to the zeros they carry
    #   order first by genus, then by number of zeros, then lexico
    
    G = Graph(1, multiedges=False, loops=True).copy(immutable=True)
    stg = (G, (tuple(sorted(zeros)),))
    yield stg
    graphs = [stg]

    while True:
        new_graphs = set()
        for G, zeros in graphs:
            for v in G:
                # add loop
                gv = (sum(zeros[v]) - k * G.degree(v)) // k  + 2
                assert gv % 2 == 0
                gv //= 2
                H = G.copy(mutable=True)
                if gv > 0:
                    if H.has_edge(v, v):
                        H.set_edge_label(v, v, G.edge_label(v, v) + 1)
                    else:
                        H.add_edge(v, v, 1)
                stg = (H.copy(immutable=True), zeros)
                if stg not in new_graphs:
                    yield stg
                    new_graphs.add(stg)

                # split zeros
                if len(zeros) > 1:
                    # a lot of choices!
                    # 1. need to split the zeros into two (non-empty) parts
                    # 2. need to split the edges

        graphs = new_graphs

