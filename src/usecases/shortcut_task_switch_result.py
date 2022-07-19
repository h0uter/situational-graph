from src.domain.entities.object_types import ObjectTypes
from src.domain.services.tosg import TOSG
from src.usecases.sar.sar_affordances import SAR_AFFORDANCES


def setup_tosg_for_task_switch_result(tosg: TOSG):
    X1 = 6.5
    X2 = 12

    NODE_POSITIONS = [
        (X1, -13),
        (X1, -9),
        (X1, -5),
        (X1, -1),

        (X2, -1),
        (X2, -5),
        (X2, -9),
        (X2, -13),
    ]

    def node_adder(node_positions: list[tuple[float, float]]):
        node_list = []
        for node_position in node_positions:
            new_node = tosg.add_waypoint_node(node_position)
            node_list.append(new_node)
        return node_list

    node_list = node_adder(NODE_POSITIONS)

    for i, node in enumerate(node_list):
        if i == 0:
            continue
        else:
            tosg.add_waypoint_diedge(node_list[i - 1], node_list[i])

    new_task_pos = (X1, 3)
    tosg.add_node_with_task_and_edges_from_affordances(
        # node_list[3], ObjectTypes.FRONTIER, new_task_pos, SAR_AFFORDANCES
        node_list[3], ObjectTypes.UNKNOWN_VICTIM, new_task_pos, SAR_AFFORDANCES
    )
