# OBSERVER PATTERN

from src.config import PlotLvl, Vizualiser, cfg
from src.usecases.operator.mpl_vizualisation import MplVizualisation
from src.usecases.operator.mission_vizualisation import MissionVisualisation
from src.utils.event import subscribe


class VizualisationListener:
    def __init__(self):
        if cfg.VIZUALISER == Vizualiser.MATPLOTLIB:
            self.viz = MplVizualisation()
        else:
            self.viz = MissionVisualisation()

    # BUG: multi agents all post their lg events and overwrite eachother
    # result is that you always see the lg of the last agent
    def handle_new_lg_event(self, lg):
        self.lg = lg

    def handle_figure_update_event(self, data):
        if (
            cfg.PLOT_LVL == PlotLvl.ALL
            or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY
        ):
            krm = data["krm"]
            agents = data["agents"]
            usecases = data["usecases"]
            self.viz.figure_update(krm, agents, self.lg, usecases)

    def handle_figure_final_result_event(self, data):
        if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
            krm = data["krm"]
            agents = data["agents"]
            usecases = data["usecases"]
            self.viz.figure_final_result(krm, agents, self.lg, usecases)

    def viz_point(self, data):
        self.viz.viz_start_point((data[0], data[1]))

    def setup_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)
        subscribe("figure final result", self.handle_figure_final_result_event)
        subscribe("viz point", self.viz_point)
