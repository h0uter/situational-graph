from typing import Sequence
from src.entities.abstract_agent import AbstractAgent
from src.entities.tosg import TOSG
from src.usecases.behaviors.abstract_behavior import AbstractBehavior, BehaviorResult
from src.utils.config import Config


class GotoBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run_implementation(self, agent, tosgraph, behavior_edge) -> BehaviorResult:
        node_data = tosgraph.get_node_data_by_node(behavior_edge[1])
        agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(tosgraph)
        return BehaviorResult(True)

    def check_postconditions(self, agent, tosgraph, result, plan) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def mutate_graph_success(self, agent, tosgraph, next_node, affordances) -> Sequence:
        """Mutate the graph according to the behavior."""
        return tosgraph

    def mutate_graph_failure(self, agent, tosgraph, behavior_edge) -> Sequence:
        """Mutate the graph according to the behavior."""
        return tosgraph
