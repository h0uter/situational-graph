from enum import Enum


class Topics(Enum):
    SHORTCUT_CHECKING = "shortcut checking data"
    FRONTIER_SAMPLING = "frontier sampling data"
    
    MISSION_VIEW_UPDATE = "mission view update"
    MISSION_VIEW_UPDATE_FINAL = "mission view update final"
    MISSION_VIEW_START_POINT = "mission view start point"

    IMAGE_MAPDEBUG_VIEW = "debug map view"

    RUN_PLATFORM = "run platform"

    TASK_UTILITIES = "task utilities"