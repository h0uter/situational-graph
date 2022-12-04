# OBSERVER PATTERN

from dataclasses import dataclass
from typing import Sequence

from src.config import PlotLvl, Vizualiser, cfg
from src.shared.node_and_edge import Edge
from src.usecases.operator.local_grid_view import LocalGridView
from src.usecases.operator.mission_view import MissionView
from src.usecases.operator.mpl_vizualisation import MplVizualisation
from src.usecases.shared.behaviors.actions.find_shortcuts_between_wps_on_lg import (
    WaypointShortcutViewModel,
)
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
            self.mission_view = MplVizualisation()
        else:
            self.mission_view = MissionView()

        self.local_grid_view = LocalGridView()

    # BUG: multi agents all post their lg events and overwrite eachother
    # result is that you always see the lg of the last agent
    def handle_new_lg_event(self, lg):
        self.lg = lg

    def handle_figure_update_event(self, data):
        if cfg.PLOT_LVL == PlotLvl.ALL or cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            krm = data["krm"]
            agents = data["agents"]
            usecases = data["usecases"]
            self.mission_view.figure_update(krm, agents, self.lg, usecases)

    def handle_figure_final_result_event(self, data):
        if cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or cfg.PLOT_LVL == PlotLvl.ALL:
            krm = data["krm"]
            agents = data["agents"]
            usecases = data["usecases"]
            self.mission_view.figure_final_result(krm, agents, self.lg, usecases)

    def viz_point(self, data):
        self.mission_view.viz_start_point((data[0], data[1]))

    def handle_shortcut_checking_data(self, data: WaypointShortcutViewModel):
        self.local_grid_view.viz_waypoint_shortcuts(
            self.lg, data.collision_cells, data.shortcut_candidate_cells
        )

    def handle_frontier_sampling_data(self, data: Sequence[tuple[int, int]]):
        self.local_grid_view.viz_frontier_sampling(self.lg, data)

    def setup_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)
        subscribe("figure final result", self.handle_figure_final_result_event)
        subscribe("viz point", self.viz_point)

        subscribe("shortcut checking data", self.handle_shortcut_checking_data)
        subscribe("new_frontier_cells", self.handle_frontier_sampling_data)
