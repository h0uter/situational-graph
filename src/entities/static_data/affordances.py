from src.entities.static_data.behaviors import Behavior
from src.entities.static_data.objective import Objective
from src.entities.static_data.objects import ObjectTypes


Affordance = tuple[ObjectTypes, Behavior, Objective]

AFFORDANCES = [
    (ObjectTypes.WAYPOINT, Behavior.GOTO, None),
    (ObjectTypes.HOTSPOT, Behavior.VISIT, Objective.VISIT_ALL_HOTSPOTS),
    (ObjectTypes.FRONTIER, Behavior.EXPLORE, Objective.EXPLORE_ALL_FTS),
    (ObjectTypes.DOOR, Behavior.OPEN_DOOR, Objective.OPEN_ALL_DOORS),
]
