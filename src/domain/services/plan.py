from typing import Optional, Sequence

from src.domain import Edge, Behaviors
from src.domain.services.tosg import TOSG


class Plan:
    _edge_sequence: Sequence[Optional[Edge]]
    valid: bool

    # FIXME: make the plan be something that is generated and discarded.
    # make it destroy itself when it is empty or something fails.
    def __init__(self, edge_sequence: Sequence[Optional[Edge]]) -> None:
        self._edge_sequence = edge_sequence
        self.valid = False

    def __len__(self) -> int:
        return len(self.edge_sequence)

    def __getitem__(self, index: int) -> Optional[Edge]:
        return self.edge_sequence[index]

    @property
    def edge_sequence(self) -> Sequence[Optional[Edge]]:
        return self._edge_sequence

    @property
    def upcoming_edge(self) -> None:
        return self[0]

    def invalidate(self) -> None:
        self.valid = False
        self._edge_sequence = []

    def validate(self, tosg: TOSG) -> bool:
        if len(self) < 1:
            return False
        if not tosg.check_node_exists(self[-1][1]):
            return False

        return True

    def upcoming_behavior(self, tosg: TOSG) -> Behaviors:
        if self.edge_sequence:
            # return self._edge_sequence[0]
            return tosg.get_behavior_of_edge(self._edge_sequence[0])
        else:
            raise Exception("No next behavior")

    def mutate_success(self) -> None:
        self._edge_sequence.pop(0)
