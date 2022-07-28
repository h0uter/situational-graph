import os
import time
from typing import Sequence, Union

import networkx as nx
import numpy as np
import vedo
from vedo import io

from src.domain.services.abstract_agent import AbstractAgent
from src.domain import TOSG, ObjectTypes, LocalGrid, OfflinePlanner
from src.domain.entities.node_and_edge import Node
from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.configuration.config import cfg, PlotLvl, Scenario


# vedo colors: https://htmlpreview.github.io/?https://github.com/Kitware/vtk-examples/blob/gh-pages/VTKNamedColorPatches.html
vedo.settings.allowInteraction = True


class VedoVisualisation(AbstractVizualisation):
    def __init__(self) -> None:
        self.factor = 1 / cfg.LG_CELL_SIZE_M

        TITLE = f"{cfg.SCENARIO} - {cfg.PLOT_LVL}"

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            resetcam=True,
            title=TITLE,
            # size=(3456, 2234),
            size=(3456, 2000),
        )
        self.map_actor = None

        # NOTE: perhaps I just should not instantiate viz classes if we run headless
        if cfg.PLOT_LVL is not PlotLvl.NONE:
            if cfg.SCENARIO is not Scenario.REAL:
                self.set_map(cfg.MAP_PATH)
                # map_pic = vedo.Picture(cfg.MAP_PATH)
                # map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
                # self.plt.show(map_pic, interactive=False)

            logo_path = os.path.join("resource", "KRM.png")
            logo = vedo.load(logo_path)
            self.plt.addIcon(logo, pos=1, size=0.15)

        self.debug_actors = list()
        self.wp_counter = []
        self.ft_counter = []

        self.actors_which_need_to_be_cleared = list()

        time.sleep(0.1)

    def set_map(self, map_path: str) -> None:
        if cfg.SCENARIO is not Scenario.REAL:
            if self.map_actor:
                self.plt.clear([self.map_actor])

            map_pic = vedo.Picture(map_path)
            map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
            self.map_actor = map_pic
            self.plt.add(self.map_actor)

    def figure_update(
        self,
        tosg: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[OfflinePlanner],
    ) -> None:
        self.viz_all(tosg, agents, usecases)

    def figure_final_result(
        self,
        tosg: TOSG,
        agents: Sequence[AbstractAgent],
        lg: Union[None, LocalGrid],
        usecases: Sequence[OfflinePlanner],
    ) -> None:
        self.viz_all(tosg, agents)
        self.plt.show(interactive=True, resetcam=True)

    def get_scaled_pos_dict(self, tosg: TOSG) -> dict:
        positions_of_all_nodes = nx.get_node_attributes(tosg.G, "pos")
        pos_dict = positions_of_all_nodes

        # scale the sizes to the scale of the simulated map image
        for pos in pos_dict:
            pos_dict[pos] = tuple([self.factor * x for x in pos_dict[pos]])

        return pos_dict

    def viz_all(self, tosg: TOSG, agents, usecases=None):
        actors = []
        pos_dict = self.get_scaled_pos_dict(tosg)
        ed_ls = list(tosg.G.edges)

        # TODO: implement coloration for the different line types
        if len(ed_ls) > 1:
            raw_lines = [
                (pos_dict[node_a], pos_dict[node_b]) for node_a, node_b, _ in ed_ls
            ]
            raw_edg = vedo.Lines(raw_lines).lw(2)
            actors.append(raw_edg)

        waypoint_nodes = tosg.get_nodes_by_type(ObjectTypes.WAYPOINT)
        wps = [pos_dict[wp] for wp in waypoint_nodes]
        self.wp_counter.append(len(wps))
        # waypoints = vedo.Points(wps, r=8, c="r")
        waypoints = vedo.Points(wps, r=15, c="FireBrick")
        actors.append(waypoints)

        frontier_nodes = tosg.get_nodes_by_type(ObjectTypes.FRONTIER)
        fts = [pos_dict[f] for f in frontier_nodes]
        self.ft_counter.append(len(fts))
        frontiers = vedo.Points(fts, r=40, c="g", alpha=0.2)
        actors.append(frontiers)

        # world_object_nodes = self.get_nodes_by_type(krm, ObjectTypes.WORLD_OBJECT)
        # HACK: we need this to extend to new world objects.
        world_object_nodes = tosg.get_nodes_by_type(ObjectTypes.UNKNOWN_VICTIM)
        world_object_nodes.extend(
            tosg.get_nodes_by_type(ObjectTypes.IMMOBILE_VICTIM)
        )
        world_object_nodes.extend(
            tosg.get_nodes_by_type(ObjectTypes.MOBILE_VICTIM)
        )
        actors = self.add_world_object_nodes(world_object_nodes, actors, pos_dict, tosg)
        actors = self.add_agents(agents, actors)

        if usecases is not None:
            self.viz_action_graph(actors, tosg, usecases, pos_dict, agents)

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
        self.plt.clear(self.actors_which_need_to_be_cleared)
        self.actors_which_need_to_be_cleared = list()

    def viz_action_graph(
        self,
        actors: list,
        krm: TOSG,
        usecases: Sequence[OfflinePlanner],
        pos_dict: dict,
        agents: Sequence[AbstractAgent],
    ):
        # FIXME: this is way too high in real scenario
        action_path_offset = self.factor * 5

        # for mission in usecases:
        #     if mission.plan:
        for agent in agents:
            if agent.plan:
                action_path = agent.plan.edge_sequence

                # HACK TO fix crash caused by frontier already being removed from krm by one agent in final step
                for edge in action_path:
                    for node in edge[1:2]:  # in source or target node
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
            grid_len = self.factor * cfg.LG_LENGTH_IN_M
            local_grid_viz = vedo.Grid(
                pos=agent_pos, sx=grid_len, sy=grid_len, lw=2, alpha=0.3
            )
            actors.append(local_grid_viz)

            agent_dir_vec = (np.cos(agent.heading), np.sin(agent.heading), 0)

            cone_r = self.factor * 1.35
            cone_height = self.factor * 3.1
            # FIXME: this is inconsistent
            if cfg.SCENARIO == Scenario.REAL:
                cone_r *= 0.4
                cone_height *= 0.4

            agent_actor = vedo.Cone(agent_pos, r=cone_r, height=cone_height, axis=agent_dir_vec, c="dodger_blue", alpha=0.7, res=3)  # type: ignore
            agent_label = f"Agent {agent.name}"
            agent_actor.caption(agent_label, size=(0.05, 0.025))

            if agent.task:
                task_print = (
                    str(agent.task.objective_enum)
                    .removeprefix("Objectives.")
                    .replace("_", " ")
                    .rjust(25)
                )
                agent_actor.legend(f"{task_print}")
            else:
                # agent_actor.legend(f"{agent.task}")
                agent_actor.legend(f"No task selected".rjust(25))

            # actors.append(agent_actor)
            # lbox = vedo.LegendBox([agent_actor], width=0.25)
            lbox = vedo.LegendBox([agent_actor], width=0.5)
            actors.append(lbox)
            self.actors_which_need_to_be_cleared.append(lbox)

            actors.append(agent_actor)
            self.actors_which_need_to_be_cleared.append(agent_actor._caption)

        return actors

    def add_world_object_nodes(
        self, world_object_nodes: Sequence, actors, pos_dict, tosg
    ):
        node_type_dict = nx.get_node_attributes(tosg.G, "type")
        for wo in world_object_nodes:
            wo_pos = pos_dict[wo]
            wo_point = vedo.Point(wo_pos, r=20, c="magenta")
            actors.append(wo_point)
            name_str = (
                str(node_type_dict[wo]).removeprefix("ObjectTypes.").replace("_", "\n")
            )
            # instead of trowing the ID in the vignette We would like their objecttype
            wo_vig = wo_point.vignette(
                # wo,
                name_str,
                offset=[0, 0, 5 * self.factor],
                s=self.factor * 0.7,
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

    def take_screenshot(self):
        path = "results/test.png"
        io.screenshot(path)
