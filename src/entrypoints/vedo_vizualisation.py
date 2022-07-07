import os
import time
from typing import Sequence, Union

import networkx as nx
import numpy as np
import vedo

from src.entities.abstract_agent import AbstractAgent
from src.entities.tosg import TOSG
from src.entities.local_grid import LocalGrid
from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.usecases.planning_pipeline import PlanningPipeline
from src.utils.config import Config, PlotLvl, Scenario
from src.utils.my_types import NodeType


# vedo colors: https://htmlpreview.github.io/?https://github.com/Kitware/vtk-examples/blob/gh-pages/VTKNamedColorPatches.html
vedo.settings.allowInteraction = True


class VedoVisualisation(AbstractVizualisation):
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.factor = 1 / self.cfg.LG_CELL_SIZE_M

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title="Knowledge Roadmap",
            size=(3456, 2234),
        )

        # NOTE: perhaps I just should not instantiate viz classes if we run headless
        if self.cfg.PLOT_LVL is not PlotLvl.NONE:
            if self.cfg.SCENARIO is not Scenario.REAL:
                map_pic = vedo.Picture(cfg.FULL_PATH)
                map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
                self.plt.show(map_pic, interactive=False)

            logo_path = os.path.join("resource", "KRM.png")
            logo = vedo.load(logo_path)
            self.plt.addIcon(logo, pos=1, size=0.15)

        self.debug_actors = list()
        self.wp_counter = []
        self.ft_counter = []

        self.annoying_captions = list()

        time.sleep(0.1)

    def figure_update(
        self,
        krm: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[PlanningPipeline],
    ) -> None:
        self.viz_all(krm, agents, usecases)

    def figure_final_result(
        self,
        krm: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases,
    ) -> None:
        self.viz_all(krm, agents)
        self.plt.show(interactive=True, resetcam=True)

    def get_nodes_by_type(self, krm, node_type):
        return list(
            dict(
                (n, d["type"])
                for n, d in krm.graph.nodes().items()
                if d["type"] == node_type
            ).keys()
        )

    def get_scaled_pos_dict(self, krm) -> dict:
        positions_of_all_nodes = nx.get_node_attributes(krm.graph, "pos")
        pos_dict = positions_of_all_nodes

        # scale the sizes to the scale of the simulated map image
        for pos in pos_dict:
            pos_dict[pos] = tuple([self.factor * x for x in pos_dict[pos]])

        return pos_dict

    def viz_all(self, krm, agents, usecases=None):
        actors = []
        pos_dict = self.get_scaled_pos_dict(krm)
        ed_ls = list(krm.graph.edges)

        # TODO: implement coloration for the different line types
        if len(ed_ls) > 1:
            raw_lines = [
                (pos_dict[node_a], pos_dict[node_b]) for node_a, node_b, _ in ed_ls
            ]
            raw_edg = vedo.Lines(raw_lines).lw(2)
            actors.append(raw_edg)

        waypoint_nodes = self.get_nodes_by_type(krm, NodeType.WAYPOINT)
        wps = [pos_dict[wp] for wp in waypoint_nodes]
        self.wp_counter.append(len(wps))
        # waypoints = vedo.Points(wps, r=8, c="r")
        waypoints = vedo.Points(wps, r=8, c="FireBrick")
        actors.append(waypoints)

        frontier_nodes = self.get_nodes_by_type(krm, NodeType.FRONTIER)
        fts = [pos_dict[f] for f in frontier_nodes]
        self.ft_counter.append(len(fts))
        frontiers = vedo.Points(fts, r=40, c="g", alpha=0.2)
        actors.append(frontiers)

        world_object_nodes = self.get_nodes_by_type(krm, NodeType.WORLD_OBJECT)
        actors = self.add_world_object_nodes(world_object_nodes, actors, pos_dict)
        actors = self.add_agents(agents, actors)

        if usecases is not None:
            self.viz_action_graph(actors, krm, usecases, pos_dict)

        # TODO: add legend
        # lbox = vedo.LegendBox([world_objects], width=0.25)
        # actors.append(lbox)

        if self.debug_actors:
            actors.extend(self.debug_actors)

        self.plt.show(
            actors,
            # rate=15 # limit rendering
        )
        self.plt.render()  # this makes it work with REAL scenario
        self.clear_annoying_captions()

    def clear_annoying_captions(self):
        """Captions apparently are persistent, so we need to clear them."""
        self.plt.clear(self.annoying_captions)
        self.annoying_captions = list()

    def viz_action_graph(
        self,
        actors: list,
        krm: TOSG,
        usecases: Sequence[PlanningPipeline],
        pos_dict: dict,
    ):
        # FIXME: this is way too high in real scenario
        action_path_offset = self.factor * 5

        for mission in usecases:
            if mission.plan.valid:
                action_path = mission.plan.edge_sequence

                # HACK TO fix crash caused by frontier already being removed from krm by one agent in final step
                # for node in action_path:
                #     if node not in pos_dict:
                #         return
                for edge in action_path:
                    for node in edge:
                        if node not in pos_dict:
                            return

                # TODO: make it actually plot based on type of action
                # ed_ls = [action_path[i : i + 2] for i in range(len(action_path) - 1)]
                ed_ls = action_path
                # raw_lines = [(pos_dict[x], pos_dict[y]) for x, y in ed_ls]
                raw_lines = [
                    (pos_dict[node_a], pos_dict[node_b]) for node_a, node_b, _ in ed_ls
                ]
                frontier_edge = raw_lines.pop()
                wp_edge_actors = (
                    vedo.Lines(raw_lines, c="r", alpha=0.5).lw(10).z(action_path_offset)
                )
                actors.append(wp_edge_actors)

                arrow_start = (frontier_edge[0][0], frontier_edge[0][1], 0)
                arrow_end = (frontier_edge[1][0], frontier_edge[1][1], 0)
                ft_edge_actor = vedo.Arrow(
                    arrow_start, arrow_end, c="g", s=self.factor * 0.037
                ).z(action_path_offset)
                actors.append(ft_edge_actor)

    def add_agents(self, agents, actors):
        for agent in agents:
            agent_pos = (self.factor * agent.pos[0], self.factor * agent.pos[1], 0)
            grid_len = self.factor * self.cfg.LG_LENGTH_IN_M
            local_grid_viz = vedo.Grid(
                pos=agent_pos, sx=grid_len, sy=grid_len, lw=2, alpha=0.3
            )
            actors.append(local_grid_viz)

            agent_dir_vec = (np.cos(agent.heading), np.sin(agent.heading), 0)

            cone_r = self.factor * 1.35
            cone_height = self.factor * 3.1
            # FIXME: this is inconsistent
            if self.cfg.SCENARIO == Scenario.REAL:
                cone_r *= 0.4
                cone_height *= 0.4

            agent_actor = vedo.Cone(agent_pos, r=cone_r, height=cone_height, axis=agent_dir_vec, c="dodger_blue", alpha=0.7, res=3)  # type: ignore
            agent_label = f"Agent {agent.name}"
            agent_actor.caption(agent_label, size=(0.05, 0.025))
            actors.append(agent_actor)
            self.annoying_captions.append(agent_actor._caption)

        return actors

    def add_world_object_nodes(self, world_object_nodes, actors, pos_dict):
        for wo in world_object_nodes:
            wo_pos = pos_dict[wo]
            wo_point = vedo.Point(wo_pos, r=20, c="magenta")
            actors.append(wo_point)

            wo_vig = wo_point.vignette(
                wo,
                offset=[0, 0, 5 * self.factor],
                s=self.factor,
            )
            actors.append(wo_vig)

        return actors

    def viz_start_point(self, pos):
        point = vedo.Point(
            (pos[0] * self.factor, pos[1] * self.factor, 0), r=35, c="blue"
        )
        print(f"adding point {pos} to debug actors")
        self.debug_actors.append(point)

        # FIXME: this is way to big in real scenario
        start_vig = point.vignette(
            "Start",
            offset=[0, 0, 5 * self.factor],
            s=self.factor,
        )
        self.debug_actors.append(start_vig)
