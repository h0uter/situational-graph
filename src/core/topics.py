from enum import Enum


class Topics(Enum):
    RUN_PLATFORM = "run platform"

    OPERATOR_TASK = "operator task"

    VIEW__SHORTCUT_CHECKING = "shortcut checking data"
    VIEW__FRONTIER_SAMPLING = "frontier sampling data"
    #
    VIEW__MISSION_UPDATE = "mission view update"
    VIEW__MISSION_UPDATE_FINAL = "mission view update final"
    VIEW__MISSION_START_POINT = "mission view start point"

    LOG__TASK_UTILITIES = "task utilities"
