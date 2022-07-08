from enum import Enum, auto


class ObjectType(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()
    HOTSPOT = auto()
    DOOR = auto()
    # TODO: add VICTIM, DOOR, 