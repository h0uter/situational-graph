from dataclasses import dataclass
from enum import Enum, auto
from random import random
from typing import Sequence
from src.domain.abstract_agent import AbstractAgent
from src.domain.entities.affordance import Affordance
from src.domain.entities.node_and_edge import Edge
from src.domain.entities.object_types import ObjectTypes
from src.domain.services.behaviors.abstract_behavior import (
    AbstractBehavior,
    BehaviorResult,
)
from src.configuration.config import Config
from src.domain.services.tosg import TOSG


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
        tosg: TOSG,
        result: AssessResult,
        behavior_edge: Edge,
    ) -> bool:
        """Check if the postconditions for the behavior are met."""
        if not result.victim_state == VictimState.UNKNOWN:
            return True
        else:
            return False

    def _mutate_graph_and_tasks_success(
        self,
        agent: AbstractAgent,
        tosg: TOSG,
        result: AssessResult,
        behavior_edge: Edge,
        affordances: Sequence[Affordance],
    ):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        # transform the target node object into the state of the victim
        # the goal here is to get this graph transformation rolling.

        VICTIM_STATE_TO_OBJECT_TYPE = {
            VictimState.MOBILE: ObjectTypes.MOBILE_VICTIM,
            VictimState.IMMMOBILE: ObjectTypes.IMMOBILE_VICTIM,
            VictimState.UNKNOWN: ObjectTypes.UNKNOWN_VICTIM,
        }

        # remove the target node
        old_pos = tosg.get_node_data_by_node(behavior_edge[1])["pos"]
        tosg.remove_node(behavior_edge[1])

        # add the target node with the ObjectType corresponding to the victim
        mutated_node = tosg.add_node(old_pos, VICTIM_STATE_TO_OBJECT_TYPE[result.victim_state])

        # use the affordances to add the correct edges.

        for aff in affordances:
            if aff[0] == VICTIM_STATE_TO_OBJECT_TYPE[result.victim_state]:
                tosg.add_my_edge(behavior_edge[0], mutated_node, aff[1])

    def _mutate_graph_and_tasks_failure(
        self, agent: AbstractAgent, tosg: TOSG, behavior_edge: Edge
    ):
        """Mutate the graph according to the behavior."""
        # return tosgraph
        # deactivate the target node, 
        tosg.remove_node(behavior_edge[1])
        # pass

    def __scan_victim(self, targt_node_pos: tuple[float, float]):
        # todo make this actually orient the robot towards the target and perform some scan or assessment.
        # use the play file library to say some shit and emulate listening for the response.
        if random() < 0.5:
            return VictimState.MOBILE
        else:
            return VictimState.IMMMOBILE
