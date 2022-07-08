import logging
from typing import Optional, Sequence, Tuple

from src.entities.abstract_agent import AbstractAgent
from src.entities.dynamic_data.task import Task
from src.entities.plan import Plan
from src.entities.static_data.objective import Objective
from src.entities.tosg import TOSG
from src.usecases.behaviors.explore_behavior import ExploreBehavior
from src.usecases.behaviors.goto_behavior import GotoBehavior
from src.utils.config import Config
from src.utils.my_types import Behavior, Edge, Node


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


class Planner:
    def __init__(self, cfg: Config, tosg: TOSG, agent) -> None:
        self.cfg = cfg
        self.completed = False
        self.plan: Plan = Plan()
        self._log = logging.getLogger(__name__)

        self.initialize(tosg, agent)

    @property
    def target_node(self) -> Optional[Node]:
        if len(self.plan) >= 1:
            return self.plan[-1][1]
        else:
            self.plan.invalidate
            return None

    def initialize(self, tosg: TOSG, agent):
        # Add an explore self edge on the start node to ensure a exploration sampling action
        edge_uuid = tosg.add_my_edge(0, 0, Behavior.EXPLORE_FT_EDGE)
        tosg.tasks.append(Task(edge_uuid, Objective.EXPLORE))

        # spoof the task selection, just select the first one.
        agent.task = tosg.tasks[0]

        # obtain the plan which corresponds to this edge.
        init_explore_edge = tosg.get_edge_by_UUID(agent.task.edge_uuid)

        self.plan.edge_sequence = [init_explore_edge]
        self._log.debug(f"target node: {self.target_node}")

    # CONTEXT
    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        """ select a task"""
        if self.target_node is None:
            agent.task = self.task_selection(agent, tosg)

        """ generate a plan"""
        if not self.plan.valid:
            target_node = agent.task.get_target_node(tosg)
            edge_sequence = self.find_plan_for_task(agent, tosg, target_node)
            self.plan.edge_sequence = edge_sequence

        """ execute the plan"""
        if len(self.plan) >= 1:
            mutated_plan = self.plan_execution(agent, tosg, self.plan.edge_sequence)
            self.plan.edge_sequence = mutated_plan

            if len(mutated_plan) == 0:
                self.destroy_task(agent, tosg)

        """check completion of mission"""
        if self.check_completion(tosg):
            self.completed = True

        return self.completed

    def destroy_task(self, agent: AbstractAgent, tosg: TOSG):
        self._log.debug(f"{agent.name}:  has a task  {agent.task}")

        if agent.task:
            if agent.task in tosg.tasks:
                tosg.tasks.remove(agent.task)
        self._log.debug(f"{agent.name}: destroying task  {agent.task}")

        agent.clear_task()

    def check_target_still_valid(self, tosg: TOSG, target_node: Optional[Node]) -> bool:
        if target_node is None:
            return False
        return tosg.check_node_exists(target_node)

    def task_selection(self, agent: AbstractAgent, tosg: TOSG) -> Optional[Task]:
        highest_utility = 0
        optimal_task = None

        for task in tosg.tasks:
            task_target_node = task.get_target_node(tosg)

            # HACK: sometimes we get a task that does not exist anymore.
            if not task_target_node:
                continue

            path_cost = tosg.shortest_path_len(agent.at_wp, task_target_node)

            def calc_utility(reward: float, path_cost: float) -> float:
                if path_cost == 0:
                    return float("inf")
                else:
                    return reward / path_cost

            utility = calc_utility(task.reward, path_cost)

            if utility > highest_utility:
                highest_utility = utility
                optimal_task = task

        return optimal_task

    def find_plan_for_task(
        self, agent: AbstractAgent, tosg: TOSG, target_node: Node
    ) -> Sequence[Optional[Edge]]:

        # FIXME: lets make the plan check its own validity
        # fixme this should return a plan
        if not self.check_target_still_valid(tosg, target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            return []

        self._log.debug(f"{agent.name}: target_node: {target_node}")
        node_path = tosg.shortest_path(agent.at_wp, target_node)  # type: ignore

        if node_path:
            node_path = list(node_path)
            edge_path = tosg.node_list_to_edge_list(node_path)
            return edge_path
        else:
            self._log.warning(f"{agent.name}: path_generation(): no path found")
            return []

    # this is the plan executor, maybe make it its own class.
    def plan_execution(
        self, agent: AbstractAgent, tosg: TOSG, edge_path: Sequence[Edge]
    ) -> Sequence[Optional[Edge]]:
        if not self.check_target_still_valid(tosg, self.target_node):
            self._log.warning(
                f"path_execution()::{agent.name}:: Target is no longer valid."
            )
            self.destroy_task(agent, tosg)

            return []

        self._log.debug(f"{agent.name}: action_path: {edge_path}")
        current_edge_type = tosg.get_behavior_of_edge(edge_path[0])
        self._log.debug(f"{agent.name}: current_edge_type: {current_edge_type}")

        if current_edge_type == Behavior.EXPLORE_FT_EDGE:
            edge_path = ExploreBehavior(self.cfg).execute_pipeline(
                agent, tosg, edge_path
            )
            self.destroy_task(agent, tosg)
            return []

        elif current_edge_type == Behavior.GOTO_WP_EDGE:
            edge_path = GotoBehavior(self.cfg).execute_pipeline(agent, tosg, edge_path)
            if len(edge_path) < 1:
                self.destroy_task(agent, tosg)

                return []
            else:
                return edge_path

        return edge_path

    def check_completion(self, tosg: TOSG) -> bool:
        num_of_frontiers = len(tosg.get_all_frontiers_idxs())
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
        self, agent: AbstractAgent, target_idxs: list, tosg: TOSG
    ) -> Optional[Node]:

        shortest_path_len = float("inf")
        selected_target_idx: Optional[Node] = None

        for target_idx in target_idxs:
            candidate_path_len: float = tosg.shortest_path_len(agent.at_wp, target_idx)  # type: ignore

            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                selected_target_idx = target_idx

        if not selected_target_idx:
            return

        assert selected_target_idx is not None

        return selected_target_idx
