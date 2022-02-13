import uuid

import networkx as nx


class KnowledgeRoadmap:
    """
    An agent implements a Knowledge Roadmap to keep track of the
    world beliefs which are relevant for navigating during his mission.
    A KRM is a graph with 3 distinct node and corresponding edge types.
    - Waypoint Nodes:: correspond to places the robot has been and can go to.
    - Frontier Nodes:: correspond to places the robot has not been but expects it can go to.
    - World Object Nodes:: correspond to actionable items the robot has seen.
    """

    # TODO: adress local vs global KRM
    def __init__(self, start_pos: tuple) -> None:
        self.graph = nx.Graph()  # Knowledge Road Map

        self.graph.add_node(0, pos=start_pos, type="waypoint", id=uuid.uuid4())
        self.next_wp_idx = 1
        self.next_frontier_idx = 1000
        self.next_wo_idx = 200

    def add_waypoint(self, pos: tuple, prev_wp) -> None:
        """ adds new waypoints and increments wp the idx"""
        self.graph.add_node(self.next_wp_idx, pos=pos, type="waypoint", id=uuid.uuid4())
        self.graph.add_edge(
            self.next_wp_idx, prev_wp, type="waypoint_edge", id=uuid.uuid4()
        )
        self.next_wp_idx += 1

    def add_world_object(self, pos: tuple, label: str) -> None:
        """ adds a world object to the graph"""
        self.graph.add_node(label, pos=pos, type="world_object", id=uuid.uuid4())
        self.graph.add_edge(
            self.next_wp_idx - 1, label, type="world_object_edge", id=uuid.uuid4()
        )

    # TODO: remove the agent_at_wp parameter requirement
    def add_frontier(self, pos: tuple, agent_at_wp: int) -> None:
        """ adds a frontier to the graph"""
        self.graph.add_node(
            self.next_frontier_idx, pos=pos, type="frontier", id=uuid.uuid4()
        )
        self.graph.add_edge(
            agent_at_wp, self.next_frontier_idx, type="frontier_edge", id=uuid.uuid4()
        )
        self.next_frontier_idx += 1

    def remove_frontier(self, target_frontier_idx) -> None:
        """ removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_idx(target_frontier_idx)
        if target_frontier["type"] == "frontier":
            self.graph.remove_node(target_frontier_idx)

    def get_node_by_pos(self, pos: tuple):
        """ returns the node idx at the given position """
        for node in self.graph.nodes():
            if self.graph.nodes[node]["pos"] == pos:
                return node

    def get_node_by_UUID(self, UUID):
        """ returns the node idx with the given UUID """
        for node in self.graph.nodes():
            if self.graph.nodes[node]["id"] == UUID:
                return node

    def get_node_data_by_idx(self, idx: int) -> dict:
        """ returns the node corresponding to the given index """
        return self.graph.nodes[idx]

    def get_all_waypoints(self) -> list:
        """ returns all waypoints in the graph"""
        return [
            self.graph.nodes[node]
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == "waypoint"
        ]

    def get_all_waypoint_idxs(self) -> list:
        """ returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == "waypoint"
        ]

    def get_all_frontiers_idxs(self) -> list:
        """ returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == "frontier"
        ]

    def get_nodes_of_type_in_margin(
        self, pos: tuple, margin: float, node_type: str
    ) -> list:
        """
        Given a position, a margin and a node type, return a list of nodes of that type that are within the margin of the position.

        :param pos: the position of the agent
        :param margin: the margin of the square to look
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        """
        close_nodes = []
        for node in self.graph.nodes:
            data = self.get_node_data_by_idx(node)
            if data["type"] == node_type:
                node_pos = data["pos"]
                if (
                    abs(pos[0] - node_pos[0]) < margin
                    and abs(pos[1] - node_pos[1]) < margin
                ):
                    close_nodes.append(node)

        # if len(close_nodes) == 0:
        #     return []
        return close_nodes
