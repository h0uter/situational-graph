import uuid
from typing import Union

import networkx as nx
from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.usecases.exploration_strategy import ExplorationStrategy
from src.utils.event import post_event
from src.utils.config import Config

from src.utils.my_types import Node, NodeType


class FrontierBasedExplorationStrategy(ExplorationStrategy):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

        self.no_frontiers_remaining = False

        # TODO: according to arjan the parameters for a certain strategy should be defined here.

    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        self._log.debug(f"{agent.name}: {num_of_frontiers} frontiers currently in krm")
        if num_of_frontiers < 1:
            self._log.debug(f"{agent.name}: no frontiers left to explore, sampling one")

            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(agent, krm, lg)
            post_event("new lg", lg)

        self._log.debug(f"{agent.name}: selecting target frontier and finding path")
        target_node = self.select_target_frontier(agent, krm)
        self._log.debug(f"{agent.name}: target frontier selected: {target_node}")

        return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, target_node: Union[str, int]
    ) -> Union[list[Node], None]:
        possible_path = self.find_path_to_selected_frontier(agent, target_node, krm)
        if possible_path:
            return list(possible_path)
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return None

    # XXX: this is my most expensive function, so I should try to optimize it
    def path_execution(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path: list[Node]
    ) -> Union[list[Node], None]:
        # next_node = action_path[0]
        if not self.check_target_still_valid(krm, self.target_node):
            self._log.warning(f"{agent.name}: target frontier is no longer valid")
            return None
        next_node = action_path[1]
        self._log.debug(
            f"{agent.name}: the action path before execution is {action_path}"
        )
        action_path = self.perform_path_step(agent, action_path, krm)
        self._log.debug(
            f"{agent.name}: the action path after execution is {action_path}"
        )

        at_destination = (
            len(
                krm.get_nodes_of_type_in_margin(
                    agent.get_localization(), self.cfg.ARRIVAL_MARGIN, NodeType.FRONTIER
                )
            )
            >= 1
        )
        self._log.debug(f"{agent.name}: at_destination: {at_destination}")

        if not action_path and at_destination:
            self._log.debug(f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place")
            krm.remove_frontier(next_node)
            # self.selected_frontier_idx = None

            self.sample_waypoint_from_pose(agent, krm)
            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(
                agent, krm, lg
            )  # XXX: this is my most expensive function, so I should try to optimize it
            self.prune_frontiers(
                krm
            )  # XXX: this is my 2nd expensive function, so I should try to optimize it
            self.find_shortcuts_between_wps(lg, krm, agent)
            w_os = agent.look_for_world_objects_in_perception_scene()
            if w_os:
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

    def check_target_still_valid(
        self, krm: KnowledgeRoadmap, target_node: Node
    ) -> bool:
        return krm.check_node_exists(target_node)

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
        # self._log.debug(f"{agent.name}: found {frontiers_cells} new frontiers")
        for frontier_cell in frontiers_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################
    def evaluate_frontiers(
        self, agent: AbstractAgent, frontier_idxs: list, krm: KnowledgeRoadmap
    ) -> Node:
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
        if not selected_frontier_idx:
            self._log.error(
                f"{agent.name} at {agent.at_wp}: No frontier can be selected from {len(frontier_idxs)} frontiers because no candidate path can be found."
            )
            self._log.error(
                f"{agent.name} at {agent.at_wp}: so either im at a node not connected to the krm or my target is not connected to the krm."
            )
            # HACK: low cohesion solution
            # self.target_node = None
            # self.localize_agent_to_wp(agent, krm)

        # assert selected_frontier_idx is not None

        return selected_frontier_idx

    # TODO: this should be a variable strategy
    def select_target_frontier(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> Node:
        """ using the KRM, obtain the optimal frontier to visit next"""
        frontier_idxs = krm.get_all_frontiers_idxs()

        if len(frontier_idxs) < 1:
            self._log.warning(
                f"{agent.name}: could not select a frontier, when I should've."
            )

        return self.evaluate_frontiers(agent, frontier_idxs, krm)

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
            self._log.error(f"{agent.name}: No path found")

    def perform_path_step(
        self, agent: AbstractAgent, path: list, krm: KnowledgeRoadmap
    ) -> list:
        """
        Execute a single step of the path.
        """
        if len(path) > 2:
            # node_data = krm.get_node_data_by_idx(path[0])
            node_data = krm.get_node_data_by_idx(path[1])
            agent.move_to_pos(node_data["pos"])
            # FIXME: this can return none if world object nodes are included in the graph.
            # can just give them infinite weight... should solve it by performing shortest path over a subgraph.
            # BUG: can still randomly think the agent is at a world object if it is very close to the frontier.
            agent.at_wp = krm.get_nodes_of_type_in_margin(
                agent.pos, self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
            )[0]
            path.pop(0)
            return path

        # if len(path) == 2:
        #     # node_data = krm.get_node_data_by_idx(path[0])
        #     node_data = krm.get_node_data_by_idx(path[1])
        #     agent.move_to_pos(node_data["pos"])
        #     # FIXME: this can return none if world object nodes are included in the graph.
        #     # can just give them infinite weight... should solve it by performing shortest path over a subgraph.
        #     # BUG: can still randomly think the agent is at a world object if it is very close to the frontier.
        #     agent.at_wp = krm.get_nodes_of_type_in_margin(
        #         agent.pos, self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        #     )[0]
        #     path.pop(0)
        #     return path

        # elif len(path) == 1:
        elif len(path) == 2:
            # selected_frontier_data = krm.get_node_data_by_idx(path[0])
            selected_frontier_data = krm.get_node_data_by_idx(path[1])
            agent.move_to_pos(selected_frontier_data["pos"])
            self._log.debug(
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
        # BUG:  this can make the agent teleport to a random frontier in the vicinty.
        # better would be to explicitly check if we reached the frontier we intended to reach.
        # and if we didnt to attempt to walk to it again. To attempt to actually expand the krm
        # with the intended frontier and not a random one
        # HACK: just taking the first one from the list is not neccessarily the closest
        # BUG: list index out of range range
        wp_at_previous_pos = krm.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, NodeType.WAYPOINT
        )[0]
        krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)
        agent.at_wp = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )[0]

    # TODO: move this to agent class
    def localize_agent_to_wp(self, agent: AbstractAgent, krm: KnowledgeRoadmap):
        agent.at_wp = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )[0]

    def prune_frontiers(self, krm: KnowledgeRoadmap) -> None:
        """obtain all the frontier nodes in krm in a certain radius around the current position"""

        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)["pos"]
            # close_frontiers = self.get_nodes_of_type_in_radius(
            close_frontiers = krm.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, NodeType.FRONTIER
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    def find_shortcuts_between_wps(
        self, lg: LocalGrid, krm: KnowledgeRoadmap, agent: AbstractAgent
    ):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.WP_SHORTCUT_MARGIN, NodeType.WAYPOINT
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
