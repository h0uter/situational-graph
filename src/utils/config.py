import logging
import os
import sys
from enum import Enum, auto

import coloredlogs


class Scenario(Enum):
    SIM_VILLA = auto()
    SIM_VILLA_ROOM = auto()
    SIM_MAZE = auto()
    SIM_MAZE_MEDIUM = auto()
    REAL = auto()


class PlotLvl(Enum):
    NONE = auto()
    ALL = auto()
    INTERMEDIATE_ONLY = auto()
    RESULT_ONLY = auto()


class Vizualiser(Enum):
    MATPLOTLIB = auto()
    VEDO = auto()


class Config:
    def __init__(
        self,
        plot_lvl: PlotLvl = PlotLvl.ALL,
        scenario: Scenario = Scenario.SIM_VILLA,
        vizualiser: Vizualiser = Vizualiser.VEDO,
        num_agents: int = 1,
    ):
        self.PLOT_LVL = plot_lvl
        self.SCENARIO = scenario
        self.VIZUALISER = vizualiser

        self.PRUNE_RADIUS_FACTOR = 0.20  # too low and we get dense graph, too high and corners are pruned from inside rooms
        self.SAMPLE_RING_WIDTH = 1.0  # 0 - 1.0

        # instead of doing it like this, how could I compose this behavour?
        if self.SCENARIO == Scenario.SIM_VILLA or self.SCENARIO == Scenario.SIM_VILLA_ROOM:
            self.set_sim_villa_params()

        elif self.SCENARIO == Scenario.SIM_MAZE:
            self.set_sim_maze_params()

        elif self.SCENARIO == Scenario.SIM_MAZE_MEDIUM:
            self.set_sim_maze_medium_params()

        elif self.SCENARIO == Scenario.REAL:
            self.set_real_params()

        self.LG_LENGTH_IN_M = self.LG_NUM_CELLS * self.LG_CELL_SIZE_M

        # exploration hyperparameters
        self.PATH_FINDING_METHOD = "bellman-ford"
        # self.PATH_FINDING_METHOD = "dijkstra"
        self.N_SAMPLES = 25
        self.PRUNE_RADIUS = self.LG_LENGTH_IN_M * self.PRUNE_RADIUS_FACTOR
        self.AT_WP_MARGIN = 0.25
        self.PREV_POS_MARGIN = 0.15
        self.ARRIVAL_MARGIN = 0.5
        self.WP_SHORTCUT_MARGIN = (self.LG_LENGTH_IN_M / 2) * 0.65

        # SIM PARAMS
        self.NUM_AGENTS = num_agents

        # logging
        LOG_LVL = logging.DEBUG
        # LOG_LVL = logging.INFO
        logging.basicConfig(stream=sys.stdout, level=LOG_LVL)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("bosdyn").setLevel(logging.WARNING)
        mylogs = logging.getLogger(__name__)
        coloredlogs.install(level=LOG_LVL, logger=mylogs)

    def set_real_params(self):
        self.LG_NUM_CELLS = 128
        self.LG_CELL_SIZE_M = 0.03
        self.FULL_PATH = ""
        # self.PRUNE_RADIUS_FACTOR = 0.15
        self.PRUNE_RADIUS_FACTOR = 0.25
        self.SAMPLE_RING_WIDTH = 0.3
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2

    def set_sim_villa_params(self):
        self.FULL_PATH = os.path.join("resource", "villa_holes_closed.png")
        self.TOT_MAP_LEN_M_X = 50
        self.IMG_TOTAL_X_PIX = 2026
        self.IMG_TOTAL_Y_PIX = 1686
        self.LG_NUM_CELLS = 420  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2

        self.AGENT_START_POS = (-9, 13)
        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        if self.SCENARIO == Scenario.SIM_VILLA_ROOM:
            self.AGENT_START_POS = (13, 14)

    def set_sim_maze_params(self):
        self.FULL_PATH = os.path.join("resource", "simple_maze2_border_closed.png")
        self.TOT_MAP_LEN_M_X = 50
        self.IMG_TOTAL_X_PIX = 2000
        self.IMG_TOTAL_Y_PIX = 1000
        self.LG_NUM_CELLS = 420  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2

        self.AGENT_START_POS = (-2, 0)
        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX

    def set_sim_maze_medium_params(self):
        self.FULL_PATH = os.path.join("resource", "medium_maze.png")
        self.TOT_MAP_LEN_M_X = 73
        self.IMG_TOTAL_X_PIX = 1920
        self.IMG_TOTAL_Y_PIX = 1920
        self.LG_NUM_CELLS = 200  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2

        self.AGENT_START_POS = (-3, 0)
        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
