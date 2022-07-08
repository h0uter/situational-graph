from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid4
from src.entities.static_data.objective import Objective
from src.utils.my_types import Edge


class TOSG(Protocol):
    def get_edge_by_UUID(self, uuid) -> Edge:
        pass

@dataclass
class Task:
    uuid = uuid4()
    edge_uuid: UUID
    objective_enum: Objective

    @property
    def reward(self):
        return self.objective_enum.reward

    def get_edge(self, tosg: TOSG) -> Edge:
        return tosg.get_edge_by_UUID(self.edge_uuid)

    def get_target_node(self, tosg: TOSG):
        edge = self.get_edge(tosg)
        if edge:
            return edge[1]
