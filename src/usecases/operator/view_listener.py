# OBSERVER PATTERN

from src.config import PlotLvl, cfg
from src.shared.topics import Topics
from src.usecases.operator.mission_view import MissionView
from src.usecases.utils.feedback import MissionViewModel
from src.utils.event import subscribe


# deze hele class mag eigenlijk weg, dit kan gewoon in elke view
class ViewListener:
    def __init__(self):
        self.mission_view = MissionView()

        self.setup_event_handler()

    def viz_start_point(self, data):
        self.mission_view.viz_start_point((data[0], data[1]))

    def handle_figure_update_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            self.mission_view.figure_update(
                data.situational_graph, data.agents, data.usecases
            )

    def handle_figure_final_result_event(self, data: MissionViewModel):
        if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
            self.mission_view.figure_final_result(
                data.situational_graph, data.agents, data.usecases
            )

    def setup_event_handler(self):
        subscribe(str(Topics.MISSION_VIEW_START_POINT), self.viz_start_point)

        subscribe(str(Topics.MISSION_VIEW_UPDATE), self.handle_figure_update_event)
        subscribe(
            str(Topics.MISSION_VIEW_UPDATE_FINAL), self.handle_figure_final_result_event
        )
