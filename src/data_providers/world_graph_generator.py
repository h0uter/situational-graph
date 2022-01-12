import networkx as nx

class GraphGenerator():
    def __init__(self) -> None:
        pass

    def generate_graph(self, num_nodes: int) -> nx.Graph:
        graph = nx.Graph()

        for i in range(num_nodes):
            if i == 0:
                graph.add_node(0, pos=(0, 0))
            else:
                # sample 4 meters away from any existing waypoint.
                # lets just start in 1D
                
                old_pos = graph.nodes[i-1]['pos']
                print(old_pos)
                new_x = old_pos[0] + 4
                new_y = old_pos[1] + 0
                # new_pos = list(old_pos) + list((4,0))
                new_pos = (new_x, new_y)
                
                graph.add_node(i, pos=new_pos)
                graph.add_edge(i, i-1)

        return graph
