from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entrypoints.demo import main
from src.utils.config import Config, World, PlotLvl


def test_get_node_by_pos():
    KRM = KnowledgeRoadmap((55, 55))
    assert 0 == KRM.get_node_by_pos((55, 55))


def test_demo_villa_closed_room_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_VILLA_ROOM)
    assert main(cfg) is True


def test_demo_villa_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_VILLA)
    assert main(cfg) is True


def test_main_maze_completes():
    cfg = Config(PlotLvl.NONE, World.SIM_MAZE)
    assert main(cfg) is True
