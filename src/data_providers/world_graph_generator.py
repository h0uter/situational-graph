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
                graph.add_node(0, pos=(-20, 0))
            else:
            
                old_pos = graph.nodes[i-1]['pos']
                # lets randomly sample between 3 and 5 meters
                sign1 = get_rand_sign()
                sign2 = get_rand_sign()
                sample_dist = np.random.randint(low=3, high=5)
                sample_dist2 = np.random.randint(low=3, high=5)
                new_x = old_pos[0] + sample_dist
                new_y = old_pos[1] + sample_dist2*sign2
                # new_pos = list(old_pos) + list((4,0))
                new_pos = (new_x, new_y)
                
                graph.add_node(i, pos=new_pos)
                graph.add_edge(i, i-1)

        return graph
