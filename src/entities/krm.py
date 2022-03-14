import math
import uuid

import networkx as nx
import logging

from src.utils.my_types import EdgeType, Node, NodeType
from src.utils.config import Config


class KRM:
    """
    An agent implements a Knowledge Roadmap to keep track of the
    world beliefs which are relevant executing its mission.
    A KRM is a graph with 3 distinct node and corresponding edge types.
    - Waypoint Nodes:: correspond to places the robot has been and can go to.
    - Frontier Nodes:: correspond to places the robot has not been but expects it can go to.
    - World Object Nodes:: correspond to actionable items the robot has seen.
    """

    # TODO: adress local vs global KRM
    def __init__(self, cfg: Config, start_poses: list[tuple]) -> None:
        self._log = logging.getLogger(__name__)

        self.graph = nx.DiGraph()  # Knowledge Road Map
        self.cfg = cfg
        self.next_wp_idx = 0

        # This is ugly
        self.duplicate_start_poses = []
        for start_pos in start_poses:
            if start_pos not in self.duplicate_start_poses:
                self.add_start_waypoints(start_pos)
                self.duplicate_start_poses.append(start_pos)
        self.next_frontier_idx = 9000
        self.next_wo_idx = 90000

        self.path_len_dict = dict()
        self.prev_source_set = set()

    # add startpoints function
    def add_start_waypoints(self, pos: tuple) -> None:
        """ adds start points to the graph"""
        self.graph.add_node(
            self.next_wp_idx, pos=pos, type=NodeType.WAYPOINT, id=uuid.uuid4()
        )
        self.next_wp_idx += 1

    def calc_edge_len(self, node_a, node_b):
        """ calculates the distance between two nodes"""
        return math.sqrt(
            (self.graph.nodes[node_a]["pos"][0] - self.graph.nodes[node_b]["pos"][0])
            ** 2
            + (self.graph.nodes[node_a]["pos"][1] - self.graph.nodes[node_b]["pos"][1])
            ** 2
        )

    def add_waypoint(self, pos: tuple, prev_wp) -> None:
        """ adds new waypoints and increments wp the idx"""
        self.graph.add_node(
            self.next_wp_idx, pos=pos, type=NodeType.WAYPOINT, id=uuid.uuid4()
        )
        self.add_waypoint_diedge(self.next_wp_idx, prev_wp)
        self.next_wp_idx += 1

    def add_waypoint_diedge(self, node_a, node_b) -> None:
        """ adds a waypoint edge in both direction to the graph"""
        d = {
            "type": EdgeType.WAYPOINT_EDGE,
            "cost": self.calc_edge_len(node_a, node_b),
        }
        self.graph.add_edges_from([(node_a, node_b, d), (node_b, node_a, d)])

    def add_world_object(self, pos: tuple, label: str) -> None:
        """ adds a world object to the graph"""
        self.graph.add_node(label, pos=pos, type=NodeType.WORLD_OBJECT, id=uuid.uuid4())
        # HACK: instead of adding infite cost toworld object edges, use a subgraph for specific planning problems
        self.graph.add_edge(
            self.next_wp_idx - 1,
            label,
            type=EdgeType.WORLD_OBJECT_EDGE,
            # id=uuid.uuid4(),
            cost=-100,
        )

    # TODO: remove the agent_at_wp parameter requirement
    def add_frontier(self, pos: tuple, agent_at_wp: Node) -> None:
        """ adds a frontier to the graph"""
        self.graph.add_node(
            self.next_frontier_idx, pos=pos, type=NodeType.FRONTIER, id=uuid.uuid4()
        )

        edge_len = self.calc_edge_len(agent_at_wp, self.next_frontier_idx)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the longest waypoints
        else:
            cost = edge_len

        self.graph.add_edge(
            agent_at_wp,
            self.next_frontier_idx,
            type=EdgeType.FRONTIER_EDGE,
            # id=uuid.uuid4(),
            cost=cost,
        )

        self.next_frontier_idx += 1

    def remove_frontier(self, target_frontier_idx) -> None:
        """ removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(target_frontier_idx)
        if target_frontier["type"] == NodeType.FRONTIER:
            self.graph.remove_node(target_frontier_idx)  # also removes the edge

    # TODO: this should be invalidate, so that we change its alpha or smth
    def remove_world_object(self, idx) -> None:
        """ removes a frontier from the graph"""
        removal_target = self.get_node_data_by_node(idx)
        if removal_target["type"] == NodeType.WORLD_OBJECT:
            self.graph.remove_node(idx)  # also removes the edge

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

    def get_node_data_by_node(self, node: Node) -> dict:
        """ returns the node corresponding to the given index """
        return self.graph.nodes[node]

    def get_all_waypoints(self) -> list:
        """ returns all waypoints in the graph"""
        return [
            self.graph.nodes[node]
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.WAYPOINT
        ]

    def get_all_waypoint_idxs(self) -> list:
        """ returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.WAYPOINT
        ]

    def get_all_frontiers_idxs(self) -> list:
        """ returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.FRONTIER
        ]

    def get_all_world_object_idxs(self) -> list:
        """ returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.WORLD_OBJECT
        ]

    def get_nodes_of_type_in_margin(
        self, pos: tuple, margin: float, node_type: NodeType
    ) -> list:
        """
        Given a position, a margin and a node type, return a list of nodes of that type that are within the margin of the position.

        :param pos: the position of the agent
        :param margin: the margin of the square to look
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        """
        close_nodes = list()
        for node in self.graph.nodes:
            data = self.get_node_data_by_node(node)
            if data["type"] == node_type:
                node_pos = data["pos"]
                if (
                    abs(pos[0] - node_pos[0]) < margin
                    and abs(pos[1] - node_pos[1]) < margin
                ):
                    close_nodes.append(node)

        return close_nodes

    def check_node_exists(self, node: Node):
        """ checks if the given node exists in the graph"""
        return node in self.graph.nodes

    # def set_frontier_edge_weight(self, node_a: Node, weight: float):
    #     """ sets the weight of the edge between two nodes"""
    #     predecessors = self.graph.predecessors(node_a)
    #     for predecessor in predecessors:
    #         if self.graph.edges[predecessor, node_a]["type"] == EdgeType.FRONTIER_EDGE:
    #             self.graph.edges[predecessor, node_a]["cost"] = weight
    #             print(f"setting edge between {predecessor} and {node_a} to {weight}")

    def shortest_path(self, source: Node, target: Node):

        path = nx.shortest_path(
            self.graph,
            source=source,
            target=target,
            weight="cost",
            method=self.cfg.PATH_FINDING_METHOD,
        )
        if len(path) > 1:
            return path
        else:
            self._log.error(f": No path found from {source} to {target}.")

    def shortest_path_len(self, source: Node, target: Node):

        # TODO: create this dictionary in a smarter way.

        if target in self.path_len_dict.keys() and source in self.prev_source_set:
            return self.path_len_dict[target]
        else:
            self.path_len_dict = nx.shortest_path_length(
                self.graph,
                source=source,
                weight="cost",
                method=self.cfg.PATH_FINDING_METHOD,
            )
            self.prev_source_set.add(source)
            return self.path_len_dict[target]

        # TODO: use the reconstruct path function
        # with an all pairs algorithms that also returns a predecessor dict.

        # TODO: identify what is most expensive
        # - checking the path lengths
        # - finding the paths

        # TODO: track how often these funcs are called in a single run.

        #     path_len = nx.shortest_path_length(
        #         self.graph,
        #         source=source,
        #         target=target,
        #         weight="cost",
        #         method=self.cfg.PATH_FINDING_METHOD,
        #     )

        # return path_len