import networkx as nx
import numpy as np

def get_rand_sign():
    return np.random.choice([-1, 1])

class GraphGenerator():
    def __init__(self) -> None:
        pass

    def generate_graph(self, num_nodes: int) -> nx.Graph:
        graph = nx.Graph()

        for i in range(num_nodes):
            if i == 0:
                graph.add_node(0, pos=(0, 0))
            else:
                old_pos = graph.nodes[i-1]['pos']
                
                valid_candidate = False
                while not valid_candidate:

                    # lets randomly sample between 3 and 5 meters
                    sign1 = get_rand_sign()
                    sign2 = get_rand_sign()
                    sample_dist = np.random.randint(low=3, high=6)
                    sample_dist2 = np.random.randint(low=3, high=6)
                    new_x = old_pos[0] + sample_dist*sign1
                    new_y = old_pos[1] + sample_dist2*sign2
                    # new_pos = list(old_pos) + list((4,0))
                    new_pos = (new_x, new_y)

                    candidate_node_pos = new_pos

                    nodes_in_rad = self.get_nodes_in_radius(graph, candidate_node_pos, 3)
                    if nodes_in_rad == []:
                        valid_candidate = True

                    print(i)

                
                graph.add_node(i, pos=new_pos)
                graph.add_edge(i, i-1)

        return graph
    
    # so make a candidate node, run this function, if its empty lets sample it.
    # otherwise lets try a new candidate. 

    # Guess I need a function which can compute over a grapph if there are any nodes positioned in a certain radius around it.
    def get_nodes_in_radius(self, graph: nx.Graph, pos: tuple, radius: int) -> list:
        nodes_in_radius = []
        for node in graph.nodes:
            node_pos = graph.nodes[node]['pos']
            dist = np.linalg.norm(np.array(pos) - np.array(node_pos))
            if dist < radius:
                nodes_in_radius.append(node)
        return nodes_in_radius
