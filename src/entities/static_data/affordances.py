from src.entities.static_data.objective import Objective
from src.utils.my_types import Behavior, ObjectType


Affordance = tuple[ObjectType, Behavior, Objective]

AFFORDANCES = [
    (ObjectType.WAYPOINT, Behavior.GOTO, None),
    (ObjectType.HOTSPOT, Behavior.VISIT, Objective.VISIT_ALL_HOTSPOTS),
    (ObjectType.FRONTIER, Behavior.EXPLORE, Objective.EXPLORE_ALL_FTS),
    (ObjectType.DOOR, Behavior.OPEN_DOOR, Objective.OPEN_ALL_DOORS),
]
