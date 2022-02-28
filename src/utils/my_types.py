from typing import Union
from enum import Enum, auto

Node = Union[str, int]


class NodeType(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()


class EdgeType(Enum):
    WAYPOINT_EDGE = auto()
    FRONTIER_EDGE = auto()
    WORLD_OBJECT_EDGE = auto()
