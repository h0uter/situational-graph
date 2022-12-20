from typing import Sequence

from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.execution.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.platform_autonomy.execution.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.situational_graph import SituationalGraph
from src.shared.types.node_and_edge import Edge


class GotoBehavior(AbstractBehavior):
    def _run_behavior_implementation(
        self, agent: AbstractAgent, situational_graph: SituationalGraph, behavior_edge: Edge
    ) -> BehaviorResult:
        node_data = situational_graph.get_node_data_by_node(behavior_edge[1])
        success = agent.move_to_pos(node_data["pos"])
        agent.at_wp = situational_graph.get_closest_waypoint_to_pos(agent.get_localization())

        # return BehaviorResult(success)
        return BehaviorResult(True)

    def _check_postconditions(
        self,
        agent: AbstractAgent,
        situational_graph: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        situational_graph: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: Sequence[Affordance],
    ):
        """Mutate the graph according to the behavior."""
        lg = agent.get_local_grid()
        add_shortcut_edges_between_wps_on_lg(lg, situational_graph, agent)

    def mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, situational_graph: SituationalGraph, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return situational_graph
        # TODO: make this remove the edge if we failed to traverse it.
        pass
