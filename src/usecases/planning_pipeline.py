import logging
from abc import ABC, abstractmethod
from typing import Literal, Optional, Sequence, Tuple

from src.entities.abstract_agent import AbstractAgent
from src.entities.tosg import TOSG
from src.entities.plan import Plan
from src.utils.config import Config
from src.entities.dynamic_data.task import Task
from src.utils.my_types import Edge, EdgeType, Node
from src.usecases.behaviors.goto_behavior import GotoBehavior
from src.usecases.behaviors.explore_behavior import ExploreBehavior


def select_optimal_task(
    agent: AbstractAgent, tosgraph: TOSG, tasks: Sequence[Task]
) -> Optional[Task]:
    # this should be a method of the agent
    pass


def find_plan(agent: AbstractAgent, tosgraph: TOSG, task: Task) -> Plan:
    """Find a plan for the agent."""
    pass


def execute_edge(
    agent: AbstractAgent, tosgraph: TOSG, plan: Plan, tasks: Sequence[Task]
) -> Tuple[Plan, Sequence[Task]]:
    """Execute the plan."""
    pass


class PlanningPipeline:
    def __init__(self, cfg: Config, tosg: TOSG) -> None:
        self.cfg = cfg
        self.completed = False
        self.plan: Plan = Plan()
        self.target_node: Optional[Node] = None
        self._log = logging.getLogger(__name__)

        self.initialize(tosg)

    # HACK: initialization should add this edge to the tasks,
    # FIXME: this is the start, here I will add the tasks and see them work instantly
    def initialize(self, tosg: TOSG):
        # Add a frontier edge self loop on the start node to ensure a exploration sampling action
        edge_id = tosg.graph.add_edge(0, 0, type=EdgeType.EXPLORE_FT_EDGE)
        # tosg.tasks.append(Task(edge_id))
        
        self.plan.edge_sequence = [(0, 0, edge_id)]
        self.target_node = 0

    # CONTEXT
    def main_loop(self, agent: AbstractAgent, krm: TOSG) -> bool:
        something_was_done = False

        if self.target_node is None:
            self._log.debug(f"{agent.name}: No target node set. Setting one.")
            self.target_node = self.target_selection(agent, krm)
            something_was_done = True

        if not self.plan.valid:
            self._log.debug(
                f"{agent.name}: No action path set. Finding one to {self.target_node}."
            )
            edge_sequence = self.path_generation(agent, krm, self.target_node)
            self.plan.edge_sequence = edge_sequence

            something_was_done = True

        if len(self.plan) >= 1:
            self._log.debug(f"{agent.name}: Action path set. Executing one.")
            mutated_plan = self.plan_execution(agent, krm, self.plan.edge_sequence)
            self.plan.edge_sequence = mutated_plan

            if not self.plan.valid:
                self._log.debug(f"{agent.name}: plan execution finished.")
            something_was_done = True

        # only ever have to check completion here
        if self.check_completion(krm):
            self._log.debug(f"{agent.name}: Exploration completed.")
            self.completed = True

        if not something_was_done:
            logging.warning("No exploration step taken")

        return self.completed

    def check_target_available(self, krm: TOSG) -> bool:
        num_targets = 0
        num_frontiers = len(krm.get_all_frontiers_idxs())
        num_targets += num_frontiers
        num_targets += len(krm.get_all_world_object_idxs())

        if num_targets < 1:
            return False
        else:
            return True

    def clear_target(self) -> None:
        self.target_node = None

    def check_target_still_valid(self, krm: TOSG, target_node: Optional[Node]) -> bool:
        if target_node is None:
            return False
        return krm.check_node_exists(target_node)

    def target_selection(self, agent: AbstractAgent, krm: TOSG) -> Optional[Node]:
        self._log.debug(f"{agent.name}: Selecting target frontier and finding path.")

        # here I scramble it but this should really be the tasks
        # really this is all the edges which have been instantiated with an affordance.
        # FIXME: make a list of all potential targets, this should be done with tasks
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
        self, agent: AbstractAgent, krm: TOSG, target_node: Node
    ) -> Sequence[Optional[Edge]]:

        # FIXME: lets make the plan check its own validity
        if not self.check_target_still_valid(krm, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return []

        self._log.debug(f"{agent.name}: target_node: {target_node}")
        node_path = krm.shortest_path(agent.at_wp, target_node)  # type: ignore

        if node_path:
            node_path = list(node_path)
            edge_path = krm.node_list_to_edge_list(node_path)
            return edge_path
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return []

    # this is the plan executor, maybe make it its own class.
    def plan_execution(
        self, agent: AbstractAgent, krm: TOSG, edge_path: Sequence[Edge]
    ) -> Sequence[Optional[Edge]]:
        if not self.check_target_still_valid(krm, self.target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            self.clear_target()
            return []

        self._log.debug(f"{agent.name}: action_path: {edge_path}")
        # print(f"action_path: {action_path}")
        # current_edge_type = krm.graph.edges[action_path[0], action_path[1]]["type"]
        # current_edge_type = krm.graph.edges[action_path[0]]["type"]
        current_edge_type = krm.get_type_of_edge_triplet(edge_path[0])
        self._log.debug(f"{agent.name}: current_edge_type: {current_edge_type}")

        if current_edge_type == EdgeType.EXPLORE_FT_EDGE:
            # action_path = ExploreBehavior(self.cfg).run(agent, krm, action_path)
            edge_path = ExploreBehavior(self.cfg).execute_pipeline(
                agent, krm, edge_path
            )
            self.clear_target()

            # either a reset function
            # or pass and return the action path continuously

        elif current_edge_type == EdgeType.GOTO_WP_EDGE:
            # action_path = GotoBehavior(self.cfg).run(agent, krm, action_path)
            edge_path = GotoBehavior(self.cfg).execute_pipeline(agent, krm, edge_path)
            # if len(action_path) < 2:
            if len(edge_path) < 1:
                self.clear_target()
                return []
            else:
                return edge_path

        # elif current_edge_type == EdgeType.PLAN_EXTRACTION_WO_EDGE:
        #     action_path = PlanExtractionBehavior(self.cfg).run_implementation(
        #         agent, krm, action_path
        #     )
        #     # Lets check if this is not neccesary, it is necce
        #     self.target_node = action_path[-1][1]

        # elif current_edge_type is EdgeType.GUIDE_WP_EDGE:
        #     action_path = GuideBehavior(self.cfg).run_implementation(
        #         agent, krm, action_path
        #     )
        #     if len(action_path) < 1:
        #         self.clear_target()

        return edge_path

    def check_completion(self, krm: TOSG) -> bool:
        num_of_frontiers = len(krm.get_all_frontiers_idxs())
        if num_of_frontiers < 1:
            return True
        else:
            return False

    """Target Selection"""
    ############################################################################################
    # ENTRYPOINT FOR GUIDING EXPLORATION WITH SEMANTICS ########################################
    ############################################################################################

    # FIXME: task selector, needs to use list of tasks
    def evaluate_potential_targets_based_on_path_cost(
        self, agent: AbstractAgent, target_idxs: list, krm: TOSG
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
