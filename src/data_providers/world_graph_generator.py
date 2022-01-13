import os
import networkx as nx
import numpy as np
import pickle
import time

def get_rand_sign():
    return np.random.choice([-1, 1])

class GraphGenerator():
    def __init__(self, num_nodes) -> None:
        self.generate_graph(num_nodes)

    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.graph.nodes():
            if self.graph.nodes[node]['pos'] == pos:
                return node

    def generate_graph(self, num_nodes: int) -> nx.Graph:
        self.graph = nx.Graph()
        count = 0

        for i in range(num_nodes):
            if i == 0:
                self.graph.add_node(0, pos=(0, 0))
            elif count == 15:
                subtree_idx = i
                count = 0

                valid_candidate = False
                while not valid_candidate:
                    self.graph.add_node(i , pos=(0, 0))
                    min_idx = min(self.graph.nodes)
                    max_idx = max(self.graph.nodes)
                    new_root_idx = np.random.randint(low=min_idx, high=max_idx)
                    print(f"min_idx: {min_idx}, max_idx: {max_idx}, new root idx: {new_root_idx}")
                    new_root_pos  = self.graph.nodes[new_root_idx]['pos']

                    sign1 = get_rand_sign()
                    sign2 = get_rand_sign()
                    sample_dist = np.random.randint(low=3, high=6)
                    sample_dist2 = np.random.randint(low=3, high=6)
                    new_x = new_root_pos[0] + sample_dist*sign1
                    new_y = new_root_pos[1] + sample_dist2*sign2
                    new_pos = (new_x, new_y)

                    candidate_node_pos = new_pos

                    nodes_in_rad = self.get_nodes_in_radius(self.graph, candidate_node_pos, 4)
                    if nodes_in_rad == []:
                        valid_candidate = True

                self.graph.add_node(i, pos=new_pos)
                self.graph.add_edge(i, new_root_idx)

            else:
                old_pos = self.graph.nodes[i-1]['pos']
                
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

                    nodes_in_rad = self.get_nodes_in_radius(self.graph, candidate_node_pos, 4)
                    if nodes_in_rad == []:
                        valid_candidate = True

                    print(i)
                    # TODO: reset the whole unit if it gets stuck

                count += 1
                
                self.graph.add_node(i, pos=new_pos)
                self.graph.add_edge(i, i-1)

        # path = os.getcwd()
        full_path = os.path.join('src', 'data_providers', 'generated_world_graphs', f'{time.time()}_generated_world_graph.p')
        file_to_store = open(full_path, "wb")
        pickle.dump(self, file_to_store)
        file_to_store.close()


        # return self.graph
    
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
