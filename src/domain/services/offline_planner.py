import copy
import logging
from typing import Mapping, Optional, Sequence, Type
import networkx as nx

from src.configuration.config import Config
from src.domain import TOSG, AbstractBehavior, Affordance, Behaviors, Node, Plan, Task, Edge
from src.domain.services.abstract_agent import AbstractAgent


class CouldNotFindPlan(Exception):
    pass


class CouldNotFindTask(Exception):
    pass


class TargetNodeNotFound(Exception):
    pass


class OfflinePlanner:
    def __init__(
        self,
        cfg: Config,
        domain_behaviors: Mapping[Behaviors, Type[AbstractBehavior]],
        affordances: Sequence[Affordance],
    ) -> None:
        self.cfg = cfg
        self._log = logging.getLogger(__name__)
        self.DOMAIN_BEHAVIORS = domain_behaviors
        self.AFFORDANCES = affordances

    def pipeline(self, agent: AbstractAgent, tosg: TOSG) -> bool:
        """filter the graph over the agent capabilities"""
        def my_edge_filter(u, v, k) -> bool:
            behavior_enum = tosg.G.edges[u, v, k]['type']  # Behaviors
            for req_cap in behavior_enum.required_capabilities:
                print(f"req_cap: {req_cap}")
                if req_cap not in agent.capabilities:
                    return False
            return True


        filtered_G = nx.subgraph_view(tosg.G, filter_edge=my_edge_filter)
        print(filtered_G)
        filtered_tosg = copy.deepcopy(tosg)
        filtered_tosg.G = filtered_G

        # TODO: so what I need to do is make these functions operate on an actual graph, not the complext tosg object
        # a path over the filtered graphs can be executed on the tosg.
        # need to refactor to tasks and graph

        # A. refactor all tosg methods to just take a graph as argument.
        # B make my filtered graph be a filtered tosg
        
        """select a task"""
        if not agent.task:
            # agent.task = self._task_selection(agent, tosg)
            agent.task = self._task_selection(agent, filtered_tosg)
            if not agent.task:
                raise CouldNotFindTask(f"Could not find a task for agent {agent.name}")

        """ generate a plan"""
        if not agent.plan:
            try:
                agent.plan = self._find_plan_for_task(agent.at_wp, tosg, agent.task)
                # agent.plan = self._find_plan_for_task(agent.at_wp, filtered_tosg, agent.task)
            except CouldNotFindPlan:
                self._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                self._log.error(f"Could not find a target node for task {agent.task}")
                agent.clear_task()

        """ execute the plan"""
        if agent.plan and len(agent.plan) >= 1:
            agent.plan = self._plan_execution(agent, tosg, agent.plan)

            if agent.plan and len(agent.plan) == 0:
                self._destroy_task(agent, tosg)

        """check completion of mission"""
        return self._check_if_tasks_exhausted(tosg)

    def _destroy_task(self, agent: AbstractAgent, tosg: TOSG):
        self._log.debug(f"{agent.name}:  has a task  {agent.task}")

        if agent.task:
            if agent.task in tosg.tasks:
                tosg.tasks.remove(agent.task)
                # tosg.destroy_task_and_edge(agent.task)
        self._log.debug(f"{agent.name}: destroying task  {agent.task}")

        agent.clear_task()

    def _check_target_still_valid(
        self, tosg: TOSG, target_node: Optional[Node]
    ) -> bool:
        if target_node is None:
            return False
        return tosg.G.has_node(target_node)

    def _task_selection(self, agent: AbstractAgent, tosg: TOSG) -> Optional[Task]:
        highest_utility: float = 0
        optimal_task = None

        for task in tosg.tasks:

            task_target_node = task.edge[1]

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
    ) -> Plan:
        target_node = task.edge[1]

        if not self._check_target_still_valid(tosg, target_node):
            # return None
            raise TargetNodeNotFound("Target node is not valid")

        edge_path = tosg.shortest_path(agent_localized_to, target_node)

        # if the agent can find a plan for that task we remove the task
        # this is necc for the initial task of exploration.
        if edge_path is None:
            tosg.tasks.remove(task)
            # return None
            raise CouldNotFindPlan(f"Could not find a plan for task {task}")

        return Plan(edge_path)

    # this is the plan executor, maybe make it its own class.
    def _plan_execution(
        self, agent: AbstractAgent, tosg: TOSG, plan: Plan
    ) -> Optional[Plan]:

        if not tosg.validate_plan(plan):
            return None

        behavior_of_current_edge = tosg.get_behavior_of_edge(plan.upcoming_edge)

        current_edge = plan.upcoming_edge

        """Execute the behavior of the current edge"""
        result = self.DOMAIN_BEHAVIORS[behavior_of_current_edge](
            self.cfg, self.AFFORDANCES
        ).pipeline(agent, tosg, current_edge)

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
        num_of_tasks = len(tosg.tasks)
        if num_of_tasks < 1:
            return True
        else:
            return False
