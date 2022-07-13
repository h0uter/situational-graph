from typing import Sequence
from src.domain.abstract_agent import AbstractAgent
from src.domain.entities.affordance import Affordance
from src.domain.entities.node_and_edge import Edge
from src.domain.services.behaviors.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.configuration.config import Config
from src.domain.services.tosg import TOSG


class GotoBehavior(AbstractBehavior):
    def _run_behavior_implementation(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ) -> BehaviorResult:
        node_data = tosg.get_node_data_by_node(behavior_edge[1])
        agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(tosg)
        return BehaviorResult(True)

    def _check_postconditions(
        self,
        agent: AbstractAgent,
        tosg: TOSG,
        result: BehaviorResult,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: TOSG,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: Sequence[Affordance],
    ):
        """Mutate the graph according to the behavior."""
        # return tosg
        pass

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return tosg
        pass
