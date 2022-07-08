from enum import Enum, auto
from typing import Union

Node = Union[str, int]
# Edge = tuple[Union[str, int], Union[str, int]]
Edge = tuple[Union[str, int], Union[str, int], int]


# class ObjectType(Enum):
#     WAYPOINT = auto()
#     WORLD_OBJECT = auto()
#     FRONTIER = auto()
#     HOTSPOT = auto()
#     DOOR = auto()
#     # TODO: add VICTIM, DOOR,
