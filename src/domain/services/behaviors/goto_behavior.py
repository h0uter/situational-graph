from src.domain.services.behaviors.abstract_behavior import AbstractBehavior, BehaviorResult
from src.configuration.config import Config


class GotoBehavior(AbstractBehavior):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def _run_behavior_implementation(
        self, agent, tosgraph, behavior_edge
    ) -> BehaviorResult:
        node_data = tosgraph.get_node_data_by_node(behavior_edge[1])
        agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(tosgraph)
        return BehaviorResult(True)

    def _check_postconditions(self, agent, tosgraph, result, behavior_edge) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def _mutate_graph_and_tasks_success(self, agent, tosgraph, next_node, affordances):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        pass

    def _mutate_graph_and_tasks_failure(self, agent, tosgraph, behavior_edge):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        pass
