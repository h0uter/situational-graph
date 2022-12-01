# OBSERVER PATTERN

from dataclasses import dataclass

from src.config import PlotLvl, Vizualiser, cfg
from src.shared.node_and_edge import Edge
from src.usecases.operator.mission_vizualisation import MissionVisualisation
from src.usecases.operator.mpl_vizualisation import MplVizualisation
from src.utils.event import subscribe

# this class should build a view model


@dataclass
class SituationalGraphViewModel:
    nodes: list
    edges: list


@dataclass
class PlanViewModel:
    plan: list[Edge]


@dataclass
class PlatformViewModel:
    pos: tuple
    heading: float


@dataclass
class ExplorationViewModel:
    local_grid_img: list
    lines: list
    collision_points: list
    frontiers: list
    waypoints: list


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
        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
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

    def handle_shortcut_checking_data(self, data):
        # print(data["collision_points"])
        self.viz.viz_local_grid(self.lg, data["collision_points"], data["shortcut_candidate_cells"])

    def setup_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)
        subscribe("figure final result", self.handle_figure_final_result_event)
        subscribe("viz point", self.viz_point)

        subscribe("shortcut checking data", self.handle_shortcut_checking_data)
