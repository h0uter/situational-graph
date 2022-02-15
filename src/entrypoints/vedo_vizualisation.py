from src.entrypoints.abstract_vizualisation import AbstractVizualisation
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
        self.cfg = cfg
        self.factor = 1 / self.cfg.LG_CELL_SIZE_M
        self.plt = vedo.Plotter(axes=13, sharecam=True)
        self.plt.addLegendBox()
        map_pic = vedo.Picture(cfg.FULL_PATH)

        map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
        self.plt.show(map_pic, interactive=False)
        time.sleep(1)

    def figure_update(
        self, krm: KnowledgeRoadmap, agent: AbstractAgent, lg: LocalGrid
    ) -> None:
        self.plt = self.viz_all(krm, agent, self.cfg)

    def viz_all(self, krm, agent, cfg):

        positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
        pos_dict = positions_of_all_nodes
        for pos in pos_dict:

            pos_dict[pos] = tuple([self.factor * x for x in pos_dict[pos]])

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

        waypoints = vedo.Points(wps, r=12, c="r")
        frontiers = vedo.Points(fts, r=45, c="g", alpha=0.2)

        agent_pos = [self.factor * agent.pos[0], self.factor * agent.pos[1], 0]
        grid_len = self.factor * self.cfg.LG_LENGTH_IN_M
        local_grid_viz = vedo.Grid(pos=agent_pos, sx=grid_len, sy=grid_len)
        agent_sphere = vedo.Point(
            agent_pos, r=25, c="b"
        )

        if len(ed_ls) > 1:
            plt = vedo.show(
                agent_sphere,
                waypoints,
                frontiers,
                raw_edg,
                local_grid_viz,
                interactive=False,
                sharecam=False,
            )
        else:
            plt = vedo.show(
                local_grid_viz,
                agent_sphere, waypoints, frontiers, interactive=False, sharecam=False
            )

        # if plt.escaped: break  # if ESC is hit during loop

        # vedo.plotter.show(raw_pts, raw_pts.labels('id'), at=0, N=2, axes=True, sharecam=False, interactive=False, rate=1.0)
        return plt
