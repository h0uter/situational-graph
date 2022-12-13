from src.operator.views.frontier_sampling_view import FrontierSamplingDebugView
from src.operator.views.mission_view import MissionView
from src.operator.views.waypoint_shortcuts_view import WaypointShortcutDebugView
from src.mission.sar.search_and_rescue_usecase import SearchAndRescueUsecase

if __name__ == "__main__":
    # matplotlib.use("Qt5agg")

    """initiliaze view subscribers"""
    MissionView()
    WaypointShortcutDebugView()
    FrontierSamplingDebugView()

    # ImageMapDebugView()

    SearchAndRescueUsecase().run()


    # benchmark_func()
