import logging
from typing import Optional, Mapping

from src.domain.abstract_agent import AbstractAgent
from src.domain import Node, Behaviors, Objectives, Task, AbstractBehavior

from src.domain.services.plan import Plan
from src.domain.services.tosg import TOSG
from src.configuration.config import Config


class Planner:
    def __init__(
        self,
        cfg: Config,
        tosg: TOSG,
        agent: AbstractAgent,
        domain_behaviors: Mapping[Behaviors, AbstractBehavior],
    ) -> None:
        self.cfg = cfg
        self.completed = False  # TODO: remove this
        self._log = logging.getLogger(__name__)
        self.DOMAIN_BEHAVIORS = domain_behaviors

        self._initialize(tosg, agent)

    def _initialize(self, tosg: TOSG, agent):
        # Add an explore self edge on the start node to ensure a exploration sampling action
        edge_uuid = tosg.add_my_edge(0, 0, Behaviors.EXPLORE)
        tosg.tasks.append(Task(edge_uuid, Objectives.EXPLORE_ALL_FTS))

        # spoof the task selection, just select the first one.
        agent.task = tosg.tasks[0]

        # obtain the plan which corresponds to this edge.
        init_explore_edge = tosg.get_task_edge(agent.task)

        agent.plan = Plan([init_explore_edge])
        self._log.debug(f"target node: {agent.target_node}")

    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        """select a task"""
        if not agent.task:
            agent.task = self._task_selection(agent, tosg)

        """ generate a plan"""
        if not agent.plan:
            agent.plan = self._find_plan_for_task(agent.at_wp, tosg, agent.task)

        """ execute the plan"""
        if agent.plan and len(agent.plan) >= 1:
            agent.plan = self._plan_execution(agent, tosg, agent.plan)

            if agent.plan and len(agent.plan) == 0:
                self._destroy_task(agent, tosg)

        """check completion of mission"""
        if self._check_if_tasks_exhausted(tosg):
            self.completed = True

        return self.completed

    def _destroy_task(self, agent: AbstractAgent, tosg: TOSG):
        self._log.debug(f"{agent.name}:  has a task  {agent.task}")

        if agent.task:
            if agent.task in tosg.tasks:
                tosg.tasks.remove(agent.task)
        self._log.debug(f"{agent.name}: destroying task  {agent.task}")

        agent.clear_task()

    def _check_target_still_valid(
        self, tosg: TOSG, target_node: Optional[Node]
    ) -> bool:
        if target_node is None:
            return False
        return tosg.check_node_exists(target_node)

    def _task_selection(self, agent: AbstractAgent, tosg: TOSG) -> Optional[Task]:
        highest_utility = 0
        optimal_task = None

        for task in tosg.tasks:

            task_target_node = tosg.get_task_target_node(task)
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

    def _find_plan_for_task(
        self, agent_localized_to: Node, tosg: TOSG, task: Task
    ) -> Optional[Plan]:

        target_node = tosg.get_task_target_node(task)
        if not self._check_target_still_valid(tosg, target_node):
            return None

        edge_path = tosg.shortest_path(agent_localized_to, target_node)

        return Plan(edge_path)

    # this is the plan executor, maybe make it its own class.
    def _plan_execution(
        self, agent: AbstractAgent, tosg: TOSG, plan: Plan
    ) -> Optional[Plan]:

        if not plan.validate(tosg):
            return None

        behavior_of_current_edge = plan.upcoming_behavior(tosg)
        current_edge = plan.upcoming_edge

        # FIXME: this should be dependency injected.
        """Execute the behavior of the current edge"""
        result = self.DOMAIN_BEHAVIORS[behavior_of_current_edge](self.cfg).pipeline(
            agent, tosg, current_edge
        )

        # FIXME: this can be shorter
        if result.success:
            self._log.debug(f"the plan is {plan}")
            plan.mutate_success()
            if len(plan) == 0:
                self._destroy_task(agent, tosg)
                return None
            return plan
        else:
            self._destroy_task(agent, tosg)
            return None

    def _check_if_tasks_exhausted(self, tosg: TOSG) -> bool:
        # HACK: we just check the fronteirs, not the tasks.
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
    def _evaluate_potential_target_nodes_based_on_path_cost(
        self, agent: AbstractAgent, target_nodes: list[Node], tosg: TOSG
    ) -> Optional[Node]:

        shortest_path_len = float("inf")
        selected_target_idx: Optional[Node] = None

        for target_idx in target_nodes:
            candidate_path_len: float = tosg.shortest_path_len(agent.at_wp, target_idx)  # type: ignore

            if candidate_path_len < shortest_path_len and candidate_path_len != 0:
                shortest_path_len = candidate_path_len
                selected_target_idx = target_idx

        if not selected_target_idx:
            return

        # assert selected_target_idx is not None

        return selected_target_idx
