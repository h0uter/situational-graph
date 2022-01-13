import os
import networkx as nx
import numpy as np
import pickle
import time

class GraphGenerator():
    def __init__(self, num_nodes) -> None:
        self.graph = nx.Graph()

        success = False
        self.tries_before_reset = 25
        while not success:
            success = self.generate_graph(num_nodes)

    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.graph.nodes():
            if self.graph.nodes[node]['pos'] == pos:
                return node

    def sample_pos(self, from_node_pos):
        sign1 = np.random.choice([-1, 1])
        sign2 = np.random.choice([-1, 1])
        sample_dist = np.random.randint(low=3, high=6)
        sample_dist2 = np.random.randint(low=3, high=6)
        new_x = from_node_pos[0] + sample_dist*sign1
        new_y = from_node_pos[1] + sample_dist2*sign2
        new_pos = (new_x, new_y)
        return new_pos

    def generate_graph(self, num_nodes: int) -> nx.Graph:
        count = 0
        reset_counter = 0

        for i in range(num_nodes):
            if i == 0:
                self.graph.add_node(0, pos=(0, 0))
            elif count == 5:
                count = 0
                valid_candidate = False
                while not valid_candidate:
                    if reset_counter > self.tries_before_reset:
                        print("STUCK, retrying")
                        return False
                    # self.graph.add_node(i , pos=(0, 0))
                    min_idx = min(self.graph.nodes)
                    max_idx = max(self.graph.nodes)
                    new_root_idx = np.random.randint(low=min_idx, high=max_idx)
                    new_root_pos  = self.graph.nodes[new_root_idx]['pos']

                    candidate_pos = self.sample_pos(new_root_pos)
                    nodes_in_rad = self.get_nodes_in_radius(self.graph, candidate_pos, 4)
                    if nodes_in_rad == []:
                        valid_candidate = True
                
                reset_counter = 0
                self.graph.add_node(i, pos=candidate_pos)
                self.graph.add_edge(i, new_root_idx)

            else:
                old_pos = self.graph.nodes[i-1]['pos']
                
                valid_candidate = False
                while not valid_candidate:
                    if reset_counter > self.tries_before_reset:
                        print("STUCK, retrying")
                        return False

                    candidate_pos = self.sample_pos(old_pos)
                    nodes_in_rad = self.get_nodes_in_radius(self.graph, candidate_pos, 4)
                    if nodes_in_rad == []:
                        valid_candidate = True

                    print(i)
                    reset_counter += 1
                    # TODO: reset the whole unit if it gets stuck
                reset_counter = 0
                count += 1
                self.graph.add_node(i, pos=candidate_pos)
                self.graph.add_edge(i, i-1)

        '''save the generated map object to a pickle file so it can be used for testing'''
        self.save_graph()
        return True

    def save_graph(self):
        full_path = os.path.join('src', 'data_providers', 'generated_world_graphs', f'{time.time()}_generated_world_graph.p')
        file_to_store = open(full_path, "wb")
        pickle.dump(self, file_to_store)
        file_to_store.close()

    def get_nodes_in_radius(self, graph: nx.Graph, pos: tuple, radius: int) -> list:
        nodes_in_radius = []
        for node in graph.nodes:
            node_pos = graph.nodes[node]['pos']
            dist = np.linalg.norm(np.array(pos) - np.array(node_pos))
            if dist < radius:
                nodes_in_radius.append(node)
        return nodes_in_radius
