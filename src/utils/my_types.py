from enum import Enum, auto
from typing import Union

Node = Union[str, int]
# Edge = tuple[Union[str, int], Union[str, int]]
Edge = tuple[Union[str, int], Union[str, int], int]


class NodeType(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()


# this is the start for my knowledge base action types domain.pddl etc
class Behavior(Enum):
    GOTO_WP_EDGE = auto()
    EXPLORE_FT_EDGE = auto()
    PLAN_EXTRACTION_WO_EDGE = auto()
    GUIDE_WP_EDGE = auto()
