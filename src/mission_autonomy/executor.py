import logging
from typing import Mapping, Type, Sequence

from src.execution_autonomy.abstract_behavior import AbstractBehavior
from src.execution_autonomy.plan_model import PlanModel
from src.mission_autonomy.situational_graph import SituationalGraph
from src.platform_control.abstract_agent import AbstractAgent
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.behaviors import Behaviors


class Executor:
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
