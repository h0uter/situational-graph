from typing import Optional, Sequence

from src.shared.types.node_and_edge import Edge


class PlanModel:
    _edge_sequence: list[Optional[Edge]]
    valid: bool

    def __init__(self, edge_sequence: list[Optional[Edge]]) -> None:
        self._edge_sequence = edge_sequence

    def __len__(self) -> int:
        if self.edge_sequence:
            return len(self.edge_sequence)
        else:
            return 0

    def __getitem__(self, index: int) -> Optional[Edge]:
        return self.edge_sequence[index]

    @property
    def edge_sequence(self) -> Sequence[Optional[Edge]]:
        return self._edge_sequence

    @property
    def upcoming_edge(self) -> Optional[Edge]:
        return self[0]

    def invalidate(self) -> None:
        self._edge_sequence = []

    def mutate_success(self):
        self._edge_sequence.pop(0)
