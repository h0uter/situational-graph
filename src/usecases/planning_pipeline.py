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
        self.completed = False  # TODO: remove this
        self.plan: Optional[Plan]
        self._log = logging.getLogger(__name__)

        self.initialize(tosg, agent)

    @property
    def target_node(self) -> Optional[Node]:
        if len(self.plan) >= 1:
            return self.plan[-1][1]
        else:
            self.plan.invalidate()
            return None

    def initialize(self, tosg: TOSG, agent):
        # Add an explore self edge on the start node to ensure a exploration sampling action
        edge_uuid = tosg.add_my_edge(0, 0, Behavior.EXPLORE_FT_EDGE)
        tosg.tasks.append(Task(edge_uuid, Objective.EXPLORE))

        # spoof the task selection, just select the first one.
        agent.task = tosg.tasks[0]

        # obtain the plan which corresponds to this edge.
        init_explore_edge = tosg.get_edge_by_UUID(agent.task.edge_uuid)

        self.plan = Plan([init_explore_edge])
        self._log.debug(f"target node: {self.target_node}")

    # CONTEXT
    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        """select a task"""
        if not agent.task:
            agent.task = self.task_selection(agent, tosg)

        """ generate a plan"""
        if not self.plan:
            self.plan = self.find_plan_for_task(agent.at_wp, tosg, agent.task)

        """ execute the plan"""
        if self.plan and len(self.plan) >= 1:
            # mutated_plan = self.plan_execution(agent, tosg, self.plan.edge_sequence)
            self.plan = self.plan_execution(agent, tosg, self.plan)
            # self.plan.edge_sequence = mutated_plan

            if self.plan and len(self.plan) == 0:
                self.destroy_task(agent, tosg)

        """check completion of mission"""
        if self.check_if_tasks_exhausted(tosg):
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
        self, agent_localized_to: Node, tosg: TOSG, task: Task
    ) -> Optional[Plan]:
        
        target_node = task.get_target_node(tosg)
        if not self.check_target_still_valid(tosg, target_node):
            return None

        edge_path = tosg.shortest_path(agent_localized_to, target_node)

        return Plan(edge_path)

    # this is the plan executor, maybe make it its own class.
    def plan_execution(
        self, agent: AbstractAgent, tosg: TOSG, plan: Plan
    ) -> Optional[Plan]:

        if not plan.validate(tosg):
            return None

        # current_edge_type = tosg.get_behavior_of_edge(edge_path[0])
        current_edge_type = plan.next_behavior(tosg)

        if current_edge_type == Behavior.EXPLORE_FT_EDGE:
            '''exploration'''
            edge_path = ExploreBehavior(self.cfg).execute_pipeline(
                agent, tosg, plan.edge_sequence
            )
            self.destroy_task(agent, tosg)
            return None

        elif current_edge_type == Behavior.GOTO_WP_EDGE:
            '''goto'''
            edge_path = GotoBehavior(self.cfg).execute_pipeline(agent, tosg, plan.edge_sequence)
            if len(edge_path) < 1:
                self.destroy_task(agent, tosg)

                return None
            else:
                # TODO: here we should execute the plan as a method of the plan.
                return Plan(edge_path)

        # return Plan(edge_path)

    def check_if_tasks_exhausted(self, tosg: TOSG) -> bool:
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
