# OBSERVER PATTERN

from typing import Sequence

from src.config import PlotLvl, cfg
from src.usecases.operator.local_grid_view import LocalGridView
from src.usecases.operator.mission_view import MissionView
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import \
    WaypointShortcutViewModel
from src.usecases.shared.behaviors.explore_behavior import FrontierSamplingViewModel
from src.usecases.utils.feedback import MissionViewModel
from src.utils.event import subscribe


class ViewListener:
    def __init__(self):
        self.mission_view = MissionView()
        self.local_grid_view = LocalGridView()

    # # BUG: multi agents all post their lg events and overwrite eachother
    # # result is that you always see the lg of the last agent
    def handle_new_lg_event(self, lg):
        self.lg = lg

    def handle_figure_update_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            self.mission_view.figure_update(data.situational_graph, data.agents, self.lg, data.usecases)

    def handle_figure_final_result_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
            self.mission_view.figure_final_result(data.situational_graph, data.agents, self.lg, data.usecases)

    def viz_point(self, data):
        self.mission_view.viz_start_point((data[0], data[1]))

    def handle_shortcut_checking_data(self, data: WaypointShortcutViewModel):
        self.local_grid_view.viz_waypoint_shortcuts(
            data.local_grid, data.collision_cells, data.shortcut_candidate_cells
        )

    def handle_frontier_sampling_data(self, data: FrontierSamplingViewModel):
        self.local_grid_view.viz_frontier_sampling(data.local_grid_img, data.new_frontier_cells)

    def setup_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)
        subscribe("figure final result", self.handle_figure_final_result_event)
        subscribe("viz point", self.viz_point)

        subscribe("shortcut checking data", self.handle_shortcut_checking_data)
        subscribe("new_frontier_cells", self.handle_frontier_sampling_data)


