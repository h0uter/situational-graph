from src.entities.krm import KRM


def test_get_node_by_pos():
    KRM = KRM([(55, 55)])
    assert 0 == KRM.get_node_by_pos((55, 55))
