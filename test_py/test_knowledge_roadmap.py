from src.entities.tosg import TOSG
from src.utils.config import Config


def test_get_node_by_pos():
    krm = TOSG(Config(), [(55, 55)])
    assert 0 == krm.get_node_by_pos((55, 55))
