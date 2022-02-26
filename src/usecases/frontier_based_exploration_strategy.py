import logging
import uuid
from typing import Union

import networkx as nx
from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.usecases.exploration_strategy import ExplorationStrategy
from src.utils.event import post_event
from src.utils.config import Config

from src.utils.my_types import Node


class FrontierBasedExplorationStrategy(ExplorationStrategy):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

        self.no_frontiers_remaining = False

    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        self._logger.debug(
            f"{agent.name}: {num_of_frontiers} frontiers currently in krm"
        )
        if num_of_frontiers < 1:
            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(agent, krm, lg)
            post_event("new lg", lg)

        self._logger.debug(f"{agent.name}: selecting target frontier and finding path")
        target_node = self.select_target_frontier(agent, krm)
        self._logger.debug(f"{agent.name}: target frontier selected: {target_node}")

        return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, target_node: Union[str, int]
    ) -> Union[list[Node], None]:
        possible_path = self.find_path_to_selected_frontier(agent, target_node, krm)
        if possible_path:
            return list(possible_path)
        else:
            self._logger.warning(f"{agent.name}: path_generation(): no path found")
            return None

    def path_execution(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path: list[Node]
    ) -> Union[list[Node], None]:
        next_node = action_path[0]
        action_path = self.perform_path_step(agent, action_path, krm)

        at_destination = (
            len(
                krm.get_nodes_of_type_in_margin(
                    agent.get_localization(), self.cfg.ARRIVAL_MARGIN, "frontier"
                )
            )
            >= 1
        )

        if not action_path and at_destination:
            """now we have visited the frontier we can remove it from the KRM and sample a waypoint in its place"""
            self._logger.debug(f"{agent.name}: frontier processing")
            krm.remove_frontier(next_node)
            # self.selected_frontier_idx = None

            self.sample_waypoint_from_pose(agent, krm)
            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(agent, krm, lg)
            self.prune_frontiers(krm)
            self.find_shortcuts_between_wps(lg, krm, agent)
            w_os = agent.look_for_world_objects_in_perception_scene()
            for w_o in w_os:
                krm.add_world_object(w_o.pos, w_o.name)
            post_event("new lg", lg)

        return action_path

    def check_completion(self, krm: KnowledgeRoadmap) -> bool:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        if num_of_frontiers < 1:
            return True
        else:
            return False

    # utitlies
    ############################################################################################

    def get_lg(self, agent: AbstractAgent) -> LocalGrid:
        lg_img = agent.get_local_grid_img()

        return LocalGrid(
            world_pos=agent.get_localization(), img_data=lg_img, cfg=self.cfg,
        )

    def obtain_and_process_new_frontiers(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, lg: LocalGrid,
    ) -> None:
        frontiers_cells = lg.sample_frontiers_on_cellmap(
            radius=self.cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS,
            num_frontiers_to_sample=self.cfg.N_SAMPLES,
        )
        self._logger.debug(f"{agent.name}: found {frontiers_cells} new frontiers")
        for frontier_cell in frontiers_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################
    def evaluate_frontiers(
        self, agent: AbstractAgent, frontier_idxs: list, krm: KnowledgeRoadmap
    ):
        """
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics
        """
        shortest_path_by_node_count = float("inf")
        selected_frontier_idx: Union[int, None] = None

        for frontier_idx in frontier_idxs:
            candidate_path = []
            # HACK: have to do this becaue  sometimes the paths are not possible
            # perhaps add a connected check first...
            try:
                candidate_path = nx.shortest_path(
                    krm.graph,
                    source=agent.at_wp,
                    target=frontier_idx,
                    weight="cost",
                    method=self.cfg.PATH_FINDING_METHOD,
                )
                # candidate_path = nx.shortest_path(
                #     krm.graph, source=agent.at_wp, target=frontier_idx
                # )
            except Exception:
                # no path can be found which is ok
                # for multi agent systems the graphs can be disconnected
                continue
            # choose the last shortest path among equals
            # if len(candidate_path) <= shortest_path_by_node_count:
            #  choose the first shortest path among equals
            if (
                len(candidate_path) < shortest_path_by_node_count
                and len(candidate_path) > 0
            ):
                shortest_path_by_node_count = len(candidate_path)
                candidate_path = list(candidate_path)
                selected_frontier_idx = candidate_path[-1]
        if selected_frontier_idx:
            return selected_frontier_idx
        else:
            self._logger.error(
                f"{agent.name} at {agent.at_wp}: No frontier can be selected from {len(frontier_idxs)} frontiers"
            )
            return None

    # TODO: this should be a variable strategy
    def select_target_frontier(self, agent: AbstractAgent, krm: KnowledgeRoadmap):
        """ using the KRM, obtain the optimal frontier to visit next"""
        frontier_idxs = krm.get_all_frontiers_idxs()
        if len(frontier_idxs) > 0:
            return self.evaluate_frontiers(agent, frontier_idxs, krm)

        else:
            self._logger.debug(f"{agent.name}: No frontiers left to explore")
            self.no_frontiers_remaining = True
            return None

    """Path/Plan generation"""
    #############################################################################################
    def find_path_to_selected_frontier(
        self, agent: AbstractAgent, target_frontier, krm: KnowledgeRoadmap
    ):
        """
        Find the shortest path from the current waypoint to the target frontier.

        :param target_frontier: the frontier that we want to reach
        :return: The path to the selected frontier.
        """
        path = nx.shortest_path(
            krm.graph,
            source=agent.at_wp,
            target=target_frontier,
            weight="cost",
            method=self.cfg.PATH_FINDING_METHOD,
        )
        if len(path) > 1:
            return path
        else:
            # raise ValueError("No path found")
            self._logger.error(f"{agent.name}: No path found")

    def perform_path_step(
        self, agent: AbstractAgent, path: list, krm: KnowledgeRoadmap
    ) -> list:
        """
        Execute a single step of the path.
        """
        if len(path) > 1:
            node_data = krm.get_node_data_by_idx(path[0])
            agent.move_to_pos(node_data["pos"])
            # FIXME: this can return none if world object nodes are included in the graph.
            # can just give them infinite weight... should solve it by performing shortest path over a subgraph.
            # BUG: can still randomly think the agent is at a world object if it is very close to the frontier.
            agent.at_wp = krm.get_nodes_of_type_in_margin(
                agent.pos, self.cfg.AT_WP_MARGIN, "waypoint"
            )[0]
            path.pop(0)
            return path

        elif len(path) == 1:
            selected_frontier_data = krm.get_node_data_by_idx(path[0])
            agent.move_to_pos(selected_frontier_data["pos"])
            self._logger.debug(
                f"{agent.name}: the selected frontier pos is {selected_frontier_data['pos']}"
            )
            return []

        else:
            # self._logger.warning(
            #     f"trying to perform path step with empty path {path}"
            # )
            raise Exception(
                f"{agent.name}: trying to perform path step with empty path {path}"
            )

    """Path Execution"""
    #############################################################################################
    def sample_waypoint_from_pose(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> None:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        """
        # HACK: just taking the first one from the list is not neccessarily the closest
        wp_at_previous_pos = krm.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, "waypoint"
        )[0]
        krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)
        agent.at_wp = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.AT_WP_MARGIN, "waypoint"
        )[0]

    def prune_frontiers(self, krm: KnowledgeRoadmap) -> None:
        """obtain all the frontier nodes in krm in a certain radius around the current position"""

        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)["pos"]
            # close_frontiers = self.get_nodes_of_type_in_radius(
            close_frontiers = krm.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, "frontier"
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    def find_shortcuts_between_wps(
        self, lg: LocalGrid, krm: KnowledgeRoadmap, agent: AbstractAgent
    ):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.LG_LENGTH_IN_M / 2, "waypoint"
        )
        points = []
        for node in close_nodes:
            if node != agent.at_wp:
                points.append(krm.get_node_data_by_idx(node)["pos"])

        if points:
            for point in points:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)
                is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if is_collision_free:
                    from_wp = agent.at_wp
                    to_wp = krm.get_node_by_pos(point)
                    krm.graph.add_edge(
                        from_wp, to_wp, type="waypoint_edge", id=uuid.uuid4()
                    )
