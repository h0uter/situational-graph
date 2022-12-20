from dataclasses import dataclass
from enum import Enum, auto
from random import random

from src.config import cfg
from src.platform_autonomy.control.abstract_agent import AbstractAgent
from src.platform_autonomy.control.audio_feedback import play_file
from src.platform_autonomy.execution.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.situational_graph import SituationalGraph
from src.shared.types.node_and_edge import Edge


class VictimState(Enum):
    MOBILE = auto()
    IMMMOBILE = auto()
    UNKNOWN = auto()


@dataclass
class AssessResult(BehaviorResult):
    victim_state: VictimState


class AssessBehavior(AbstractBehavior):
    def _run_behavior_implementation(
        self, agent, tosgraph, behavior_edge
    ) -> AssessResult:
        target_node_pos = tosgraph.get_node_data_by_node(behavior_edge[1])["pos"]
        victim_state = self.__scan_victim(target_node_pos)

        return AssessResult(True, victim_state)

    def _check_postconditions(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: AssessResult,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        if result.victim_state == VictimState.UNKNOWN:
            return True
        else:
            return True

    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        result: AssessResult,
        behavior_edge: Edge,
        affordances: list[Affordance],
    ):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        # transform the target node object into the state of the victim
        # the goal here is to get this graph transformation rolling.

        VICTIM_STATE_TO_OBJECT_TYPE = {
            VictimState.MOBILE: Situations.MOBILE_VICTIM,
            VictimState.IMMMOBILE: Situations.IMMOBILE_VICTIM,
            VictimState.UNKNOWN: Situations.UNKNOWN_VICTIM,
        }

        # remove the target node
        old_pos = tosg.get_node_data_by_node(behavior_edge[1])["pos"]
        tosg.G.remove_node(behavior_edge[1])

        my_object_type = VICTIM_STATE_TO_OBJECT_TYPE[result.victim_state]

        from_edge = behavior_edge[0]
        tosg.add_node_with_task_and_edges_from_affordances(
            from_edge, my_object_type, old_pos, affordances
        )

    def mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: SituationalGraph, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        # deactivate the target node,
        tosg.G.remove_node(behavior_edge[1])

    def __scan_victim(self, target_node_pos: tuple[float, float]):
        # todo make this actually orient the robot towards the target and perform some scan or assessment.
        # use the play file library to say some shit and emulate listening for the response.

        if cfg.AUDIO_FEEDBACK:
            play_file("assessment.mp3")

        if random() < 0.5:
            return VictimState.MOBILE
        else:
            return VictimState.IMMMOBILE
