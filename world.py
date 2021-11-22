import networkx as nx
import matplotlib.pyplot as plt
from numpy.core.shape_base import block

class GraphWorld():
    def __init__(self):
        self.world = nx.Graph()
        self.world.add_node(0, pos=(0, 0))
        self.idx = 1

        # self.create_path_graph_world()
        self.create_complex_graph_world()

        self.init_plot()

    def create_path_graph_world(self):
        structure = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, -1), (8, -1),
                          (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]

        # TODO:: find a cleaner way to init graph world
        for wp in structure:
            self.world.add_node(self.idx, pos=wp)
            self.world.add_edge(self.idx, self.idx-1)
            self.idx += 1

    def create_complex_graph_world(self):
        living = [(12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4)]
        hall = [(4, 0), (8, -1), (5, 6), (0, 6), (-4, 6),
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

        self.world.add_edge(0, 1) # connect start to the hall

        for wp in living:
            if living_init:
                self.world.add_node(self.idx, pos=wp)
                self.world.add_edge(self.idx, self.idx-1)
                self.idx += 1
            else:
                self.world.add_node(self.idx, pos=wp)
                self.idx += 1
                living_init = True
            
        self.world.add_edge(17, 10)
        self.world.add_edge(2, 10)

        # add the kitchen nodes
        self.world.add_node(self.idx, pos=(7, -5))
        self.world.add_edge(1, self.idx)
        self.idx += 1
        self.world.add_node(self.idx, pos=(6, -9))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1
        self.world.add_node(self.idx, pos=(6, -14))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1

        # add the small room nodes
        self.world.add_node(self.idx, pos=(-9, 10))
        self.world.add_edge(self.idx, 6)
        self.idx += 1
        self.world.add_node(self.idx, pos=(-8, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1
        #
        self.world.add_node(self.idx, pos=(-2, 10))
        self.world.add_edge(self.idx, 4)
        self.idx += 1
        self.world.add_node(self.idx, pos=(2, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1


    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.world.nodes():
            if self.world.nodes[node]['pos'] == pos:
                return node

    def init_plot(self):
        ''' initializes the plot'''
        # plt.ion()
        fig, self.ax = plt.subplots(figsize=(10, 10))

        self.img = plt.imread("resource/floor-plan-villa.png")

        self.ax.set_title('GraphWorld for the robot to explore')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        self.draw_world()

    def draw_world(self):
        ''' draws the world '''
        nx.draw_networkx_nodes(self.world, pos=nx.get_node_attributes(self.world, 'pos'),
                ax=self.ax, node_color='grey')
        nx.draw_networkx_edges(
            self.world, pos=nx.get_node_attributes(self.world, 'pos'), ax=self.ax, edge_color='grey')
        nx.draw_networkx_labels(self.world, pos=nx.get_node_attributes(
            self.world, 'pos'), ax=self.ax, font_size=10)
        plt.axis('on')
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)
        plt.show()



class GraphWorldExperiment():
    def __init__(self):
        self.structure = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, 0), (8, 0),
                          (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]
        
        self.world = nx.generators.navigable_small_world_graph(5)
        print(self.world.nodes().data())
        nx.draw(self.world)
        plt.show()


if __name__ == '__main__':

    gw = GraphWorldExperiment()
