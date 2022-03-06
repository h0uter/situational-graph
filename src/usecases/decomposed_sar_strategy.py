import uuid
from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.usecases.exploration_strategy import ExplorationStrategy
from src.usecases.frontier_based_exploration_strategy import (
    FrontierBasedExplorationStrategy,
)
from src.utils.event import post_event
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, NodeType

from src.usecases.actions.goto import Goto
from src.usecases.actions.explore_frontier import ExploreFrontier


# class DecomposedSARStrategy(FrontierBasedExplorationStrategy):
class DecomposedSARStrategy(FrontierBasedExplorationStrategy):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

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
                    self.target_node = None  # HACK: this should not be set all the way down here.
                    action_path = []
                else:
                    return action_path
            elif current_edge_type == EdgeType.WORLD_OBJECT_EDGE:
                action_path = self.world_object_action_edge(agent, krm, action_path)

        return action_path

    def world_object_action_edge(self, agent, krm, action_path):
        # is it allowed to make an action set a different action path?
        start_node = 0
        self._log.debug(
            f"{agent.name}: world_object_action_edge():: removing world object {action_path[-1]} from graph."
        )
        krm.remove_world_object(action_path[-1])
        # action_path = krm.shortest_path(agent.at_wp, start_node)
        # self._log.debug(
        #     f"{agent.name}: world_object_action_edge():: action_path: {action_path}"
        # )
        # return action_path
        self.target_node = start_node
        return []

    # TODO: this should be a variable strategy
    def select_target_frontier(
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
