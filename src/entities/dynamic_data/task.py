from dataclasses import dataclass
from typing import Optional, Protocol
from uuid import UUID, uuid4
from src.entities.static_data.objectives import Objectives
from src.entities.dynamic_data.node_and_edge import Edge, Node


class TOSG(Protocol):
    def get_edge_by_UUID(self, uuid) -> Edge:
        pass


@dataclass
class Task:
    uuid = uuid4()
    edge_uuid: UUID
    objective_enum: Objectives

    @property
    def reward(self):
        return self.objective_enum.reward

    def get_edge(self, tosg: TOSG) -> Edge:
        return tosg.get_edge_by_UUID(self.edge_uuid)

    def get_target_node(self, tosg: TOSG) -> Optional[Node]:
        edge = self.get_edge(tosg)
        if edge:
            return edge[1]
        else:
            # BUG: this often happens
            # raise ValueError("Edge not found")
            return None
