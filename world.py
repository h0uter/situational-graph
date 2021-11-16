import networkx as nx
import matplotlib.pyplot as plt
from numpy.core.shape_base import block

class GraphWorld():
    def __init__(self):
        self.structure = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, 0), (8, 0),
                          (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]
        
        self.world = nx.Graph()
        # self.world.add_nodes_from(self.structure)


        self.world.add_node(0, pos=(0,0))
        self.idx = 1
        for wp in self.structure:
            self.world.add_node(self.idx, pos=wp)
            self.world.add_edge(self.idx, self.idx-1)
            self.idx += 1
        # nx.draw(self.world, pos=nx.get_node_attributes(self.world, 'pos'))
        # plt.show()


    def get_local_grid(self, agent_at_wp):
        ''' 
        returns the local-grid aka 
        '''
        # HACK:: the GraphWorld nodes which can be observed from the current agent state
        observable_nodes = self.world.neighbors(agent_at_wp)
        local_grid = observable_nodes
        return local_grid
