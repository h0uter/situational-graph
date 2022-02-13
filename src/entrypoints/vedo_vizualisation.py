from src.utils.saving_objects import load_something
from src.entities.knowledge_roadmap import KnowledgeRoadmap

import networkx as nx

# from vedo import Points, show
import vedo
import time

vedo.settings.allowInteraction = True


def main():
    krm: KnowledgeRoadmap = load_something("krm_1302.p")

    print(krm.graph)
    vedo_krm(krm)


def vedo_krm(krm):

    # plt = vedo.Plotter(bg2='lb', interactive=False)
    # plt = vedo.Plotter(interactive=True)
    # plt = vedo.Plotter(interactive=False)
    positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
    pos_dict = positions_of_all_nodes
    # pos_arr = positions_of_all_nodes.values()
    # pos_arr = list(positions_of_all_nodes.values())
    # print(f"positions_of_all_nodes = {pos_dict}")

    # print(krm.graph.edges)
    ed_ls = list(krm.graph.edges)
    # print(f"len ed_ls = {len(ed_ls)}, len pos_arr = {len(pos_arr)}")
    # print(f"ed_ls = {ed_ls}")
    # print(f"pos_arr = {pos_arr}")
    if len(ed_ls) > 1:
        raw_lines = [(pos_dict[x], pos_dict[y]) for x, y in ed_ls]

        raw_edg = vedo.Lines(raw_lines).lw(2)
    raw_pts = vedo.Points(list(pos_dict.values()), r=12)

    # vedo.clear()
    # plt.show(raw_pts, raw_pts.labels('id'))
    # plt = vedo.show(raw_pts, interactive=False)
    if len(ed_ls) > 1:
        plt = vedo.show(raw_pts, raw_edg, interactive=False)
    else:
        plt = vedo.show(raw_pts, interactive=False)
    # if plt.escaped: break  # if ESC is hit during loop

    # time.sleep(1)
    # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
    return plt


if __name__ == "__main__":
    main()
