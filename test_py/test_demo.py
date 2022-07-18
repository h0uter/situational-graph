from src.__main__ import run_sar_usecase
from src.configuration.config import Config, Scenario, PlotLvl


def test_demo_villa_closed_room_completes():
    cfg = Config(PlotLvl.NONE, Scenario.SIM_VILLA_ROOM)
    assert run_sar_usecase(cfg) is True


def test_main_maze_completes():
    cfg = Config(PlotLvl.NONE, Scenario.SIM_MAZE)
    assert run_sar_usecase(cfg) is True
