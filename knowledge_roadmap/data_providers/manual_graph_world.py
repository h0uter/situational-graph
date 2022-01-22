import networkx as nx
from PIL import Image
import os

from knowledge_roadmap.utils.coordinate_transforms import img_axes2world_axes


class ManualGraphWorld():
    ''' 
    The goal of this class is to 
    - enable testing of the exploration without the sampler
    '''
    def __init__(self, map_img=False):
        
        self.graph = nx.Graph()
        self.graph.add_node(0, pos=(0, 0))
        self.idx = 1
        self.create_complex_graph_world()

        # this is the map we use to emulate the local grid, not the one used by the gui.
        full_path = os.path.join('resource', 'villa_holes_closed.png')
        upside_down_map_img = Image.open(full_path)
        self.map_img = img_axes2world_axes(upside_down_map_img)

    def create_path_graph_world(self):
        structure = [(4, 0), (7, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, -1), (8, -1),
                     (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]

        for wp in structure:
            self.graph.add_node(self.idx, pos=wp)
            self.graph.add_edge(self.idx, self.idx-1)
            self.idx += 1

    def create_complex_graph_world(self):
        living = [(12.5, 0), (15, 3), (17.5, 0), (17.5, -4), (17.5, -8),
                  (17.5, -12), (12.5, -12), (12.5, -8), (12.5, -4)]
        hall = [(4, 0), (8, -1), (7,3), (4, 6), (0, 6), (-4, 6),
                (-8, 6), (-12, 6), (-16, 6), (-16, 11)]
        hall_init = False
        living_init = False
        for wp in hall:
            if hall_init:
                self.graph.add_node(self.idx, pos=wp)
                self.graph.add_edge(self.idx, self.idx-1)
                self.idx += 1
            else:
                self.graph.add_node(self.idx, pos=wp)
                self.idx += 1
                hall_init = True

        self.graph.add_edge(0, 1)  # connect start to the hall
        self.graph.add_edge(1, 3) # make cyclic the start
        for wp in living:
            if living_init:
                self.graph.add_node(self.idx, pos=wp)
                self.graph.add_edge(self.idx, self.idx-1)
                self.idx += 1
            else:
                self.graph.add_node(self.idx, pos=wp)
                self.idx += 1
                living_init = True

        # make the living dense
        self.graph.add_edge(11, 13)  
        self.graph.add_edge(19, 14)  
        self.graph.add_edge(18, 15)  

        self.graph.add_edge(11, 14)
        self.graph.add_edge(13, 19)
        self.graph.add_edge(19, 15)
        self.graph.add_edge(14, 18)
        self.graph.add_edge(16, 18)
        self.graph.add_edge(15, 17)


        self.graph.add_edge(19, 11) # make cyclic the living
        self.graph.add_edge(2, 11) # connect living to hall

        # add the kitchen nodes
        self.graph.add_node(self.idx, pos=(7, -5))
        self.graph.add_edge(1, self.idx)
        self.idx += 1
        self.graph.add_node(self.idx, pos=(6, -9))
        self.graph.add_edge(self.idx, self.idx-1)
        self.idx += 1
        self.graph.add_node(self.idx, pos=(5, -12))
        self.graph.add_edge(self.idx, self.idx-1)
        self.idx += 1

        # add the small room nodes
        self.graph.add_node(self.idx, pos=(-9, 10))
        self.graph.add_edge(self.idx, 7) # connect left small room to hall
        self.idx += 1
        self.graph.add_node(self.idx, pos=(-7, 12))
        self.graph.add_edge(self.idx, self.idx-1)
        self.idx += 1
        #
        self.graph.add_node(self.idx, pos=(-2, 10))
        self.graph.add_edge(self.idx, 5) # connect right small room to hall
        self.idx += 1
        self.graph.add_node(self.idx, pos=(2, 12))
        self.graph.add_edge(self.idx, self.idx-1)
        self.idx += 1

        # HACK: add the world objects
        self.graph.nodes[10]["world_object_dummy"] = "victim1" # top left room
        self.graph.nodes[10]["world_object_pos_dummy"] = (-13.5, 13)

        self.graph.nodes[17]["world_object_dummy"] = "victim2" # living
        self.graph.nodes[17]["world_object_pos_dummy"] = (11, -14)

        self.graph.nodes[22]["world_object_dummy"] = "victim3" # kitchen
        self.graph.nodes[22]["world_object_pos_dummy"] = (8, -14)

    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.graph.nodes():
            if self.graph.nodes[node]['pos'] == pos:
                return node

class LatticeWorld():
    def __init__(self):
        N = 10
        M = 10
        self.world = nx.generators.lattice.grid_2d_graph(N, M, periodic=False)
        for node in self.world.nodes():
            self.world.nodes[node]["pos"] = (node[0], node[1])

    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.world.nodes():
            if self.world.nodes[node]['pos'] == pos:
                return node

if __name__ == '__main__':
    pass
