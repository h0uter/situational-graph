from src.domain import Behaviors, Objectives, Situations

SAR_AFFORDANCES = [
    (Situations.WAYPOINT, Behaviors.GOTO, None),
    (Situations.FRONTIER, Behaviors.EXPLORE, Objectives.EXPLORE_ALL_FTS),
    (Situations.UNKNOWN_VICTIM, Behaviors.ASSESS, Objectives.ASSES_ALL_VICTIMS),
    # (ObjectTypes.MOBILE_VICTIM, Behaviors.GUIDE, Objectives.ASSES_ALL_VICTIMS),
    # (ObjectTypes.HOTSPOT, Behaviors.GOTO, Objectives.VISIT_ALL_HOTSPOTS),
    # (ObjectTypes.DOOR, Behaviors.OPEN_DOOR, Objectives.OPEN_ALL_DOORS),
]
