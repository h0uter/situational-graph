from enum import Enum, auto


class ObjectTypes(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()
    HOTSPOT = auto()
    DOOR = auto()
    IMMOBILE_VICTIM = auto()
    UNKNOWN_VICTIM = auto()
    MOBILE_VICTIM = auto()
    # TODO: add VICTIM, DOOR
