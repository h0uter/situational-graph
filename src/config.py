import logging
import math
import os
import sys
from enum import Enum, IntEnum, auto

import coloredlogs

"""User Configuration can be selected at the bottom of this file"""


class Scenario(Enum):
    SIM_VILLA = auto()
    SIM_VILLA_ROOM = auto()
    SIM_MAZE = auto()
    SIM_MAZE_MEDIUM = auto()
    REAL = auto()


class PlotLvl(IntEnum):
    ALL = auto()
    INTERMEDIATE_ONLY = auto()
    RESULT_ONLY = auto()
    STATS_ONLY = auto()
    NONE = auto()


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
        max_steps: float = math.inf,
        audio_feedback: bool = False,
        screenshot: bool = False,
        screenshot_folder_name: str = "test",
    ):
        self.MAX_STEPS = max_steps
        self.PLOT_LVL = plot_lvl
        self.SCENARIO = scenario
        self.VIZUALISER = vizualiser

        self.AUDIO_FEEDBACK = audio_feedback
        self.SCREENSHOT = screenshot
        self.SCREENSHOT_FOLDER_NAME = screenshot_folder_name

        # self.PRUNE_RADIUS_FACTOR = 0.20  # too low (<0.20) and we get dense graph, too high (>0.25) and corners are pruned from inside rooms
        self.PRUNE_RADIUS_FACTOR = 0.18  # too low and we get dense graph, too high and corners are pruned from inside rooms
        self.SAMPLE_RING_WIDTH = 1.0  # 0 - 1.0
        self.SAMPLE_RADIUS_FACTOR = 0.6
        self.WP_SHORTCUT_FACTOR = 0.75

        # instead of doing it like this, how could I compose this behavour?
        if (
            self.SCENARIO == Scenario.SIM_VILLA
            or self.SCENARIO == Scenario.SIM_VILLA_ROOM
        ):
            self.set_sim_villa_params()

        elif self.SCENARIO == Scenario.SIM_MAZE:
            self.set_sim_maze_params()

        elif self.SCENARIO == Scenario.SIM_MAZE_MEDIUM:
            self.set_sim_maze_medium_params()

        elif self.SCENARIO == Scenario.REAL:
            self.set_real_params()

        self.LG_LEN_IN_M = self.LG_NUM_CELLS * self.LG_MTR_PER_CELL

        # exploration hyperparameters
        # self.PATH_FINDING_METHOD = "bellman-ford"
        self.PATH_FINDING_METHOD = "dijkstra"
        self.N_SAMPLES = 30
        self.PRUNE_RADIUS = self.LG_LEN_IN_M * self.PRUNE_RADIUS_FACTOR
        self.AT_WP_MARGIN = 0.25
        # self.PREV_POS_MARGIN = 0.15
        self.PREV_POS_MARGIN = 0.35
        self.ARRIVAL_MARGIN = 0.5
        self.WP_SHORTCUT_MARGIN = (self.LG_LEN_IN_M / 2) * self.WP_SHORTCUT_FACTOR

        # SIM PARAMS
        self.NUM_AGENTS = num_agents

        # logging
        # LOG_LVL = logging.DEBUG
        LOG_LVL = logging.INFO
        logging.basicConfig(stream=sys.stdout, level=LOG_LVL)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("bosdyn").setLevel(logging.WARNING)
        mylogs = logging.getLogger(__name__)
        coloredlogs.install(level=LOG_LVL, logger=mylogs)

        # LOGIN
        self.LOGIN_PATH = os.path.join("src", "platform_autonomy", "real")

    def set_real_params(self):
        self.LG_NUM_CELLS = 128
        self.LG_MTR_PER_CELL = 0.03
        self.MAP_PATH = ""
        self.AGENT_START_POS = (0, 0)

        self.AUDIO_FEEDBACK = True

        self.PRUNE_RADIUS_FACTOR = 0.25  # really dont want a dense graph
        # self.PRUNE_RADIUS_FACTOR = 0.23
        # self.SAMPLE_RING_WIDTH = 0.5
        self.SAMPLE_RING_WIDTH = 0.7
        self.SAMPLE_RADIUS_FACTOR = (
            0.9  # this cannot be 1 for Angular sampling strategy
        )
        self.WP_SHORTCUT_FACTOR = 1.0
        self.AT_WP_MARGIN = (
            # 0.35  # hopefully this makes it more robust on real spot in doorways
            0.4  # hopefully this makes it more robust on real spot in doorways
        )

        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = math.floor(
            (self.LG_NUM_CELLS // 2) * self.SAMPLE_RADIUS_FACTOR
        )

    def set_sim_villa_params(self):

        self.PRUNE_RADIUS_FACTOR = 0.18  # too low and we get dense graph, too high and corners are pruned from inside rooms
        self.SAMPLE_RING_WIDTH = 1.0  # 0 - 1.0
        self.SAMPLE_RADIUS_FACTOR = 0.6

        self.MAP_PATH = os.path.join("resource", "villa_holes_closed.png")
        self.MAP_PATH2 = os.path.join("resource", "villa_holes_closed_open_wall.png")
        self.MAP_PATH_TASK_SWITCH = os.path.join(
            "resource", "villa_holes_closed_task_switch.png"
        )
        self.TOT_MAP_LEN_M_X = 50
        self.IMG_TOTAL_X_PIX = 2026
        self.IMG_TOTAL_Y_PIX = 1686
        self.LG_NUM_CELLS = 420  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = math.floor(
            (self.LG_NUM_CELLS // 2) * self.SAMPLE_RADIUS_FACTOR
        )

        """startpositions for the agent"""
        # self.AGENT_START_POS = (-9, 13)  # top left second room
        # self.AGENT_START_POS = (-14, 13)  # top left first room
        self.AGENT_START_POS = (4, 0)

        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_MTR_PER_CELL = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        if self.SCENARIO == Scenario.SIM_VILLA_ROOM:
            self.AGENT_START_POS = (13, 14)

    def set_sim_maze_params(self):
        self.MAP_PATH = os.path.join("resource", "simple_maze2_border_closed.png")
        self.TOT_MAP_LEN_M_X = 50
        self.IMG_TOTAL_X_PIX = 2000
        self.IMG_TOTAL_Y_PIX = 1000
        self.LG_NUM_CELLS = 420  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = math.floor(
            (self.LG_NUM_CELLS // 2) * self.SAMPLE_RADIUS_FACTOR
        )

        self.AGENT_START_POS = (-2, 0)
        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_MTR_PER_CELL = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX

    def set_sim_maze_medium_params(self):
        self.MAP_PATH = os.path.join("resource", "medium_maze.png")
        self.TOT_MAP_LEN_M_X = 73
        self.IMG_TOTAL_X_PIX = 1920
        self.IMG_TOTAL_Y_PIX = 1920
        self.LG_NUM_CELLS = 200  # max:420 due to img border margins
        self.FRONTIER_SAMPLE_RADIUS_NUM_CELLS = math.floor(
            (self.LG_NUM_CELLS // 2) * self.SAMPLE_RADIUS_FACTOR
        )

        # self.AGENT_START_POS = (-3, 0)
        self.AGENT_START_POS = (-30, -30)
        self.TOT_MAP_LEN_M_Y = (
            self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX
        ) * self.IMG_TOTAL_Y_PIX
        self.TOTAL_MAP_LEN_M = (self.TOT_MAP_LEN_M_X, self.TOT_MAP_LEN_M_Y)
        self.LG_MTR_PER_CELL = self.TOT_MAP_LEN_M_X / self.IMG_TOTAL_X_PIX


"""Set configuration here"""
cfg = Config()
# cfg = Config(max_steps=10)
# cfg = Config(scenario=Scenario.SIM_VILLA_ROOM)
# cfg = Config(num_agents=5, scenario=Scenario.SIM_MAZE_MEDIUM)
cfg = Config(num_agents=2)
# cfg = Config(num_agents=10, scenario=Scenario.SIM_MAZE_MEDIUM)
# cfg = Config(plot_lvl=PlotLvl.NONE)
# cfg = Config(scenario=Scenario.SIM_VILLA_ROOM, plot_lvl=PlotLvl.RESULT_ONLY)
# cfg = Config(scenario=Scenario.SIM_MAZE)
# cfg = Config(scenario=Scenario.SIM_VILLA, vizualiser=Vizualiser.MATPLOTLIB)
# cfg = Config(plot_lvl=PlotLvl.RESULT_ONLY, scenario=Scenario.SIM_MAZE_MEDIUM)

# cfg = Config(scenario=Scenario.REAL, vizualiser=Vizualiser.MATPLOTLIB)
# cfg = Config(scenario=Scenario.REAL, screenshot=True, screenshot_folder_name="vonweiler2")
# cfg = Config(screenshot=True, screenshot_folder_name="vonweiler2")
# cfg = Config(scenario=Scenario.REAL)

# cfg = Config(PlotLvl.NONE, World.SIM_MAZE, num_agents=10)
# cfg = Config(scenario=Scenario.SIM_VILLA, num_agents=10)
# cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM)
# cfg = Config(scenario=Scenario.SIM_MAZE_MEDIUM, vizualiser=Vizualiser.MATPLOTLIB)
# cfg = Config(vizualiser=Vizualiser.MATPLOTLIB)

# '''benchmark'''
# cfg = Config(
#     # plot_lvl=PlotLvl.NONE,
#     plot_lvl=PlotLvl.ALL,
#     num_agents=10,
#     # num_agents=2,
#     scenario=Scenario.SIM_MAZE_MEDIUM,
#     # max_steps=400,
# )
