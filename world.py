import networkx as nx
import matplotlib.pyplot as plt
from numpy.core.shape_base import block

class ManualGraphWorld():
    def __init__(self, debug=False):
        self.world = nx.Graph()
        self.world.add_node(0, pos=(0, 0))
        self.idx = 1
        self.create_complex_graph_world()

        if debug:
            self.init_plot()

    def create_path_graph_world(self):
        structure = [(4, 0), (7, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, -1), (8, -1),
                     (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]

        # TODO:: find a cleaner way to init graph world
        for wp in structure:
            self.world.add_node(self.idx, pos=wp)
            self.world.add_edge(self.idx, self.idx-1)
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
                self.world.add_node(self.idx, pos=wp)
                self.world.add_edge(self.idx, self.idx-1)
                self.idx += 1
            else:
                self.world.add_node(self.idx, pos=wp)
                self.idx += 1
                hall_init = True

        self.world.add_edge(0, 1)  # connect start to the hall
        self.world.add_edge(1, 3) # make cyclic the start
        for wp in living:
            if living_init:
                self.world.add_node(self.idx, pos=wp)
                self.world.add_edge(self.idx, self.idx-1)
                self.idx += 1
            else:
                self.world.add_node(self.idx, pos=wp)
                self.idx += 1
                living_init = True

        # make the living dense
        self.world.add_edge(11, 13)  
        self.world.add_edge(19, 14)  
        self.world.add_edge(18, 15)  

        self.world.add_edge(11, 14)
        self.world.add_edge(13, 19)
        self.world.add_edge(19, 15)
        self.world.add_edge(14, 18)
        self.world.add_edge(16, 18)
        self.world.add_edge(15, 17)


        self.world.add_edge(19, 11) # make cyclic the living
        self.world.add_edge(2, 11) # connect living to hall

        # add the kitchen nodes
        self.world.add_node(self.idx, pos=(7, -5))
        self.world.add_edge(1, self.idx)
        self.idx += 1
        self.world.add_node(self.idx, pos=(6, -9))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1
        self.world.add_node(self.idx, pos=(6, -13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1

        # add the small room nodes
        self.world.add_node(self.idx, pos=(-9, 10))
        self.world.add_edge(self.idx, 7) # connect left small room to hall
        self.idx += 1
        self.world.add_node(self.idx, pos=(-8, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1
        #
        self.world.add_node(self.idx, pos=(-2, 10))
        self.world.add_edge(self.idx, 5) # connect right small room to hall
        self.idx += 1
        self.world.add_node(self.idx, pos=(2, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1

        # HACK: add the world objects
        self.world.nodes[10]["world_object_dummy"] = "victim1" # top left room
        self.world.nodes[10]["world_object_pos_dummy"] = (-13.5,13)

        self.world.nodes[17]["world_object_dummy"] = "victim2" # living
        self.world.nodes[17]["world_object_pos_dummy"] = (11,-14)

        self.world.nodes[22]["world_object_dummy"] = "victim3" # kitchen
        self.world.nodes[22]["world_object_pos_dummy"] = (8,-14)


    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.world.nodes():
            if self.world.nodes[node]['pos'] == pos:
                return node

    # FIXME: 2 move this method to GUI class
    def init_plot(self):
        ''' initializes the plot'''
        # plt.ion()
        fig, self.ax = plt.subplots(figsize=(10, 10))

        self.img = plt.imread("resource/floor-plan-villa.png")

        self.ax.set_title('GraphWorld simplification of optimal frontiers for exploration')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        self.draw_world()

    # FIXME: 2 move this method to GUI class
    def draw_world(self):
        ''' draws the world '''
        nx.draw_networkx_nodes(
                                self.world, 
                                pos=nx.get_node_attributes(self.world, 'pos'),
                                ax=self.ax, 
                                node_color='grey')
        nx.draw_networkx_edges(
                                self.world, 
                                pos=nx.get_node_attributes(self.world, 'pos'), 
                                ax=self.ax, 
                                edge_color='grey')

        nx.draw_networkx_labels(
                                self.world, 
                                pos=nx.get_node_attributes(self.world, 'pos'), 
                                ax=self.ax, 
                                font_size=10)

        plt.axis('on')
        self.ax.tick_params(left=True, 
                            bottom=True,
                            labelleft=True, 
                            labelbottom=True)
        plt.show()


# TODO: create abstract world class which implements the plot methods
class LatticeWorld():
    def __init__(self):
        N = 10
        M = 10
        self.world = nx.generators.lattice.grid_2d_graph(N, M, periodic=False)
        for node in self.world.nodes():
            self.world.nodes[node]["pos"] = (node[0], node[1])

        self.init_plot()

    # FIXME: 2 move this method to GUI class
    def init_plot(self):
        ''' initializes the plot'''
        # plt.ion()
        fig, self.ax = plt.subplots(figsize=(10, 10))

        self.ax.set_title('LatticeWorld for the agent to explore')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)

        self.draw_world()

    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.world.nodes():
            if self.world.nodes[node]['pos'] == pos:
                return node


    # FIXME: 2 move this method to GUI class
    def draw_world(self):
        ''' draws the world '''
        nx.draw_networkx_nodes(
            self.world,
            pos=nx.get_node_attributes(self.world, 'pos'),
            ax=self.ax,
            node_color='grey',
            node_size=150)

        nx.draw_networkx_edges(
            self.world,
            pos=nx.get_node_attributes(self.world, 'pos'),
            ax=self.ax,
            edge_color='grey')

        nx.draw_networkx_labels(
            self.world,
            pos=nx.get_node_attributes(self.world, 'pos'),
            ax=self.ax,
            font_size=10)

        plt.axis('on')
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)
        plt.show()


if __name__ == '__main__':
    pass
