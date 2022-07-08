from typing import Optional, Sequence
from src.entities.static_data.behaviors import Behavior

from src.entities.tosg import TOSG
from src.utils.my_types import Edge, Node


class Plan:
    _edge_sequence: Sequence[Optional[Edge]]
    valid: bool

    # FIXME: make the plan be something that is generated and discarded.
    # make it destroy itself when it is empty or something fails.
    def __init__(self, edge_sequence: Sequence[Optional[Edge]]) -> None:
        self._edge_sequence = edge_sequence
        self.valid = False

    def invalidate(self) -> None:
        self.valid = False
        self._edge_sequence = []

    def validate(self, tosg: TOSG) -> bool:
        if len(self) < 1:
            return False
        if not tosg.check_node_exists(self[-1][1]):
            return False

        return True

    @property
    def edge_sequence(self) -> Sequence[Optional[Edge]]:
        return self._edge_sequence

    @edge_sequence.setter
    def edge_sequence(self, value: Sequence[Optional[Edge]]) -> None:
        if self.validate(value):
            self._edge_sequence = value
        else:
            self.invalidate()

    def upcoming_behavior(self, tosg: TOSG) -> Behavior:
        if self.edge_sequence:
            # return self._edge_sequence[0]
            return tosg.get_behavior_of_edge(self._edge_sequence[0])
        else:
            raise Exception("No next behavior")

    def __len__(self) -> int:
        return len(self.edge_sequence)

    def __getitem__(self, index: int) -> Optional[Edge]:
        return self.edge_sequence[index]

    def mutate(self) -> None:
        self.edge_sequence.pop(0)
