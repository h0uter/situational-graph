import logging
from typing import Mapping, Sequence, Type

from src.platform.autonomy.abstract_behavior import AbstractBehavior
from src.platform.autonomy.plan_model import PlanModel
from src.mission.situational_graph import SituationalGraph
from src.platform.control.abstract_agent import AbstractAgent
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.behaviors import Behaviors


class PlanExecutor:
    def __init__(
        self,
        domain_behaviors: Mapping[Behaviors, Type[AbstractBehavior]],
        affordances: Sequence[Affordance],
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.DOMAIN_BEHAVIORS = domain_behaviors
        self.AFFORDANCES = affordances

    def _plan_execution(
        self, agent: AbstractAgent, tosg: SituationalGraph, plan: PlanModel
    ):

        behavior_of_current_edge = tosg.get_behavior_of_edge(plan.upcoming_edge)

        current_edge = plan.upcoming_edge

        """Execute the behavior of the current edge"""
        result = self.DOMAIN_BEHAVIORS[behavior_of_current_edge](
            self.AFFORDANCES
        ).pipeline(agent, tosg, current_edge)

        return result

    @staticmethod
    def process_execution_result(result, agent: AbstractAgent, tosg: SituationalGraph):

        if result.success:
            agent.plan.mutate_success()
            if len(agent.plan) == 0:
                destroy_task(agent, tosg)
                agent.plan = None
        else:
            destroy_task(agent, tosg)
            agent.plan = None

        """check completion of mission"""
        tasks_exhausted = tosg.check_if_tasks_exhausted()

        return tasks_exhausted


def destroy_task(agent: AbstractAgent, tosg: SituationalGraph):
    if agent.task:
        if agent.task in tosg.tasks:
            tosg.tasks.remove(agent.task)

    agent.clear_task()
