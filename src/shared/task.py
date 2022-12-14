from dataclasses import dataclass
from uuid import uuid4

from src.shared.prior_knowledge.objectives import Objectives
from src.shared.types.node_and_edge import Edge


@dataclass
class Task:
    uuid = uuid4()
    edge: Edge
    objective_enum: Objectives

    @property
    def reward(self) -> float:
        return self.objective_enum.reward

    def __hash__(self):
        return id(self)
