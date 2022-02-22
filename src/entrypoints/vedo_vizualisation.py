import os
import time
from typing import Sequence

import networkx as nx
import vedo
from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.utils.config import Config, PlotLvl, World

# from src.utils.print_timing import print_timing

# from vedo.pyplot import plot

# vedo colors: https://htmlpreview.github.io/?https://github.com/Kitware/vtk-examples/blob/gh-pages/VTKNamedColorPatches.html

vedo.settings.allowInteraction = True


class VedoVisualisation(AbstractVizualisation):
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.factor = 1 / self.cfg.LG_CELL_SIZE_M
        self.plt = vedo.Plotter(axes=13, sharecam=False, title="Knowledge Roadmap")

        # NOTE: perhaps I just should not instantiate viz classes if we run headless
        if self.cfg.PLOT_LVL is not PlotLvl.NONE:
            if self.cfg.WORLD is not World.REAL:
                map_pic = vedo.Picture(cfg.FULL_PATH)
                map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
                self.plt.show(map_pic, interactive=False)

            logo_path = os.path.join("resource", "KRM.png")
            logo = vedo.load(logo_path)
            self.plt.addIcon(logo, pos=1, size=0.15)

        self.wp_counter = []
        self.ft_counter = []

        time.sleep(0.1)

    def figure_update(
        self, krm: KnowledgeRoadmap, agents: Sequence[AbstractAgent], lg: LocalGrid
    ) -> None:
        self.viz_all(krm, agents)

    def figure_final_result(
        self, krm: KnowledgeRoadmap, agents: Sequence[AbstractAgent], lg: LocalGrid
    ) -> None:
        self.figure_update(krm, agents, lg)
        self.plt.show(interactive=True, resetcam=True)

    # @print_timing
    def viz_all(self, krm, agents):
        actors = []

        positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
        pos_dict = positions_of_all_nodes
        for pos in pos_dict:

            pos_dict[pos] = tuple([self.factor * x for x in pos_dict[pos]])

        ed_ls = list(krm.graph.edges)

        if len(ed_ls) > 1:
            raw_lines = [(pos_dict[x], pos_dict[y]) for x, y in ed_ls]

            raw_edg = vedo.Lines(raw_lines).lw(2)
            actors.append(raw_edg)

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

        world_object_nodes = list(
            dict(
                (n, d["type"])
                for n, d in krm.graph.nodes().items()
                if d["type"] == "world_object"
            ).keys()
        )

        wps = [pos_dict[wp] for wp in waypoint_nodes]
        self.wp_counter.append(len(wps))
        # waypoints = vedo.Points(wps, r=8, c="r")
        waypoints = vedo.Points(wps, r=8, c="FireBrick")
        actors.append(waypoints)

        fts = [pos_dict[f] for f in frontier_nodes]
        self.ft_counter.append(len(fts))
        frontiers = vedo.Points(fts, r=40, c="g", alpha=0.2)
        actors.append(frontiers)

        actors = self.add_world_object_nodes(world_object_nodes, actors, pos_dict)
        actors = self.add_agents(agents, actors)

        # lbox = vedo.LegendBox([world_objects], font="roboto", width=0.25)
        # lbox = vedo.LegendBox([world_objects], width=0.25)
        # actors.append(lbox)

        # print(f"the num of actors is {len(actors)}")

        self.plt.show(
            actors,
            interactive=False,
            # render=False,
            # sharecam=False,
            resetcam=False,
            # at=0
        )

    def add_agents(self, agents, actors):
        for agent in agents:
            agent_pos = [self.factor * agent.pos[0], self.factor * agent.pos[1], 0]
            grid_len = self.factor * self.cfg.LG_LENGTH_IN_M
            local_grid_viz = vedo.Grid(
                pos=agent_pos, sx=grid_len, sy=grid_len, lw=2, alpha=0.3
            )
            actors.append(local_grid_viz)
            # agent_sphere = vedo.Point(agent_pos, r=25, c="b")
            # agent_sphere = vedo.Point(agent_pos, r=25, c="royal_blue")
            agent_sphere = vedo.Point(agent_pos, r=25, c="dodger_blue")
            actors.append(agent_sphere)
            return actors

    def add_world_object_nodes(self, world_object_nodes, actors, pos_dict):
        # world_objects = vedo.Points(wos, r=25, c="p")
        # for world_object in world_objects:

        # world_object.flag("hello world")
        # world_objects.caption("hello world")
        # world_objects.legend("world objects")
        # actors.append(world_objects)

        for wo in world_object_nodes:
            wo_pos = pos_dict[wo]
            wo_point = vedo.Point(wo_pos, r=20, c="magenta")
            # wo_point = vedo.Point(wo_pos, r=20, c="cobalt_violet_deep")
            # wo_point.flag(wo)
            # print(f"wo_pos: {wo_pos}")
            # print(f"wo : {wo}")
            # caption_pos = wo_pos[0], wo_pos[1], 2 * self.factor
            # caption_pos = [0, 0, 2*self.factor]
            # wo_label = wo_point.labels('id', scale=self.factor)
            # wo_label = wo_point.labels(content=[wo], scale=self.factor)
            # wo_cap = wo_point.caption(wo, point=caption_pos, size=(0.05, 0.025), font='VTK')
            
            # wo_point.caption(wo, size=(0.1, 0.05), font="VictorMono", lw=0.5)
            
            # wo_cap = wo_point.caption(wo, size=(0.03, 0.015))
            # wo_cap = wo_point.caption(wo, offset=[0,0, 10*self.factor], size=(0.1, 0.05))
            # wo_vig = wo_point.vignette(wo, point=wo_pos, offset=[0, 0, self.factor], s=self.factor,)
            wo_vig = wo_point.vignette(wo, offset=[0, 0, 5*self.factor], s=self.factor,)
            # wo_cap.z(1*self.factor)
            actors.append(wo_point)
            actors.append(wo_vig)
            # actors.append(wo_cap)
            # actors.append(wo_label)

        return actors

    # def plot_stats(self):
    #     if len(self.wp_counter) > 1 and len(self.ft_counter) > 1:
    #         self.plt.clear(at=1)
    #         plot_wps = plot(self.wp_counter, "r")
    #         plot_wps.overlayPlot(self.ft_counter, "b")
    #         # plot(self.wp_counter, "r").plot(self.ft_counter, "bo-").show(at=1)
    #         # plot(self.wp_counter, "r").plot(self.ft_counter, "bo-").show()
    #         # plot_fts = plot(self.ft_counter)

    #         # plot_wps.x(0.7 * self.cfg.IMG_TOTAL_X_PIX)
    #         # plot_wps.show()
    #         self.plt.add(plot_wps, at=1, render=False)
