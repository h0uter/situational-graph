from src.domain import ObjectTypes, Behaviors, Objectives

SAR_AFFORDANCES = [
    (ObjectTypes.WAYPOINT, Behaviors.GOTO, None),
    (ObjectTypes.FRONTIER, Behaviors.EXPLORE, Objectives.EXPLORE_ALL_FTS),
    (ObjectTypes.UNKNOWN_VICTIM, Behaviors.ASSESS, Objectives.ASSES_ALL_VICTIMS),
    # (ObjectTypes.HOTSPOT, Behaviors.GOTO, Objectives.VISIT_ALL_HOTSPOTS),
    # (ObjectTypes.DOOR, Behaviors.OPEN_DOOR, Objectives.OPEN_ALL_DOORS),
]
