from typing import Sequence

from src.execution.abstract_behavior import AbstractBehavior, BehaviorResult
from src.perception_processing.local_grid import LocalGrid
from src.platform.abstract_agent import AbstractAgent
from src.state.situational_graph import SituationalGraph
from src.shared.affordance import Affordance
from src.shared.node_and_edge import Edge
from src.shared.situations import Situations
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import \
    add_shortcut_edges_between_wps_on_lg


class GotoBehavior(AbstractBehavior):
    def _run_behavior_implementation(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge: Edge
    ) -> BehaviorResult:
        node_data = tosg.get_node_data_by_node(behavior_edge[1])
        success = agent.move_to_pos(node_data["pos"])
        self._localize_to_waypoint(agent, tosg)

        # return BehaviorResult(success)
        return BehaviorResult(True)

    def _check_postconditions(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        return True

    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: BehaviorResult,
        behavior_edge: Edge,
        affordances: Sequence[Affordance],
    ):
        """Mutate the graph according to the behavior."""
        lg = agent.get_local_grid()
        add_shortcut_edges_between_wps_on_lg(lg, tosg, agent)

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return tosg
        # TODO: make this remove the edge if we failed to traverse it.
        pass
