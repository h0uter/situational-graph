import networkx as nx
import pylab
import matplotlib.pyplot as plt

def main():
    tail = [0, 2, 4, 5, 6, 8, 9, 11, 13, 1, 10, 1, 3, 7]
    head = [1, 3, 3, 1, 7, 7, 10, 12, 12, 14, 14, 12, 14, 10]
    ed_ls = [(x, y) for x, y in zip(tail, head)]
    G = nx.Graph()
    G.add_nodes_from(range(100, 110))
    G.add_edges_from(ed_ls)
    # G = nx.complete_graph(5)

    nx.draw(G)
    plt.show()

if __name__ == '__main__':
    main()
