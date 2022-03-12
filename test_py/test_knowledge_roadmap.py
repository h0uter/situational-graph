from src.entities.krm import KRM
from src.utils.config import Config


def test_get_node_by_pos():
    krm = KRM(Config(), [(55, 55)])
    assert 0 == krm.get_node_by_pos((55, 55))
