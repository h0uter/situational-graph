import logging
from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence, Type

import networkx as nx

import src.shared.event_system as event_system
from src.execution_autonomy.abstract_behavior import AbstractBehavior
from src.execution_autonomy.plan_model import PlanModel
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.shared.node_and_edge import Node
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.behaviors import Behaviors
from src.shared.task import Task


class CouldNotFindPlan(Exception):
    pass


class CouldNotFindTask(Exception):
    pass


class TargetNodeNotFound(Exception):
    pass


class AbstractPlanner(ABC):
    def __init__(
        self,
        domain_behaviors: Mapping[Behaviors, Type[AbstractBehavior]],
        affordances: Sequence[Affordance],
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.DOMAIN_BEHAVIORS = domain_behaviors
        self.AFFORDANCES = affordances

    @abstractmethod
    def pipeline(self, agent: AbstractAgent, tosg: SituationalGraph) -> bool:
        pass

    def _filter_graph(self, tosg: SituationalGraph, agent: AbstractAgent) -> SituationalGraph:
        def filter_edges_based_on_agent_capabilities(u: Node, v: Node, k: Node) -> bool:
            behavior_enum = tosg.G.edges[u, v, k]["type"]  # Behaviors
            for req_cap in behavior_enum.required_capabilities:
                if req_cap not in agent.capabilities:
                    return False
            return True

        filtered_G = nx.subgraph_view(
            tosg.G, filter_edge=filter_edges_based_on_agent_capabilities
        )

        # here we insert the filtered graph into a new tosg object
        filtered_tosg = SituationalGraph()
        filtered_tosg.tasks = tosg.tasks
        filtered_tosg.G = filtered_G
        return filtered_tosg

    # TODO: instead of removing tasks we should remove unssuccessfull edges, and this can then indirectly remove a task.
    def _destroy_task(self, agent: AbstractAgent, tosg: SituationalGraph):
        self._log.debug(f"{agent.name}:  has a task  {agent.task}")

        if agent.task:
            if agent.task in tosg.tasks:
                tosg.tasks.remove(agent.task)
        self._log.debug(f"{agent.name}: destroying task  {agent.task}")

        agent.clear_task()

    def _check_target_still_valid(
        self, tosg: SituationalGraph, target_node: Optional[Node]
    ) -> bool:
        if target_node is None:
            return False
        return tosg.G.has_node(target_node)

    def _task_selection(self, agent: AbstractAgent, tosg: SituationalGraph) -> Optional[Task]:
        target_node_to_task = {task.edge[1]: task for task in tosg.tasks}

        path_costs, paths = tosg.distance_and_path_dijkstra(
            agent.at_wp, target_node_to_task.keys()
        )

        # TODO: depending on the number of tasks switch between dijkstra lookup and A* lookup
        # path_cost = tosg.distance_astar(agent.at_wp, task_target_node)

        def calc_utility(reward: float, path_cost: float) -> float:
            if path_cost == 0:
                return float("inf")
            else:
                return reward / path_cost

        # utility_to_task = {calc_utility(task.reward, path_costs[task.edge[1]]): task for task in tosg.tasks if task.edge[1] in path_costs}
        # highest_utility = max(utility_to_task.keys())
        # event.post_event("task_utilities", utility_to_task)
        # return utility_to_task[highest_utility]

        task_to_utility = {
            task: calc_utility(task.reward, path_costs[task.edge[1]])
            for task in tosg.tasks
            if task.edge[1] in path_costs
        }

        event_system.post_event("task_utilities", task_to_utility)

        if len(task_to_utility) == 0:
            return None

        return max(task_to_utility, key=task_to_utility.get)

    def _find_plan_for_task(
        self, agent_localized_to: Node, full_tosg: SituationalGraph, task: Task, filtered_tosg: SituationalGraph
    ) -> PlanModel:
        target_node = task.edge[1]

        if not self._check_target_still_valid(full_tosg, target_node):
            raise TargetNodeNotFound("Target node is not valid")

        edge_path = filtered_tosg.shortest_path(agent_localized_to, target_node)

        # if the agent can find a plan for that task we remove the task
        # this is necc for the initial task of exploration.
        if edge_path is None:
            full_tosg.tasks.remove(task)
            raise CouldNotFindPlan(f"Could not find a plan for task {task}")

        return PlanModel(edge_path)

    def validate_plan(self, plan: PlanModel, tosg: SituationalGraph) -> bool:
        if not plan:
            return False
        if len(plan) < 1:
            return False
        if not tosg.G.has_node(plan[-1][1]):
            return False

        return True

    # this is the plan executor, maybe make it its own class.
    def _plan_execution(
        self, agent: AbstractAgent, tosg: SituationalGraph, plan: PlanModel
    ) -> Optional[PlanModel]:

        if not self.validate_plan(plan, tosg):
            return None

        behavior_of_current_edge = tosg.get_behavior_of_edge(plan.upcoming_edge)

        current_edge = plan.upcoming_edge

        """Execute the behavior of the current edge"""
        result = self.DOMAIN_BEHAVIORS[behavior_of_current_edge](
            self.AFFORDANCES
        ).pipeline(agent, tosg, current_edge)

        # FIXME: this can be shorter
        if result.success:
            # self._log.debug(f"the plan is {plan}")
            plan.mutate_success()
            # this is duplicate with the check in calling the plan executor
            if len(plan) == 0:
                self._destroy_task(agent, tosg)
                return None
            return plan
        else:
            self._destroy_task(agent, tosg)
            return None

    def _check_if_tasks_exhausted(self, tosg: SituationalGraph) -> bool:
        num_of_tasks = len(tosg.tasks)
        if num_of_tasks < 1:
            return True
        else:
            return False