import matplotlib.pyplot as plt
import networkx as nx


class GUI():
    def __init__(self):
        # self.init_plot()
        pass


    # FIXME: 2 move this method to GUI class
    def draw_world(self, world):
        ''' draws the world '''

        fig, self.ax = plt.subplots(figsize=(10, 10))

        self.img = plt.imread("resource/floor-plan-villa.png")

        self.ax.set_title('GraphWorld simplification of optimal frontiers for exploration')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        nx.draw_networkx_nodes(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'),
                                ax=self.ax, 
                                node_color='grey')
        nx.draw_networkx_edges(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'), 
                                ax=self.ax, 
                                edge_color='grey')

        nx.draw_networkx_labels(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'), 
                                ax=self.ax, 
                                font_size=10)

        plt.axis('on')
        self.ax.tick_params(left=True, 
                            bottom=True,
                            labelleft=True, 
                            labelbottom=True)
        plt.show()