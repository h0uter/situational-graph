import os
import logging
import sys
import coloredlogs

from enum import Enum, auto

class Scenario(Enum):
    SIM_VILLA = auto()
    SIM_VILLA_CLOSED_ROOM = auto()
    SIM_MAZE = auto()
    REAL = auto()

class PlotLvl(Enum):
    NONE = auto()
    ALL = auto()
    INTERMEDIATE_ONLY = auto()
    RESULT_ONLY = auto()

class Config:
    def __init__(
            self, 
            plot_lvl: PlotLvl = PlotLvl.ALL, 
            scenario: Scenario = Scenario.SIM_VILLA
        ):
        self.plot_lvl = plot_lvl
        self.scenario = scenario

        if self.scenario == Scenario.SIM_VILLA or self.scenario == Scenario.SIM_VILLA_CLOSED_ROOM:
            self.FULL_PATH = os.path.join("resource", "villa_holes_closed.png")
            self.TOTAL_MAP_LEN_M_X = 50
            self.IMG_TOTAL_X_PIX = 2026
            self.IMG_TOTAL_Y_PIX = 1686
            self.LG_NUM_CELLS = 420  # max:400 due to img border margins
            self.AGENT_START_POS = (-9, 13)
            self.TOTAL_MAP_LEN_M_Y = (
                self.TOTAL_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
                ) * self.IMG_TOTAL_Y_PIX  # zo klopt het met de foto verhoudingen (square cells)
            self.TOTAL_MAP_LEN_M = (self.TOTAL_MAP_LEN_M_X, self.TOTAL_MAP_LEN_M_Y)
            self.LG_CELL_SIZE_M = self.TOTAL_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
            if self.scenario == Scenario.SIM_VILLA_CLOSED_ROOM:
                self.AGENT_START_POS = (13, 14)


        elif self.scenario == Scenario.SIM_MAZE:
            self.FULL_PATH = os.path.join('resource', 'simple_maze2_border_closed.png')
            self.TOTAL_MAP_LEN_M_X = 73
            self.IMG_TOTAL_X_PIX = 2000
            self.IMG_TOTAL_Y_PIX = 1000
            self.LG_NUM_CELLS = 300  # max:400 due to img border margins
            self.AGENT_START_POS = (-2, 0)
            self.TOTAL_MAP_LEN_M_Y = (
            self.TOTAL_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
                ) * self.IMG_TOTAL_Y_PIX  # zo klopt het met de foto verhoudingen (square cells)
            self.TOTAL_MAP_LEN_M = (self.TOTAL_MAP_LEN_M_X, self.TOTAL_MAP_LEN_M_Y)
            self.LG_CELL_SIZE_M = self.TOTAL_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX

        elif self.scenario == Scenario.REAL:
            self.LG_NUM_CELLS = 128  # max:400 due to img border margins
            self.LG_CELL_SIZE_M = 0.03
            self.FULL_PATH = ""

 
        self.LG_LENGTH_IN_M = self.LG_NUM_CELLS * self.LG_CELL_SIZE_M

        # exploration hyperparameters
        self.N_SAMPLES = 25
        self.PRUNE_RADIUS = self.LG_LENGTH_IN_M * 0.25
        self.SAMPLE_RING_WIDTH = 0.9
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = self.LG_NUM_CELLS / 2

        # logging
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        mylogs = logging.getLogger(__name__)
        coloredlogs.install(level=logging.INFO,
                            logger=mylogs)
