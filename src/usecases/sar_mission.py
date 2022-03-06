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

from src.usecases.actions.goto_action import GotoAction
from src.usecases.actions.explore_frontier_action import ExploreFrontierAction
from src.usecases.actions.world_object_action import WorldObjectAction


class SARMission(AbstractMission):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

    def target_selection(self, agent: AbstractAgent, krm: KnowledgeRoadmap) -> Node:
        self._log.debug(f"{agent.name}: Selecting target frontier and finding path.")
        target_node = self.select_optimal_target(agent, krm)
        self._log.debug(f"{agent.name}: Target frontier selected: {target_node}.")

        return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap, target_node: Union[str, int]
    ) -> Union[list[Node], None]:

        if not self.check_target_still_valid(krm, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return None

        # possible_path = self.find_path_to_selected_frontier(agent, target_node, krm)
        possible_path = krm.shortest_path(agent.at_wp, target_node)

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
            self.target_node = None
            self.action_path = None
            return None

        print(f"{agent.name}: action_path: {action_path}")
        self.next_node = action_path[1]  # HACK: this is a hack, but it works for now
        # check edge type
        if len(action_path) >= 2:
            current_edge_type = krm.graph.edges[action_path[0], action_path[1]]["type"]
            print(f"{agent.name}: current_edge_type: {current_edge_type}")
            if current_edge_type == EdgeType.FRONTIER_EDGE:
                # self.frontier_action_edge(agent, krm, action_path)
                ExploreFrontierAction(self.cfg).run(agent, krm, action_path)
                action_path = []
                self.target_node = None
                self.action_path = None
            elif current_edge_type == EdgeType.WAYPOINT_EDGE:
                # action_path = self.waypoint_action_edge(agent, krm, action_path)
                action_path = GotoAction(self.cfg).run(agent, krm, action_path)
                if len(action_path) < 2:
                    self.target_node = (
                        None  # HACK: this should not be set all the way down here.
                    )
                    action_path = []
                else:
                    return action_path
            elif current_edge_type == EdgeType.WORLD_OBJECT_EDGE:
                # action_path, self.target_node = self.world_object_action_edge(agent, krm, action_path)
                action_path, self.target_node = WorldObjectAction(self.cfg).run(
                    agent, krm, action_path
                )

        return action_path

    def select_optimal_target(
        self, agent: AbstractAgent, krm: KnowledgeRoadmap
    ) -> Node:
        """ using the KRM, obtain the optimal target node to visit next"""
        target_nodes = []
        frontier_idxs = krm.get_all_frontiers_idxs()
        target_nodes.extend(frontier_idxs)
        target_nodes.extend(krm.get_all_world_object_idxs())

        if len(frontier_idxs) < 1:
            self._log.warning(
                f"{agent.name}: Could not select a frontier, when I should've."
            )

        return self.evaluate_potential_targets_based_on_cost_to_go(
            agent, target_nodes, krm
        )

    def check_target_available(self, krm: KnowledgeRoadmap) -> bool:
        num_targets = 0
        num_frontiers = len(krm.get_all_frontiers_idxs())
        num_targets += num_frontiers

        # TODO: this is actually initialisation logic. it should be moved elsewere.
        if num_targets < 1:
            return False
        else:
            return True

    def fix_target_initialisation(self, krm: KnowledgeRoadmap) -> tuple:
        krm.graph.add_edge(0, 0, type=EdgeType.FRONTIER_EDGE)

        action_path = [0, 0]
        return action_path, 0

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

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################

    # TODO: this function needs to be optimized with a lookupt table
    def evaluate_potential_targets_based_on_cost_to_go(
        self, agent: AbstractAgent, target_idxs: list, krm: KnowledgeRoadmap
    ) -> Node:
        """
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics
        """
        shortest_path_len = float("inf")

        selected_frontier_idx: Union[int, None] = None

        for frontier_idx in target_idxs:
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
                f"{agent.name} at {agent.at_wp}: 1/2 No frontier can be selected from {len(target_idxs)} frontiers because no candidate path can be found."
            )
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 2/2 So either im at a node not connected to the krm or my target is not connected to the krm."
            )
            # HACK: low cohesion solution
            # self.target_node = None
            # self.localize_agent_to_wp(agent, krm)

        # assert selected_frontier_idx is not None

        return selected_frontier_idx
