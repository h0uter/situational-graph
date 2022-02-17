from src.entrypoints.demo import main
from src.utils.config import Config, World, PlotLvl


def test_demo_villa_closed_room_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_VILLA_ROOM)
    assert main(cfg) is True


def test_demo_villa_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_VILLA)
    assert main(cfg) is True


def test_main_maze_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_MAZE)
    assert main(cfg) is True


def test_main_maze_completes_multi_agent():
    cfg = Config(PlotLvl.NONE, World.SIM_VILLA, num_agents=10)
    assert main(cfg) is True
