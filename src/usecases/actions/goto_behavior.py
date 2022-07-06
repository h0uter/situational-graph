from typing import Sequence
from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.actions.abstract_behavior import AbstractBehavior
from src.utils.config import Config


class GotoBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def execute_pipeline(self, agent, tosgraph, plan) -> Sequence:
        """Execute the behavior pipeline."""

        behavior_edge = plan[0]
        if not self.check_preconditions(agent, tosgraph, behavior_edge):
            return []

        result = self.run(agent, tosgraph, behavior_edge)

        if self.check_postconditions(agent, result):
            tosgraph = self.mutate_graph_success(agent, tosgraph)
            plan.pop(0)
        else:
            tosgraph = self.mutate_graph_failure(agent, tosgraph)
            plan = []

        return plan

    def check_preconditions(self, agent, tosgraph, behavior_edge) -> bool:
        return True

    def run(self, agent, tosgraph, behavior_edge):
        node_data = tosgraph.get_node_data_by_node(behavior_edge[1])
        agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(tosgraph)
        return {}

    def check_postconditions(self, agent, tosgraph) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def mutate_graph_success(self, agent, tosgraph) -> Sequence:
        """Mutate the graph according to the behavior."""
        return tosgraph

    def mutate_graph_failure(self, agent, tosgraph) -> Sequence:
        """Mutate the graph according to the behavior."""
        return tosgraph