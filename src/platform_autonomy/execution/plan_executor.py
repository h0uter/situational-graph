import logging
from typing import Mapping, Sequence, Type

from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.execution.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.shared.plan import Plan
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.sar_behaviors import Behaviors
from src.shared.situational_graph import SituationalGraph


class PlanExecutor:
    def __init__(
        self,
        domain_behaviors: Mapping[Behaviors, Type[AbstractBehavior]],
        affordances: list[Affordance],
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.DOMAIN_BEHAVIORS = domain_behaviors
        self.AFFORDANCES = affordances

    def execute_plan(self, agent: AbstractAgent, situational_graph: SituationalGraph, plan: Plan):
        behavior_of_current_edge = situational_graph.get_behavior_of_edge(plan.upcoming_edge)

        if not behavior_of_current_edge:
            self._log.error(
                f"Behavior of edge {plan.upcoming_edge} is not defined in the domain."
            )
            return BehaviorResult(success=False)

        current_edge = plan.upcoming_edge

        """Execute the behavior of the current edge"""
        # HACK: this is ugly, but used to remove dependencyo nthe behavior implementations
        result = self.DOMAIN_BEHAVIORS[behavior_of_current_edge](
            self.AFFORDANCES
        ).pipeline(agent, situational_graph, current_edge)

        return result

    @staticmethod
    def process_execution_result(result, agent: AbstractAgent, situational_graph: SituationalGraph):
        if result.success:
            agent.plan.mutate_success()
            if len(agent.plan) == 0:
                destroy_task(agent, situational_graph)
                agent.plan = None
        else:
            destroy_task(agent, situational_graph)
            agent.plan = None


def destroy_task(agent: AbstractAgent, situational_graph: SituationalGraph):
    if agent.task:
        if agent.task in situational_graph.tasks:
            situational_graph.tasks.remove(agent.task)

    agent.clear_task()
