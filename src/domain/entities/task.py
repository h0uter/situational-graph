from dataclasses import dataclass
from uuid import UUID, uuid4
from src.domain import Objectives


@dataclass
class Task:
    uuid = uuid4()
    edge_uuid: UUID
    objective_enum: Objectives

    @property
    def reward(self) -> float:
        return self.objective_enum.reward
