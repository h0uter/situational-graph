import logging
import math
import uuid
from typing import List, Optional, Sequence

import networkx as nx
from src.entities.dynamic_data.task import Task
from src.entities.static_data.objective import Objective
from src.utils.config import Config
from src.utils.my_types import Behavior, Edge, Node, NodeType


class TOSG:
    # TODO: adress local vs global KRM
    def __init__(self, cfg: Config, start_poses: list[tuple]) -> None:
        self._log = logging.getLogger(__name__)

        # self.graph = nx.DiGraph()  # Knowledge Road Map
        self.graph = nx.MultiDiGraph()  # Knowledge Road Map
        self.cfg = cfg
        self.next_wp_idx = 0

        self.tasks: List[Task] = []

        # This is ugly
        self.duplicate_start_poses = []
        for start_pos in start_poses:
            if start_pos not in self.duplicate_start_poses:
                self.add_start_waypoints(start_pos)
                # HACK:
                self.duplicate_start_poses.append(start_pos)
        self.next_frontier_idx = cfg.FRONTIER_INDEX_START
        self.next_wo_idx = cfg.WORLD_OBJECT_INDEX_START

    def check_if_edge_exists(self, node_a: Node, node_b: Node):
        """checks if an edge between two nodes exists"""
        return self.graph.has_edge(node_a, node_b)

    def check_node_exists(self, node: Node):
        """checks if the given node exists in the graph"""
        return node in self.graph.nodes

    def shortest_path(self, source: Node, target: Node) -> Optional[Sequence[Edge]]:
        path_of_nodes = nx.shortest_path(
            self.graph,
            source=source,
            target=target,
            weight="cost",
            method=self.cfg.PATH_FINDING_METHOD,
        )
        if len(path_of_nodes) > 1:
            return self.node_list_to_edge_list(path_of_nodes)
        else:
            self._log.error(f"shortest_path: No path found from {source} to {target}.")
            return None

    def shortest_path_len(self, source: Node, target: Node):
        # TODO: use the reconstruct path function
        # with an all pairs algorithms that also returns a predecessor dict.

        path_len = nx.shortest_path_length(
            self.graph,
            source=source,
            target=target,
            weight="cost",
            method=self.cfg.PATH_FINDING_METHOD,
        )

        return path_len

    def node_list_to_edge_list(self, node_list: Sequence[Node]) -> Sequence[Edge]:
        action_path: list[Edge] = []
        for i in range(len(node_list) - 1):
            min_cost_edge = self.get_edge_with_lowest_weight(
                node_list[i], node_list[i + 1]
            )
            action_path.append(min_cost_edge)
        self._log.debug(f"node_list_to_edge_list(): action_path: {action_path}")

        return action_path

    def calc_edge_len(self, node_a, node_b):
        """calculates the distance between two nodes"""
        return math.sqrt(
            (self.graph.nodes[node_a]["pos"][0] - self.graph.nodes[node_b]["pos"][0])
            ** 2
            + (self.graph.nodes[node_a]["pos"][1] - self.graph.nodes[node_b]["pos"][1])
            ** 2
        )

    def add_start_waypoints(self, pos: tuple) -> None:
        """adds start points to the graph"""
        self.graph.add_node(
            self.next_wp_idx, pos=pos, type=NodeType.WAYPOINT, id=uuid.uuid4()
        )
        self.next_wp_idx += 1

    def add_waypoint(self, pos: tuple, prev_wp) -> None:
        """adds new waypoints and increments wp the idx"""

        self.graph.add_node(
            self.next_wp_idx, pos=pos, type=NodeType.WAYPOINT, id=uuid.uuid4()
        )

        self.add_waypoint_diedge(self.next_wp_idx, prev_wp)
        self.next_wp_idx += 1

    def add_waypoint_diedge(self, node_a, node_b) -> None:
        """adds a waypoint edge in both direction to the graph"""
        d = {
            "type": Behavior.GOTO,
            "id": uuid.uuid4(),
            "cost": self.calc_edge_len(node_a, node_b),
        }
        if self.check_if_edge_exists(node_a, node_b):
            self._log.warning(f"Edge between a:{node_a} and b:{node_b} already exists")
            return
        if self.check_if_edge_exists(node_b, node_a):
            self._log.warning(f"Edge between b:{node_b} and a:{node_a} already exists")
            return

        self.graph.add_edges_from([(node_a, node_b, d), (node_b, node_a, d)])

    def add_my_edge(self, node_a, node_b, edge_type):
        # my_id = (uuid.uuid4(),)
        my_id = uuid.uuid4()
        self.graph.add_edge(
            node_a,
            node_b,
            type=edge_type,
            cost=self.calc_edge_len(node_a, node_b),
            id=my_id,
        )
        return my_id

    def add_world_object(self, pos: tuple, label: str) -> None:
        """adds a world object to the graph"""
        self.graph.add_node(label, pos=pos, type=NodeType.WORLD_OBJECT, id=uuid.uuid4())

        if self.check_if_edge_exists(label, self.next_wp_idx - 1):
            self._log.warning(
                f"Edge between {label} and {self.next_wp_idx - 1} already exists"
            )
            return

        # HACK: instead of adding infite cost toworld object edges, use a subgraph for specific planning problems
        self.graph.add_edge(
            self.next_wp_idx - 1,
            label,
            type=Behavior.PLAN_EXTRACTION_WO_EDGE,
            id=uuid.uuid4(),
            cost=-100,
        )

    def add_frontier(self, pos: tuple, agent_at_wp: Node) -> None:
        """adds a frontier to the graph"""
        self.graph.add_node(
            self.next_frontier_idx, pos=pos, type=NodeType.FRONTIER, id=uuid.uuid4()
        )

        edge_len = self.calc_edge_len(agent_at_wp, self.next_frontier_idx)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the longest waypoints
        else:
            cost = edge_len

        if self.check_if_edge_exists(agent_at_wp, self.next_frontier_idx):
            self._log.warning(
                f"add_frontier(): Edge between {agent_at_wp} and {self.next_frontier_idx} already exists"
            )
            return

        edge_uuid = uuid.uuid4()
        self.graph.add_edge(
            agent_at_wp,
            self.next_frontier_idx,
            type=Behavior.EXPLORE,
            id=edge_uuid,
            cost=cost,
        )
        self.tasks.append(Task(edge_uuid, Objective.EXPLORE))

        self.next_frontier_idx += 1

    def add_guide_action_edges(self, path: Sequence[Node]):
        """adds edges between the nodes in the path"""
        # TODO: make these edge costs super explicit
        for i in range(len(path) - 1):
            self.graph.add_edge(
                path[i],
                path[i + 1],
                type=Behavior.GUIDE_WP_EDGE,
                id=uuid.uuid4(),
                cost=0,
            )

    def remove_frontier(self, target_frontier_idx) -> None:
        """removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(target_frontier_idx)
        if target_frontier["type"] == NodeType.FRONTIER:
            self.graph.remove_node(target_frontier_idx)  # also removes the edge

    # TODO: this should be invalidate, so that we change its alpha or smth
    # e.g. a method to invalidate a world object for planning, but still maintain it for vizualisation
    def remove_world_object(self, idx) -> None:
        """removes a frontier from the graph"""
        removal_target = self.get_node_data_by_node(idx)
        if removal_target["type"] == NodeType.WORLD_OBJECT:
            self.graph.remove_node(idx)  # also removes the edge

    def get_node_by_pos(self, pos: tuple):
        """returns the node idx at the given position"""
        for node in self.graph.nodes():
            if self.graph.nodes[node]["pos"] == pos:
                return node

    def get_node_by_UUID(self, UUID):
        """returns the node idx with the given UUID"""
        for node in self.graph.nodes():
            if self.graph.nodes[node]["id"] == UUID:
                return node

    def get_edge_by_UUID(self, UUID):
        """returns the edge idx with the given UUID"""
        for edge in self.graph.edges(keys=True):
            if self.graph.edges[edge]["id"] == UUID:
                return edge

        # raise ValueError(f"No edge with UUID {UUID} found")

    def get_node_data_by_node(self, node: Node) -> dict:
        """returns the node corresponding to the given index"""
        return self.graph.nodes[node]

    def get_all_waypoints(self) -> list:
        """returns all waypoints in the graph"""
        return [
            self.graph.nodes[node]
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.WAYPOINT
        ]

    def get_all_waypoint_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.WAYPOINT
        ]

    def get_all_frontiers_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == NodeType.FRONTIER
        ]

    def get_all_world_object_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
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

    def get_edge_with_lowest_weight(self, node_a: Node, node_b: Node) -> Edge:
        """returns the lowest weight edge between two nodes"""
        keys_of_parallel_edges = [
            key for key in self.graph.get_edge_data(node_a, node_b).keys()
        ]

        if len(keys_of_parallel_edges) == 0:
            self._log.warning(
                f"get_edge_with_lowest_weight(): No edge between {node_a} and {node_b}"
            )
            return None

        key_of_edge_with_min_cost = min(
            keys_of_parallel_edges,
            key=lambda x: self.graph.edges[node_a, node_b, x]["cost"],
        )

        return node_a, node_b, key_of_edge_with_min_cost

    def get_behavior_of_edge(self, edge: Edge) -> Optional[Behavior]:
        """returns the type of the edge between two nodes"""
        if len(edge) == 2:
            # return self.graph.edges[edge]["type"]
            yolo = self.graph.edges[edge]["type"]
            print(yolo)
            return yolo
        elif len(edge) == 3:
            node_a, node_b, edge_id = edge
            return self.graph.edges[node_a, node_b, edge_id]["type"]
        else:
            self._log.error(f"get_type_of_edge(): wrong length of edge tuple: {edge}")

    def remove_invalid_tasks(self):
        for task in self.tasks:
            if task.edge_uuid not in [
                ddict["id"] for u, v, ddict in self.graph.edges(data=True)
            ]:
                self.tasks.remove(task)
