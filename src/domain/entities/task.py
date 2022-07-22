from dataclasses import dataclass
from uuid import UUID, uuid4
from src.domain import Objectives
from src.domain.entities.node_and_edge import Edge


@dataclass
class Task:
    uuid = uuid4()
    # edge_uuid: UUID
    edge_uuid: Edge
    objective_enum: Objectives

    @property
    def reward(self) -> float:
        return self.objective_enum.reward
