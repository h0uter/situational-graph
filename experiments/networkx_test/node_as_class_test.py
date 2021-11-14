import networkx as nx

class point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


G = nx.Graph()
p0 = point(0, 0)
p1 = point(10, 10)

G.add_node(0, data=p0)
G.add_node(1, data=p1)
G.add_edge(0, 1, weight=4)

# print(p0.x)

# print(G.nodes[0])

# so the instantiation of the class is attached to the data attribute of the node
# print(G.nodes[1]['data'].x)

# print(G.add_nodes_from[0].data.x)

H = nx.Graph()

H.add_node(p0)
H.add_node(p1)

print (H.nodes)

for node in H.nodes:
    print (node.x)