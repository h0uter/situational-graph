from src.entities.static_data.behaviors import Behaviors
from src.entities.static_data.objectives import Objectives
from src.entities.static_data.object_types import ObjectTypes


Affordance = tuple[ObjectTypes, Behaviors, Objectives]

AFFORDANCES = [
    (ObjectTypes.WAYPOINT, Behaviors.GOTO, None),
    (ObjectTypes.HOTSPOT, Behaviors.VISIT, Objectives.VISIT_ALL_HOTSPOTS),
    (ObjectTypes.FRONTIER, Behaviors.EXPLORE, Objectives.EXPLORE_ALL_FTS),
    (ObjectTypes.DOOR, Behaviors.OPEN_DOOR, Objectives.OPEN_ALL_DOORS),
]
