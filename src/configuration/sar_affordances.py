from src.domain import ObjectTypes, Behaviors, Objectives

SAR_AFFORDANCES = [
    (ObjectTypes.WAYPOINT, Behaviors.GOTO, None),
    (ObjectTypes.HOTSPOT, Behaviors.VISIT, Objectives.VISIT_ALL_HOTSPOTS),
    (ObjectTypes.FRONTIER, Behaviors.EXPLORE, Objectives.EXPLORE_ALL_FTS),
    (ObjectTypes.DOOR, Behaviors.OPEN_DOOR, Objectives.OPEN_ALL_DOORS),
]
