from src.domain.services.tosg import TOSG


def setup_tosg_for_task_switch_result(tosg: TOSG):

    node_positions = [
        (0, 0),
        (0, 2),
        (0, 4),
        (0, 6),
    ]

    def node_adder(node_positions: list[tuple[float, float]]):
        node_list = []
        for node_position in node_positions:
            new_node = tosg.add_waypoint_node(node_position)
            node_list.append(new_node)
        return node_list

    node_list = node_adder(node_positions)
    print(node_list)

    for i, node in enumerate(node_list):
        print(i)
        if i == 0:
            continue
        else:
            tosg.add_waypoint_diedge(node_list[i - 1], node_list[i])
