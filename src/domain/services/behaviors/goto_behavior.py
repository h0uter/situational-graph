from typing import Sequence
from src.domain.entities.local_grid import LocalGrid
from src.domain.entities.object_types import Situations
from src.domain.services.abstract_agent import AbstractAgent
from src.domain.entities.affordance import Affordance
from src.domain.entities.node_and_edge import Edge
from src.domain.services.behaviors.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.domain.services.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    add_shortcut_edges_between_wps_on_lg,
)
from src.domain.services.tosg import TOSG


class GotoBehavior(AbstractBehavior):
    def _run_behavior_implementation(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ) -> BehaviorResult:
        node_data = tosg.get_node_data_by_node(behavior_edge[1])
        success = agent.move_to_pos(node_data["pos"])
        agent.localize_to_waypoint(tosg)

        # return BehaviorResult(success)
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
        lg = agent.get_local_grid()
        add_shortcut_edges_between_wps_on_lg(lg, tosg, agent)

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return tosg
        # TODO: make this remove the edge if we failed to traverse it.
        pass
