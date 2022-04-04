from typing import Optional, Sequence

from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.abstract_mission import AbstractMission
from src.usecases.actions.explore_action import ExploreAction
from src.usecases.actions.goto_action import GotoAction
from src.usecases.actions.guide_action import GuideAction
from src.usecases.actions.extraction_action import ExtractionAction
from src.utils.config import Config
from src.utils.my_types import EdgeType, Node, Edge


class SARMission(AbstractMission):
    def __init__(self, cfg: Config) -> None:
        super().__init__(cfg)

    def target_selection(self, agent: AbstractAgent, krm: KRM) -> Optional[Node]:
        self._log.debug(f"{agent.name}: Selecting target frontier and finding path.")

        target_nodes = []
        frontier_idxs = krm.get_all_frontiers_idxs()
        target_nodes.extend(frontier_idxs)
        target_nodes.extend(krm.get_all_world_object_idxs())

        if len(frontier_idxs) < 1:
            self._log.warning(
                f"{agent.name}: Could not select a frontier, when I should've."
            )

        self._log.debug(f"{agent.name}: the agent is at {agent.at_wp}.")
        target_node = self.evaluate_potential_targets_based_on_path_cost(
            agent, target_nodes, krm
        )

        return target_node

    def path_generation(
        self, agent: AbstractAgent, krm: KRM, target_node: Node
    ) -> Sequence[Optional[Edge]]:

        if not self.check_target_still_valid(krm, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return []
        
        self._log.debug(f"{agent.name}: target_node: {target_node}")
        action_path = list(krm.shortest_path(agent.at_wp, target_node))  # type: ignore

        if action_path:
            action_path = krm.node_list_to_edge_list(action_path)
            return action_path
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return []

    def path_execution(
        self, agent: AbstractAgent, krm: KRM, action_path: Sequence[Edge]
    ) -> Sequence[Optional[Edge]]:
        if not self.check_target_still_valid(krm, self.target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            self.clear_target()
            return []

        self._log.debug(f"{agent.name}: action_path: {action_path}")
        # print(f"action_path: {action_path}")
        # current_edge_type = krm.graph.edges[action_path[0], action_path[1]]["type"]
        # current_edge_type = krm.graph.edges[action_path[0]]["type"]
        current_edge_type = krm.get_type_of_edge_triplet(action_path[0])
        self._log.debug(f"{agent.name}: current_edge_type: {current_edge_type}")

        if current_edge_type == EdgeType.EXPLORE_FT_EDGE:
            action_path = ExploreAction(self.cfg).run(agent, krm, action_path)
            self.clear_target()

            # either a reset function
            # or pass and return the action path continuously

        elif current_edge_type == EdgeType.GOTO_WP_EDGE:
            action_path = GotoAction(self.cfg).run(agent, krm, action_path)
            # if len(action_path) < 2:
            if len(action_path) < 1:
                self.clear_target()
                return []
            else:
                return action_path

        elif current_edge_type == EdgeType.EXTRACTION_WO_EDGE:
            action_path = ExtractionAction(self.cfg).run(
                agent, krm, action_path
            )
            # Lets check if this is not neccesary, it is necce
            self.target_node = action_path[-1][1]

        elif current_edge_type is EdgeType.GUIDE_WP_EDGE:
            action_path = GuideAction(self.cfg).run(agent, krm, action_path)
            if len(action_path) < 1:
                self.clear_target()

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
    ) -> Optional[Node]:
        """
        Evaluate the frontiers and return the best one.
        this is the entrypoint for exploiting semantics
        """
        # self._log.debug(f"{agent.name}: evaluating {target_idxs} based on path cost.")

        shortest_path_len = float("inf")
        selected_target_idx: Optional[Node] = None

        for target_idx in target_idxs:
            candidate_path_len: float = krm.shortest_path_len(agent.at_wp, target_idx)  # type: ignore

            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                selected_target_idx = target_idx

        self._log.debug(
            f"{agent.name}: Shortest path found is: {candidate_path_len} for {selected_target_idx}."
        )
        if not selected_target_idx:
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 1/2 No frontier can be selected from {len(target_idxs)} frontiers (0 candidate paths)."
            )
            self._log.error(
                f"{agent.name} at {agent.at_wp}: 2/2 So either im at a node not connected to the krm or my target is not connected to the krm."
            )
            return

        assert selected_target_idx is not None

        return selected_target_idx
