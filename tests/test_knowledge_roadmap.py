from src.shared.situational_graph import SituationalGraph


def test_get_node_by_pos():
    krm = SituationalGraph()
    node = krm.add_waypoint_node((55, 55))
    assert node == krm.get_node_by_pos((55, 55))
