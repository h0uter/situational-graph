from src.domain.services.tosg import TOSG


def test_get_node_by_pos():
    krm = TOSG()
    node = krm.add_waypoint_node((55, 55))
    assert node == krm.get_node_by_pos((55, 55))
