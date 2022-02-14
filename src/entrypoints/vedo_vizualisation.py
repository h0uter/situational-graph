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
    waypoint_nodes = list(dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "waypoint"
        ).keys())

    # print(f"waypoint_nodes = {waypoint_nodes}")
    frontier_nodes = list(dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "frontier"
        ).keys())

    wps = []
    for wp in waypoint_nodes:
        wps.append(pos_dict[wp])

    fts = []
    for f in frontier_nodes:
        fts.append(pos_dict[f])

    # print(f"frontier_nodes = {frontier_nodes}")
    waypoints = vedo.Points(wps, r=12, c='r')
    # waypoints = vedo.Points(list(waypoint_nodes), r=12, c='r')
    frontiers = vedo.Points(fts, r=45, c='g', alpha=0.2)
    # vedo.clear()
    # plt.show(raw_pts, raw_pts.labels('id'))
    # plt = vedo.show(raw_pts, interactive=False)
    if len(ed_ls) > 1:
        plt = vedo.show(waypoints, frontiers, raw_edg, interactive=False)
    else:
        plt = vedo.show(waypoints, frontiers, interactive=False)
    # if plt.escaped: break  # if ESC is hit during loop

    # time.sleep(1)
    # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
    return plt


if __name__ == "__main__":
    main()
