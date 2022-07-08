from enum import Enum, auto


class ObjectTypes(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()
    HOTSPOT = auto()
    DOOR = auto()
    # TODO: add VICTIM, DOOR
