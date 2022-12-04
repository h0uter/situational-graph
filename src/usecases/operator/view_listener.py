# OBSERVER PATTERN

from src.config import PlotLvl, cfg
from src.shared.topics import Topics
from src.usecases.operator.local_grid_view import LocalGridView
from src.usecases.operator.mission_view import MissionView
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import \
    WaypointShortcutViewModel
from src.usecases.shared.behaviors.explore_behavior import FrontierSamplingViewModel
from src.usecases.utils.feedback import MissionViewModel
from src.utils.event import subscribe

# deze hele class mag eigenlijk weg, dit kan gewoon in elke view
class ViewListener:
    def __init__(self):
        self.mission_view = MissionView()
        self.local_grid_view = LocalGridView()

        self.setup_event_handler()

    def viz_start_point(self, data):
        self.mission_view.viz_start_point((data[0], data[1]))

    def handle_figure_update_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            self.mission_view.figure_update(data.situational_graph, data.agents, data.usecases)

    def handle_figure_final_result_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
            self.mission_view.figure_final_result(data.situational_graph, data.agents,data.usecases)


    def handle_shortcut_checking_data(self, data: WaypointShortcutViewModel):
        self.local_grid_view.viz_waypoint_shortcuts(
            data.local_grid, data.collision_cells, data.shortcut_candidate_cells
        )

    def handle_frontier_sampling_data(self, data: FrontierSamplingViewModel):
        self.local_grid_view.viz_frontier_sampling(data.local_grid_img, data.new_frontier_cells)

    def setup_event_handler(self):
        subscribe(str(Topics.MISSION_VIEW_START_POINT), self.viz_start_point)

        subscribe(str(Topics.MISSION_VIEW_UPDATE), self.handle_figure_update_event)
        subscribe(str(Topics.MISSION_VIEW_UPDATE_FINAL), self.handle_figure_final_result_event)

        subscribe(str(Topics.SHORTCUT_CHECKING), self.handle_shortcut_checking_data)
        subscribe(str(Topics.FRONTIER_SAMPLING), self.handle_frontier_sampling_data)


