import uuid
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.usecases.abstract_mission import AbstractMission
from src.usecases.archive.frontier_based_exploration_strategy import (
    FrontierBasedExplorationStrategy,
)
from src.utils.event import post_event
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, NodeType

from src.usecases.actions.goto import Goto
from src.usecases.actions.explore_frontier import ExploreFrontier
from src.usecases.actions.world_object_action import WorldObjectAction


class SARMission(AbstractMission):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        self._log.debug(
            f"{agent.name}: There are {num_of_frontiers} frontiers currently in KRM."
        )

        # TODO: this is actually initialisation logic. it should be moved elsewere.
        if num_of_frontiers < 1:
            self._log.debug(
                f"{agent.name}: No frontiers left to explore, sampling one."
            )

            lg = self.get_lg(agent)
            self.obtain_and_process_new_frontiers(agent, krm, lg)
            post_event("new lg", lg)

        self._log.debug(f"{agent.name}: Selecting target frontier and finding path.")
        target_node = self.select_optimal_target(agent, krm)
        self._log.debug(f"{agent.name}: Target frontier selected: {target_node}.")

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

    def path_execution(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path: list
    ) -> Union[list[Node], None]:
        if not self.check_target_still_valid(krm, self.target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return None

        print(f"{agent.name}: action_path: {action_path}")
        self.next_node = action_path[1]  # HACK: this is a hack, but it works for now
        # check edge type
        if len(action_path) >= 2:
            current_edge_type = krm.graph.edges[action_path[0], action_path[1]]["type"]
            print(f"{agent.name}: current_edge_type: {current_edge_type}")
            if current_edge_type == EdgeType.FRONTIER_EDGE:
                # self.frontier_action_edge(agent, krm, action_path)
                ExploreFrontier(self.cfg).run(agent, krm, action_path)
                action_path = []
                self.target_node = None
                self.action_path = None
            elif current_edge_type == EdgeType.WAYPOINT_EDGE:
                # action_path = self.waypoint_action_edge(agent, krm, action_path)
                action_path = Goto(self.cfg).run(agent, krm, action_path)
                if len(action_path) < 2:
                    self.target_node = (
                        None  # HACK: this should not be set all the way down here.
                    )
                    action_path = []
                else:
                    return action_path
            elif current_edge_type == EdgeType.WORLD_OBJECT_EDGE:
                # action_path, self.target_node = self.world_object_action_edge(agent, krm, action_path)
                action_path, self.target_node = WorldObjectAction(self.cfg).run(agent, krm, action_path)

        return action_path

    # TODO: this should be a variable strategy
    def select_optimal_target(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> Node:
        """ using the KRM, obtain the optimal frontier to visit next"""
        frontier_idxs = krm.get_all_frontiers_idxs()
        frontier_idxs.extend(krm.get_all_world_object_idxs())

        if len(frontier_idxs) < 1:
            self._log.warning(
                f"{agent.name}: Could not select a frontier, when I should've."
            )

        return self.evaluate_frontiers_based_on_cost_to_go(agent, frontier_idxs, krm)

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

    # TODO: move this to agent class
    def localize_agent_to_wp(self, agent: AbstractAgent, krm: KnowledgeRoadmap):
        agent.at_wp = krm.get_nodes_of_type_in_margin(
            agent.get_localization(), self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
        )[0]

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
    def evaluate_frontiers_based_on_cost_to_go(
        self, agent: AbstractAgent, frontier_idxs: list, krm: KnowledgeRoadmap
    ) -> Node:
        """
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics
        """
        shortest_path_len = float("inf")

        selected_frontier_idx: Union[int, None] = None

        for frontier_idx in frontier_idxs:
            candidate_path_len = float("inf")
            # HACK: have to do this becaue  sometimes the paths are not possible
            # perhaps add a connected check first...

            # TODO: make this the shortest path from single point to multiple endpoints.

            try:
                # candidate_path = krm.shortest_path_len(agent.at_wp, frontier_idx)
                candidate_path_len = krm.shortest_path_len(agent.at_wp, frontier_idx)

            except Exception:
                # no path can be found which is ok
                # for multi agent systems the graphs can be disconnected
                continue
            # choose the last shortest path among equals
            # if len(candidate_path) <= shortest_path_by_node_count:
            #  choose the first shortest path among equals
            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                # candidate_path_len = list(candidate_path_len)
                # selected_frontier_idx = candidate_path_len[-1]
                selected_frontier_idx = frontier_idx
        if not selected_frontier_idx:
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 1/2 No frontier can be selected from {len(frontier_idxs)} frontiers because no candidate path can be found."
            )
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 2/2 So either im at a node not connected to the krm or my target is not connected to the krm."
            )
            # HACK: low cohesion solution
            # self.target_node = None
            # self.localize_agent_to_wp(agent, krm)

        # assert selected_frontier_idx is not None

        return selected_frontier_idx

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
        path = krm.shortest_path(source=agent.at_wp, target=target_frontier,)
        if len(path) > 1:
            return path
        else:
            # raise ValueError("No path found")
            self._log.error(f"{agent.name}: No path found.")
