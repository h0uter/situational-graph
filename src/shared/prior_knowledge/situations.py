from enum import Enum, auto


class Situations(Enum):
    WAYPOINT = auto()
    WORLD_OBJECT = auto()
    FRONTIER = auto()
    IMMOBILE_VICTIM = auto()
    UNKNOWN_VICTIM = auto()
    MOBILE_VICTIM = auto()

    # HOTSPOT = auto()
    # DOOR = auto()