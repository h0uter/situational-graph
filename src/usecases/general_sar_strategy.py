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


class GeneralSARStrategy(FrontierBasedExplorationStrategy):
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
                self.frontier_action_edge(agent, krm, action_path)
                action_path = []
            elif current_edge_type == EdgeType.WAYPOINT_EDGE:
                action_path = self.waypoint_action_edge(agent, krm, action_path)

            elif current_edge_type == EdgeType.WORLD_OBJECT_EDGE:
                action_path = self.world_object_action_edge(agent, krm, action_path)

        return action_path

    def frontier_action_edge(self, agent: AbstractAgent, krm: KnowledgeRoadmap, action_path):

        node_data = krm.get_node_data_by_idx(action_path[1])
        agent.move_to_pos(node_data["pos"])

        at_destination = (
            len(
                krm.get_nodes_of_type_in_margin(
                    agent.get_localization(), self.cfg.ARRIVAL_MARGIN, NodeType.FRONTIER
                )
            )
            >= 1
        )
        self._log.debug(f"{agent.name}: at_destination: {at_destination}")

        if at_destination:
            self._log.debug(
                f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
            )
            krm.remove_frontier(self.next_node)
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
            self.target_node = None
            self.action_path = None

    def waypoint_action_edge(self, agent, krm, action_path):
        # Execute a single action edge of the action path.

        if len(action_path) >= 2:
            # node_data = krm.get_node_data_by_idx(action_path[0])
            node_data = krm.get_node_data_by_idx(action_path[1])
            agent.move_to_pos(node_data["pos"])
            # FIXME: this can return none if world object nodes are included in the graph.
            # can just give them infinite weight... should solve it by performing shortest action_path over a subgraph.
            # BUG: can still randomly think the agent is at a world object if it is very close to the frontier.
            agent.at_wp = krm.get_nodes_of_type_in_margin(
                agent.pos, self.cfg.AT_WP_MARGIN, NodeType.WAYPOINT
            )[0]
            action_path.pop(0)
            if len(action_path) < 2:
                self.target_node = None  # HACK: this should not be set all the way down here.
                # Need a  
                return []
            else:
                return action_path

        else:
            # self._logger.warning(
            #     f"trying to perform action_path step with empty action_path {action_path}"
            # )
            raise Exception(
                f"{agent.name}: Trying to perform action_path step with empty action_path {action_path}."
            )

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
