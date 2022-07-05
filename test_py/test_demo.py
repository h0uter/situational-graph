from src.__main__ import main
from src.utils.config import Config, Scenario, PlotLvl


def test_demo_villa_closed_room_completes():
    cfg = Config(PlotLvl.NONE, Scenario.SIM_VILLA_ROOM)
    assert main(cfg) is True


# def test_demo_villa_completes():
#     cfg = Config(PlotLvl.NONE, Scenario.SIM_VILLA)
#     assert main(cfg) is True


def test_main_maze_completes():
    cfg = Config(PlotLvl.NONE, Scenario.SIM_MAZE)
    assert main(cfg) is True


# def test_main_villa_completes_multi_agent():
#     cfg = Config(PlotLvl.NONE, Scenario.SIM_VILLA, num_agents=10)
#     assert main(cfg) is True
