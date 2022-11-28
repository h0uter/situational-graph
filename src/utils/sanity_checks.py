import networkx as nx

from src.state.situational_graph import SituationalGraph
from src.shared.behaviors import Behaviors


def check_no_duplicate_wp_edges(krm: SituationalGraph):
    """
    Check if there are no duplicate waypoint edges in the graph.
    """
    G = krm.G

    def filter_wp_edge(n1, n2, n3):
        return G.edges[n1, n2, n3]["type"] == Behaviors.GOTO

    view = nx.subgraph_view(G, filter_edge=filter_wp_edge)

    for node_a in view.nodes():
        for node_b in view.nodes():
            if view.number_of_edges(node_a, node_b) > 1:
                raise Exception(
                    f"Duplicate waypoint edges in graph ({node_a} -> {node_b})"
                )
