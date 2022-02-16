import logging
import os
import sys
from enum import Enum, auto

import coloredlogs


class World(Enum):
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
    def __init__(self, plot_lvl: PlotLvl = PlotLvl.ALL, world: World = World.SIM_VILLA, vizualiser: Vizualiser = Vizualiser.VEDO):
        self.PLOT_LVL = plot_lvl
        self.WORLD = world
        self.VIZUALISER = vizualiser

        self.PRUNE_RADIUS_FACTOR = 0.25

        if self.WORLD == World.SIM_VILLA or self.WORLD == World.SIM_VILLA_ROOM:
            self.FULL_PATH = os.path.join("resource", "villa_holes_closed.png")
            self.TOT_MAP_LEN_M_X = 50
            self.IMG_TOTAL_X_PIX = 2026
            self.IMG_TOTAL_Y_PIX = 1686
            self.LG_NUM_CELLS = 420  # max:400 due to img border margins
            self.AGENT_START_POS = (-9, 13)
            self.TOT_MAP_LEN_M_Y = (
                self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
            ) * self.IMG_TOTAL_Y_PIX
            self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
            self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
            if self.WORLD == World.SIM_VILLA_ROOM:
                self.AGENT_START_POS = (13, 14)

        elif self.WORLD == World.SIM_MAZE:
            self.FULL_PATH = os.path.join("resource", "simple_maze2_border_closed.png")
            self.TOT_MAP_LEN_M_X = 50
            self.IMG_TOTAL_X_PIX = 2000
            self.IMG_TOTAL_Y_PIX = 1000
            self.LG_NUM_CELLS = 420  # max:400 due to img border margins
            self.AGENT_START_POS = (-2, 0)
            self.TOT_MAP_LEN_M_Y = (
                self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
            ) * self.IMG_TOTAL_Y_PIX
            self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
            self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX

        elif self.WORLD == World.SIM_MAZE_MEDIUM:
            self.FULL_PATH = os.path.join("resource", "medium_maze.png")
            self.TOT_MAP_LEN_M_X = 73
            self.IMG_TOTAL_X_PIX = 1920
            self.IMG_TOTAL_Y_PIX = 1920
            self.LG_NUM_CELLS = 200  # max:400 due to img border margins
            self.AGENT_START_POS = (-3, 0)
            self.TOT_MAP_LEN_M_Y = (
                self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
            ) * self.IMG_TOTAL_Y_PIX
            self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
            self.LG_CELL_SIZE_M = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX

        elif self.WORLD == World.REAL:
            self.LG_NUM_CELLS = 128  # max:400 due to img border margins
            self.LG_CELL_SIZE_M = 0.03
            self.FULL_PATH = ""
            self.PRUNE_RADIUS_FACTOR = 0.15

        self.LG_LENGTH_IN_M = self.LG_NUM_CELLS * self.LG_CELL_SIZE_M

        # exploration hyperparameters
        self.N_SAMPLES = 25
        self.PRUNE_RADIUS = self.LG_LENGTH_IN_M * self.PRUNE_RADIUS_FACTOR
        # self.SAMPLE_RING_WIDTH = 0.7
        self.SAMPLE_RING_WIDTH = 0.9
        # FIXME: the minus is for spot only
        # self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2 - 20
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS // 2
        self.AT_WP_MARGIN = 0.25
        self.PREV_POS_MARGIN = 0.15

        # logging
        # LOG_LVL = logging.DEBUG
        LOG_LVL = logging.INFO
        logging.basicConfig(stream=sys.stdout, level=LOG_LVL)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("bosdyn").setLevel(logging.WARNING)
        mylogs = logging.getLogger(__name__)
        coloredlogs.install(level=LOG_LVL, logger=mylogs)
