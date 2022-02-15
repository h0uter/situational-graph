from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.utils.saving_objects import load_something
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.abstract_agent import AbstractAgent
from src.entities.local_grid import LocalGrid


from src.utils.config import Config
import networkx as nx

import vedo
import time

vedo.settings.allowInteraction = True


class VedoVisualisation(AbstractVizualisation):
    def __init__(self, cfg: Config) -> None:
        # pass
        self.cfg = cfg
        self.factor = 1/self.cfg.LG_CELL_SIZE_M
        # self.plt = vedo.Plotter(axes=13, sharecam=False, interactive=False)
        self.plt = vedo.Plotter(axes=13, sharecam=True)
        self.plt.addLegendBox()
        # self.plt.addHoverLegend()
        map_pic = vedo.Picture(cfg.FULL_PATH)
        # map_mesh = map_pic.threshold(0.8)
        # map_mesh = map_pic.tomesh()
        # map_pic.extent(
        #     # ext=[-int(cfg.TOT_MAP_LEN_M_X // 2), int(cfg.TOT_MAP_LEN_M_X // 2),
        #     ext=[-int(cfg.TOT_MAP_LEN_M_Y // 2), int(cfg.TOT_MAP_LEN_M_Y // 2),
        #         #  -int(cfg.TOT_MAP_LEN_M_Y // 2), int(cfg.TOT_MAP_LEN_M_Y // 2)]
        #          -int(cfg.TOT_MAP_LEN_M_X // 2), int(cfg.TOT_MAP_LEN_M_X // 2)]
        # )
        # map_pic.extent(
        #     # ext=[-int(cfg.TOT_MAP_LEN_M_X // 2), int(cfg.TOT_MAP_LEN_M_X // 2),
        #     ext=[0, int(cfg.TOT_MAP_LEN_M_X),
        #         #  -int(cfg.TOT_MAP_LEN_M_Y // 2), int(cfg.TOT_MAP_LEN_M_Y // 2)]
        #          0, int(cfg.TOT_MAP_LEN_M_Y)]
        # )
        # map_pic.x(-cfg.TOT_MAP_LEN_M_X//2).y(-cfg.TOT_MAP_LEN_M_Y//2)
        map_pic.x(-cfg.IMG_TOTAL_X_PIX//2).y(-cfg.IMG_TOTAL_Y_PIX//2)
        # map_pic.resize(0.038)
        # print(cfg.LG_CELL_SIZE_M)
        # map_pic.resize(cfg.LG_CELL_SIZE_M)
        self.plt.show(map_pic, interactive=False)
        # self.plt.show(map_mesh, interactive=False)
        # self.plt.render()
        # self.plt.show(interactive=False)
        time.sleep(2)

    def figure_update(
        self, krm: KnowledgeRoadmap, agent: AbstractAgent, lg: LocalGrid
    ) -> None:
        # self.plt = vedo_krm(krm, agent, self.cfg)
        self.plt = self.viz_all(krm, agent, self.cfg)

    def viz_all(self, krm, agent, cfg):

        positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
        pos_dict = positions_of_all_nodes
        for pos in pos_dict:
            
            # pos_dict[pos] = pos_dict[pos]*100
            pos_dict[pos] = tuple([self.factor*x for x in pos_dict[pos]])
            print(pos_dict[pos])

        ed_ls = list(krm.graph.edges)

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

        # FIXME: make this list comprehensions
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
        agent_sphere = vedo.Point([self.factor*agent.pos[0], self.factor*agent.pos[1], 0], r=25, c="b")
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
        # self.plt.clear()

        if len(ed_ls) > 1:
            # plt = self.plt.show(
            #     agent_sphere, waypoints, waypoints.labels('id'), frontiers, raw_edg, interactive=False
            # )
            plt = vedo.show(
                agent_sphere, waypoints, frontiers, raw_edg, interactive=False
            )
            # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, raw_edg, interactive=False)
            # plt = vedo.show(map_pic, interactive=False)
        else:
            plt = vedo.show(agent_sphere, waypoints, frontiers, interactive=False)
            # plt = self.plt.show(agent_sphere, waypoints, waypoints.labels('id'), frontiers, interactive=False)
            # plt = vedo.show(map_pic, agent_sphere, waypoints, frontiers, interactive=False)
            # plt = vedo.show(map_pic, interactive=False)
        # if plt.escaped: break  # if ESC is hit during loop
        
        # self.plt.addLegendBox()

        # time.sleep(1)
        # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
        return plt
