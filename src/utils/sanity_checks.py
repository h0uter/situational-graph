from src.entities.krm import KRM
from src.utils.my_types import EdgeType
import networkx as nx


def check_no_duplicate_wp_edges(krm: KRM):
    """
    Check if there are no duplicate waypoint edges in the graph.
    """
    G = krm.graph

    # def filter_wp_edge(n1, n2):
    #     return G[n1][n2].get("type", EdgeType.WAYPOINT_EDGE)
    def filter_wp_edge(n1, n2, n3):
        return G[n1][n2][n3].get("type", EdgeType.GOTO_WP_EDGE)

    view = nx.subgraph_view(G, filter_edge=filter_wp_edge)

    for node_a in view.nodes():
        for node_b in view.nodes():
            if view.number_of_edges(node_a, node_b) > 1:
                print(f"{node_a} {node_b}")
                raise Exception("Duplicate waypoint edges in graph.")
