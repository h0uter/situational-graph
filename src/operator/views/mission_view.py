import os
import time
from pathlib import Path
from typing import Sequence

import networkx as nx
import numpy as np
import vedo
from vedo import io

from src.config import PlotLvl, Scenario, cfg
from src.core.event_system import subscribe
from src.core.topics import Topics
from src.operator.feedback_pipeline import MissionViewModel
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.shared.prior_knowledge.situations import Situations
from src.shared.situational_graph import SituationalGraph
from src.operator.mission_controller import MissionController
# vedo colors: https://htmlpreview.github.io/?https://github.com/Kitware/vtk-examples/blob/gh-pages/VTKNamedColorPatches.html
vedo.settings.allow_interaction = True


class MissionView:
    def __init__(self) -> None:
        self.factor = 1 / cfg.LG_MTR_PER_CELL
        self.screenshot_step = 0
        TITLE = f"{cfg.SCENARIO} - {cfg.PLOT_LVL}"

        self.plt = vedo.Plotter(
            axes=13,
            interactive=False,
            title=TITLE,
            # size=(3456, 2000),
            pos=(1500, 0),
            size=(2200, 2200),
        )
        self.map_actor = None

        self.debug_actors: list[vedo.BaseActor] = []
        self.actors_which_need_to_be_cleared: list[vedo.BaseActor] = []

        if cfg.SCENARIO is Scenario.REAL:
            self.plt.show(resetcam=True)
        else:
            self.plt.show(resetcam=False)

        # NOTE: perhaps I just should not instantiate viz classes if we run headless
        if cfg.PLOT_LVL is not PlotLvl.NONE:
            if cfg.SCENARIO is not Scenario.REAL:
                self.set_map(cfg.MAP_PATH)

        subscribe(Topics.VIEW__MISSION_START_POINT, self.viz_start_point)

        subscribe(Topics.VIEW__MISSION_UPDATE, self.figure_update)
        subscribe(Topics.VIEW__MISSION_UPDATE_FINAL, self.figure_final_result)

        self.plt.add_callback("LeftButtonPress", self.left_click_callback)

    def left_click_callback(self, event):
        coords = [coord / self.factor for coord in event.picked3d]
        # print("left clicked on: ", coords)
        node_pos = tuple(coords[0:2])
        # my_node = self.tosg.get_node_by_pos(node_pos)
        # my_node = self.tosg.get_nodes_of_type_in_margin(
        #     node_pos, 2, Situations.WAYPOINT
        # )[0]
        my_node = self.tosg._get_closest_waypoint(node_pos)
        print("node: ", my_node, " | pos: ", node_pos)
        # self.plt.render()

        MissionController().add_task_to_queue(my_node)
        self.plt.show(interactive=False)

    def set_map(self, map_path: str) -> None:
        if cfg.SCENARIO is not Scenario.REAL:
            if self.map_actor:
                self.plt.clear([self.map_actor])

            map_pic = vedo.Picture(map_path)
            map_pic.x(-cfg.IMG_TOTAL_X_PIX // 2).y(-cfg.IMG_TOTAL_Y_PIX // 2)
            self.map_actor = map_pic
            self.plt.show(self.map_actor, resetcam=True)

    def figure_update(self, data: MissionViewModel):

        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            self.viz_mission_overview(
                data.situational_graph, data.agents
            )

        if self.plt.escaped:
            exit()

    def figure_final_result(self, data: MissionViewModel):
        self.viz_mission_overview(data.situational_graph, data.agents)
        self.plt.show(interactive=True)

    def viz_mission_overview(
        self, tosg: SituationalGraph, agents: list[AbstractAgent]
    ):
        self.clear_annoying_captions()

        actors: list[vedo.BaseActor] = []
        self.tosg = tosg

        self.plt.clear()
        actors.append(self.map_actor)

        pos_dict = self.get_scaled_pos_dict(tosg)
        ed_ls = list(tosg.G.edges)

        # TODO: implement coloration for the different line types
        if len(ed_ls) > 1:
            raw_lines = [
                (pos_dict[node_a], pos_dict[node_b]) for node_a, node_b, _ in ed_ls
            ]
            raw_edg = vedo.Lines(raw_lines, c="red").lw(5)
            actors.append(raw_edg)

        waypoint_nodes = tosg.get_nodes_by_type(Situations.WAYPOINT)
        wps = [pos_dict[wp] for wp in waypoint_nodes]
        waypoints = vedo.Points(wps, r=35, c="FireBrick")
        actors.append(waypoints)

        frontier_nodes = tosg.get_nodes_by_type(Situations.FRONTIER)
        fts = [pos_dict[f] for f in frontier_nodes]
        frontiers = vedo.Points(fts, r=40, c="g", alpha=0.2)
        actors.append(frontiers)

        # HACK: we need this to extend to new world objects.
        world_object_nodes = tosg.get_nodes_by_type(Situations.UNKNOWN_VICTIM)
        world_object_nodes.extend(tosg.get_nodes_by_type(Situations.IMMOBILE_VICTIM))
        world_object_nodes.extend(tosg.get_nodes_by_type(Situations.MOBILE_VICTIM))
        actors = self.add_world_object_nodes(world_object_nodes, actors, pos_dict, tosg)
        actors = self.add_agents(agents, actors)

        # if usecases is not None:
        #     self.viz_action_graph(actors, tosg, pos_dict, agents)
        self.viz_action_graph(actors, tosg, pos_dict, agents)

        if self.debug_actors:
            actors.extend(self.debug_actors)

        if cfg.SCENARIO is Scenario.REAL:
            self.plt.show(actors, resetcam=True)
        else:
            self.plt.show(actors, resetcam=False)

        self.plt.render()  # ???: this makes it work with REAL scenario somehow

        if cfg.SCREENSHOT:
            self.take_screenshot()  # this makes it take the screenshots

    def clear_annoying_captions(self):
        """Captions apparently are persistent, so we need to clear them."""
        self.plt.clear(self.actors_which_need_to_be_cleared)
        self.actors_which_need_to_be_cleared = list()

    def viz_action_graph(
        self,
        actors: list,
        krm: SituationalGraph,
        pos_dict: dict,
        agents: Sequence[AbstractAgent],
    ):
        # FIXME: this is way too high in real scenario
        ACTION_PATH_OFFSET = self.factor * 5

        for agent in agents:
            if agent.plan:
                action_path = agent.plan.edge_sequence

                # HACK TO fix crash caused by frontier already being removed from krm by one agent in final step
                for edge in action_path:
                    for node in edge[1:2]:  # in source or target node
                        if node not in pos_dict:
                            return

                # TODO: make it actually plot based on type of action
                ed_ls = action_path
                raw_lines = [
                    (pos_dict[node_a], pos_dict[node_b]) for node_a, node_b, _ in ed_ls
                ]
                frontier_edge = raw_lines.pop()
                wp_edge_actors = (
                    vedo.Lines(raw_lines, c="purple", alpha=0.5)
                    .lw(20)
                    .z(ACTION_PATH_OFFSET)
                )
                actors.append(wp_edge_actors)

                arrow_start = (frontier_edge[0][0], frontier_edge[0][1], 0)
                arrow_end = (frontier_edge[1][0], frontier_edge[1][1], 0)
                task_edge_actor = vedo.Arrow(
                    arrow_start, arrow_end, c="g", s=self.factor * 0.037
                ).z(ACTION_PATH_OFFSET)
                actors.append(task_edge_actor)

    def add_agents(self, agents: list[AbstractAgent], actors):
        for agent in agents:
            agent_pos = (self.factor * agent.pos[0], self.factor * agent.pos[1], 0)
            grid_len = self.factor * cfg.LG_LEN_IN_M
            local_grid_viz = vedo.Grid(
                pos=agent_pos, s=(grid_len, grid_len), lw=2, alpha=0.3
            )
            actors.append(local_grid_viz)

            agent_dir_vec = (np.cos(agent.heading), np.sin(agent.heading), 0)

            cone_r = self.factor * 1.35
            cone_height = self.factor * 3.1
            # FIXME: this is inconsistent

            if cfg.SCENARIO == Scenario.REAL:
                cone_r *= 0.4
                cone_height *= 0.4

            agent_actor = vedo.Cone(agent_pos, r=cone_r, height=cone_height, axis=agent_dir_vec, c="dodger_blue", alpha=0.7, res=4)  # type: ignore
            agent_label = f"Agent {agent.name}"
            agent_actor.caption(agent_label, size=(0.05, 0.025))

            if agent.name == 0:
                if agent.task:
                    task_print = (
                        str(agent.task.objective_enum)
                        .removeprefix("Objectives.")
                        .replace("_", " ")
                        .rjust(25)
                    )
                    agent_actor.legend(f"{task_print}")
                else:
                    # agent_actor.legend(f"No task selected".rjust(25))
                    agent_actor.legend(f"Finding Task".rjust(25))

                lbox = vedo.LegendBox([agent_actor], width=self.factor * 0.005)
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
            if cfg.SCENARIO == Scenario.REAL:
                REAL_OFFSET_FACTOR = 0.2  # need vignettes to be closer in real scenario
                REAL_S_FACTOR = 0.3  # need vignettes to be closer in real scenario
                wo_vig = wo_point.vignette(
                    # wo,
                    name_str,
                    offset=[0, 0, 5 * self.factor * REAL_OFFSET_FACTOR],
                    s=0.7 * self.factor * REAL_S_FACTOR,
                )
            actors.append(wo_vig)

        return actors

    def viz_start_point(self, pos: tuple[float, float]):
        point = vedo.Point(
            (pos[0] * self.factor, pos[1] * self.factor, 0), r=35, c="blue"
        )
        self.debug_actors.append(point)

        # FIXME: this is way to big in real scenario
        start_vig = point.vignette(
            "Start",
            offset=[0, 0, 5 * self.factor],
            s=self.factor,
        )
        if cfg.SCENARIO == Scenario.REAL:
            REAL_OFFSET_FACTOR = 0.2  # need vignettes to be closer in real scenario
            REAL_S_FACTOR = 0.3  # need vignettes to be closer in real scenario
            start_vig = point.vignette(
                "Start",
                offset=[0, 0, 5 * self.factor * REAL_OFFSET_FACTOR],
                s=self.factor * REAL_S_FACTOR,
            )
        self.debug_actors.append(start_vig)

    def get_scaled_pos_dict(self, tosg: SituationalGraph) -> dict:
        positions_of_all_nodes = nx.get_node_attributes(tosg.G, "pos")
        pos_dict = positions_of_all_nodes

        # scale the sizes to the scale of the simulated map image
        for pos in pos_dict:
            pos_dict[pos] = tuple([self.factor * x for x in pos_dict[pos]])

        return pos_dict

    def take_screenshot(self):
        scenario_name = cfg.SCREENSHOT_FOLDER_NAME
        new_folder_path = os.path.join("results", scenario_name)
        Path(new_folder_path).mkdir(parents=True, exist_ok=True)

        name = f"{scenario_name}-step{self.screenshot_step}"
        file_path = os.path.join(new_folder_path, name + ".png")

        io.screenshot(file_path)
        self.screenshot_step += 1
