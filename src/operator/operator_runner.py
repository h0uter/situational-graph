from src.operator.views.frontier_sampling_view import FrontierSamplingDebugView
from src.operator.views.mission_view import MissionView
from src.operator.views.waypoint_shortcuts_view import WaypointShortcutDebugView


def run():
    """initiliaze view subscribers"""
    MissionView()
    WaypointShortcutDebugView()
    FrontierSamplingDebugView()
