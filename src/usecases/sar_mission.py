from typing import Union

from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.abstract_mission import AbstractMission
from src.usecases.actions.explore_frontier_action import ExploreFrontierAction
from src.usecases.actions.goto_action import GotoAction
from src.usecases.actions.world_object_action import WorldObjectAction
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, NodeType


class SARMission(AbstractMission):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

    def target_selection(self, agent: AbstractAgent, krm: KRM) -> Node:
        self._log.debug(f"{agent.name}: Selecting target frontier and finding path.")

        target_nodes = []
        frontier_idxs = krm.get_all_frontiers_idxs()
        target_nodes.extend(frontier_idxs)
        target_nodes.extend(krm.get_all_world_object_idxs())

        if len(frontier_idxs) < 1:
            self._log.warning(
                f"{agent.name}: Could not select a frontier, when I should've."
            )

        target_node = self.evaluate_potential_targets_based_on_path_cost(
            agent, target_nodes, krm
        )

        self._log.debug(f"{agent.name}: Target frontier selected: {target_node}.")

        return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: KRM, target_node: Union[str, int]
    ) -> Union[list[Node], None]:

        if not self.check_target_still_valid(krm, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return None

        possible_path = krm.shortest_path(agent.at_wp, target_node)

        if possible_path:
            return list(possible_path)
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return None

    def path_execution(
        self, agent: AbstractAgent, krm: KRM, action_path: list
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
                ExploreFrontierAction(self.cfg).run(agent, krm, action_path)
                action_path = []
                self.target_node = None
                self.action_path = None

            elif current_edge_type == EdgeType.WAYPOINT_EDGE:
                action_path = GotoAction(self.cfg).run(agent, krm, action_path)
                if len(action_path) < 2:
                    # HACK: this should not be set all the way down here.
                    self.target_node = None
                    action_path = []
                else:
                    return action_path

            elif current_edge_type == EdgeType.WORLD_OBJECT_EDGE:
                action_path, self.target_node = WorldObjectAction(self.cfg).run(
                    agent, krm, action_path
                )

        return action_path

    def check_completion(self, krm: KRM) -> bool:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        if num_of_frontiers < 1:
            return True
        else:
            return False

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################

    # TODO: this function needs to be optimized with a lookupt table
    def evaluate_potential_targets_based_on_path_cost(
        self, agent: AbstractAgent, target_idxs: list, krm: KRM
    ) -> Node:
        """
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics
        """
        shortest_path_len = float("inf")

        selected_target_idx: Union[int, None] = None

        for target_idx in target_idxs:
            candidate_path_len = float("inf")
            # HACK: have to do this becaue  sometimes the paths are not possible
            # perhaps add a connected check first...

            # TODO: make this the shortest path from single point to multiple endpoints.

            candidate_path_len = krm.shortest_path_len(agent.at_wp, target_idx)

            #  choose the first shortest path among equals
            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                # candidate_path_len = list(candidate_path_len)
                # selected_frontier_idx = candidate_path_len[-1]
                selected_target_idx = target_idx
        if not selected_target_idx:
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 1/2 No frontier can be selected from {len(target_idxs)} frontiers because no candidate path can be found."
            )
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 2/2 So either im at a node not connected to the krm or my target is not connected to the krm."
            )

        # assert selected_frontier_idx is not None

        return selected_target_idx
