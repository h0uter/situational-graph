from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.situational_graph import SituationalGraph


def test_get_node_by_pos():
    krm = SituationalGraph()
    node = krm.add_node_of_type((55, 55), Situations.WAYPOINT)
    assert node == krm.get_node_by_exact_pos((55, 55))
