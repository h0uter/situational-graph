import networkx as nx
import matplotlib.pyplot as plt
from numpy.core.shape_base import block

class GraphWorld():
    def __init__(self):
        self.structure = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, -1), (8, -1),
                          (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]
        
        self.world = nx.Graph()

        # TODO:: find a cleaner way to init graph world
        self.world.add_node(0, pos=(0,0))
        self.idx = 1
        for wp in self.structure:
            self.world.add_node(self.idx, pos=wp)
            self.world.add_edge(self.idx, self.idx-1)
            self.idx += 1

        # add the kitchen nodes
        self.world.add_node(self.idx, pos=(6, -5))
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
        self.world.add_edge(self.idx, 16)
        self.idx += 1
        self.world.add_node(self.idx, pos=(-8, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1
        # 
        self.world.add_node(self.idx, pos=(2, 10))
        self.world.add_edge(self.idx, 14)
        self.idx += 1
        self.world.add_node(self.idx, pos=(-2, 13))
        self.world.add_edge(self.idx, self.idx-1)
        self.idx += 1


        # self.init_plot()
    def get_node_by_pos(self, pos):
        ''' returns the node at the given position
        
        returns
        '''
        for node in self.world.nodes():
            if self.world.nodes[node]['pos'] == pos:
                return node

    def init_plot(self):
        ''' initializes the plot'''
        plt.ion()
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
        # nx.draw(self.world, pos=nx.get_node_attributes(self.world, 'pos'))

        nx.draw_networkx_nodes(self.world, pos=nx.get_node_attributes(self.world, 'pos'),
                ax=self.ax, node_color='grey')
        nx.draw_networkx_edges(
            self.world, pos=nx.get_node_attributes(self.world, 'pos'), ax=self.ax, edge_color='grey')
        nx.draw_networkx_labels(self.world, pos=nx.get_node_attributes(
            self.world, 'pos'), ax=self.ax, font_size=10)
        plt.axis('on')
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)
        plt.draw()

    # def observe(self, agent_at_wp):
    #     ''' 
    #     returns measurement of the world
    #     '''
    #     # HACK:: the GraphWorld nodes which can be observed from the current agent state
    #     observable_nodes = self.world.neighbors(agent_at_wp)
    #     return observable_nodes

class GraphWorldLoops():
    def __init__(self):
        self.structure = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, 0), (8, 0),
                          (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]
        
        self.world = nx.generators.navigable_small_world_graph(5)
        nx.draw(self.world)
        plt.show()


if __name__ == '__main__':

    gw = GraphWorldLoops()
