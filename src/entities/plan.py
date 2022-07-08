from typing import Optional, Sequence
from src.utils.my_types import Edge, Behavior, Node


class Plan:
    _edge_sequence: Sequence[Optional[Edge]]
    valid: bool

    #FIXME: make the plan be something that is generated and discarded.
    # make it destroy itself when it is empty or something fails.
    def __init__(self, edge_sequence) -> None:
        self._edge_sequence = edge_sequence
        self.valid = False

    def invalidate(self) -> None:
        self.valid = False
        self._edge_sequence = []

    def validate(self, plan) -> bool:
        if len(plan) > 0:
            self.valid = True
        else:
            self.valid = False
        return self.valid

    @property
    def edge_sequence(self) -> Sequence[Optional[Edge]]:
        return self._edge_sequence

    @edge_sequence.setter
    def edge_sequence(self, value: Sequence[Optional[Edge]]) -> None:
        if self.validate(value):
            self._edge_sequence = value
        else:
            self.invalidate()

    # @property
    # def next_behavior(self) -> Edge:
    #     if self.edge_sequence:
    #         return self.edge_sequence[0]
    #     else:
    #         raise Exception("No next behavior")

    def __len__(self) -> int:
        return len(self.edge_sequence)

    def __getitem__(self, index: int) -> Optional[Edge]:
        return self.edge_sequence[index]

    def execute_step(self, edge: Edge) -> None:
        self.edge_sequence.pop(0)
