from src.utils.saving_objects import load_something
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.abstract_agent import AbstractAgent
from src.entities.local_grid import LocalGrid


from src.utils.config import Config
import networkx as nx

# from vedo import Points, show
import vedo
import time

vedo.settings.allowInteraction = True


class VedoVisualisation:
    def __init__(self, cfg: Config) -> None:
        # pass
        self.cfg = cfg
        self.plt = vedo.Plotter(axes=13)
        self.plt.render()
        time.sleep(2)

    def figure_update(self, krm: KnowledgeRoadmap, agent: AbstractAgent, lg: LocalGrid) -> None:
        # self.plt = vedo_krm(krm, agent, self.cfg)
        self.plt = self.viz_all(krm, agent, self.cfg)

    def viz_all(self, krm, agent, cfg):
            
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
        waypoint_nodes = list(
            dict(
                (n, d["type"])
                for n, d in krm.graph.nodes().items()
                if d["type"] == "waypoint"
            ).keys()
        )

        # print(f"waypoint_nodes = {waypoint_nodes}")
        frontier_nodes = list(
            dict(
                (n, d["type"])
                for n, d in krm.graph.nodes().items()
                if d["type"] == "frontier"
            ).keys()
        )

        wps = []
        for wp in waypoint_nodes:
            wps.append(pos_dict[wp])

        fts = []
        for f in frontier_nodes:
            fts.append(pos_dict[f])

        # print(f"frontier_nodes = {frontier_nodes}")
        waypoints = vedo.Points(wps, r=12, c="r")
        # waypoints = vedo.Points(list(waypoint_nodes), r=12, c='r')
        frontiers = vedo.Points(fts, r=45, c="g", alpha=0.2)
        # vedo.clear()
        # plt.show(raw_pts, raw_pts.labels('id'))
        # plt = vedo.show(raw_pts, interactive=False)
        agent_sphere = vedo.Point([agent.pos[0], agent.pos[1], 0], r=25, c="b")
        # print(f"cfg.TOT_MAP_LEN X = {cfg.TOT_MAP_LEN_M_X//2}, cfg.TOT_MAP_LEN_Y = {cfg.TOT_MAP_LEN_M_Y//2}")
        # map_pic = vedo.Picture(cfg.FULL_PATH)
        # map_pic.extent(
        #     ext=[int(-cfg.TOT_MAP_LEN_M_X // 2), int(cfg.TOT_MAP_LEN_M_X // 2),
        #     int(-cfg.TOT_MAP_LEN_M_Y // 2), int(cfg.TOT_MAP_LEN_M_Y // 2)]
        # )
        # map_pic.extent(
        #     ext=[0, 3998, 0, 1998]
        # )
        # map_pic.x(-cfg.TOT_MAP_LEN_M_X//2).y(-cfg.TOT_MAP_LEN_M_Y//2)
        # map_pic.resize(0.038)
        # print(map_pic.extent())

        if len(ed_ls) > 1:
            plt = vedo.show(agent_sphere, waypoints, frontiers, raw_edg, interactive=False)
            # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, raw_edg, interactive=False)
            # plt = vedo.show(map_pic, interactive=False)
        else:
            plt = vedo.show(agent_sphere, waypoints, frontiers, interactive=False)
            # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, interactive=False)
            # plt = vedo.show(map_pic, interactive=False)
        # if plt.escaped: break  # if ESC is hit during loop

        # time.sleep(1)
        # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
        return plt




# Old functions

def main():
    krm: KnowledgeRoadmap = load_something("krm_1302.p")

    print(krm.graph)
    vedo_krm(krm)


def vedo_krm(krm, agent, cfg: Config):

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
    waypoint_nodes = list(
        dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "waypoint"
        ).keys()
    )

    # print(f"waypoint_nodes = {waypoint_nodes}")
    frontier_nodes = list(
        dict(
            (n, d["type"])
            for n, d in krm.graph.nodes().items()
            if d["type"] == "frontier"
        ).keys()
    )

    wps = []
    for wp in waypoint_nodes:
        wps.append(pos_dict[wp])

    fts = []
    for f in frontier_nodes:
        fts.append(pos_dict[f])

    # print(f"frontier_nodes = {frontier_nodes}")
    waypoints = vedo.Points(wps, r=12, c="r")
    # waypoints = vedo.Points(list(waypoint_nodes), r=12, c='r')
    frontiers = vedo.Points(fts, r=45, c="g", alpha=0.2)
    # vedo.clear()
    # plt.show(raw_pts, raw_pts.labels('id'))
    # plt = vedo.show(raw_pts, interactive=False)
    agent_sphere = vedo.Point([agent.pos[0], agent.pos[1], 0], r=25, c="b")
    # print(f"cfg.TOT_MAP_LEN X = {cfg.TOT_MAP_LEN_M_X//2}, cfg.TOT_MAP_LEN_Y = {cfg.TOT_MAP_LEN_M_Y//2}")
    # map_pic = vedo.Picture(cfg.FULL_PATH)
    # map_pic.extent(
    #     ext=[int(-cfg.TOT_MAP_LEN_M_X // 2), int(cfg.TOT_MAP_LEN_M_X // 2),
    #     int(-cfg.TOT_MAP_LEN_M_Y // 2), int(cfg.TOT_MAP_LEN_M_Y // 2)]
    # )
    # map_pic.extent(
    #     ext=[0, 3998, 0, 1998]
    # )
    # map_pic.x(-cfg.TOT_MAP_LEN_M_X//2).y(-cfg.TOT_MAP_LEN_M_Y//2)
    # map_pic.resize(0.038)
    # print(map_pic.extent())

    if len(ed_ls) > 1:
        plt = vedo.show(agent_sphere, waypoints, frontiers, raw_edg, interactive=False)
        # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, raw_edg, interactive=False)
        # plt = vedo.show(map_pic, interactive=False)
    else:
        plt = vedo.show(agent_sphere, waypoints, frontiers, interactive=False)
        # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, interactive=False)
        # plt = vedo.show(map_pic, interactive=False)
    # if plt.escaped: break  # if ESC is hit during loop

    # time.sleep(1)
    # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
    return plt


if __name__ == "__main__":
    main()
