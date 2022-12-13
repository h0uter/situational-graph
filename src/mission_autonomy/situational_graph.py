import logging
from typing import Optional, Sequence
from uuid import uuid4

import networkx as nx

from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.behaviors import Behaviors
from src.shared.node_and_edge import Edge, Node
from src.shared.prior_knowledge.objectives import Objectives
from src.shared.prior_knowledge.situations import Situations
from src.shared.task import Task


class SituationalGraph:
    # TODO: separate behavior from data
    """Behavior-Oriented Situational Graph"""

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

        self.G = nx.MultiDiGraph()
        self.tasks: list[Task] = []

    @property
    def waypoint_idxs(self) -> list[Node]:
        """returns all waypoints idxs in the graph"""
        return self.get_nodes_by_type(Situations.WAYPOINT)

    @property
    def frontier_idxs(self) -> list[Node]:
        """returns all frontier idxs in the graph"""
        return self.get_nodes_by_type(Situations.FRONTIER)

    def get_nodes_by_type(self, node_type: Situations) -> list[Node]:
        """returns all frontier idxs in the graph"""
        return [
            node for node in self.G.nodes() if self.G.nodes[node]["type"] == node_type
        ]

    def shortest_path(self, source: Node, target: Node) -> Optional[Sequence[Edge]]:
        """returns the shortest path between two nodes"""

        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        try:
            path_of_nodes = nx.astar_path(
                self.G,
                source=source,
                target=target,
                weight="cost",
                heuristic=dist_heur_wrapper,
            )
        except nx.NetworkXNoPath:
            self._log.debug(f"shortest_path: No path found from {source} to {target}.")
            return None

        if len(path_of_nodes) > 1:
            return self.node_list_to_edge_list(path_of_nodes)
        else:
            self._log.error(f"shortest_path: No path found from {source} to {target}.")
            return None

    def distance_astar(self, source: Node, target: Node) -> float:
        """returns the length of the shortest path between two nodes"""

        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        try:
            distance = nx.astar_path_length(
                self.G,
                source=source,
                target=target,
                weight="cost",
                heuristic=dist_heur_wrapper,
            )
        except nx.NetworkXNoPath:
            self._log.debug(
                f"shortest_path_len: No path found from {source} to {target}."
            )
            distance = float("inf")

        return distance

    def distance_and_path_dijkstra(
        self, source: Node, targets: list[Node]
    ) -> tuple[dict, dict]:
        """returns the length of the shortest path between a single source and multiple targets"""

        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        try:
            distance, path = nx.single_source_dijkstra(
                self.G,
                source=source,
                # target=targets,
                weight="cost",
                # heuristic=dist_heur_wrapper,
            )
        except nx.NetworkXNoPath:
            self._log.debug(
                f"shortest_path_len: No path found from {source} to {targets}."
            )
            distance = {target: float("inf") for target in targets}

        return distance, path

    def calc_edge_len(self, a: Node, b: Node) -> float:
        """calculates the distance between two nodes"""
        (x1, y1) = self.G.nodes[a]["pos"]
        (x2, y2) = self.G.nodes[b]["pos"]
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def node_list_to_edge_list(self, node_list: Sequence[Node]) -> Sequence[Edge]:
        action_path: list[Edge] = []
        for i in range(len(node_list) - 1):
            min_cost_edge = self.get_edge_with_lowest_weight(
                node_list[i], node_list[i + 1]
            )
            action_path.append(min_cost_edge)
        self._log.debug(f"node_list_to_edge_list(): action_path: {action_path}")

        return action_path

    def add_edge_of_type(
        self,
        node_a: Node,
        node_b: Node,
        edge_type: Behaviors,
        cost: Optional[float] = None,
    ) -> Edge:
        my_id = uuid4()
        if not cost:
            cost = self.calc_edge_len(node_a, node_b)

        self.G.add_edge(
            node_a,
            node_b,
            key=my_id,
            type=edge_type,
            cost=cost,
        )
        return (node_a, node_b, my_id)

    def add_node_with_task_and_edges_from_affordances(
        self,
        from_node: Node,
        object_type: Situations,
        pos: tuple,
        affordances: list[Affordance],
    ) -> Node:
        """
        Adds a node with edges from the affordances of the given object type.
        """
        new_node = self.add_node_of_type(pos, object_type)
        for affordance in affordances:
            if affordance[0] == object_type:
                edge = self.add_edge_of_type(from_node, new_node, affordance[1])
                self.tasks.append(Task(edge, affordance[2]))

        return new_node

    def add_node_of_type(
        self, pos: tuple[float, float], object_type: Situations
    ) -> Node:
        node_uuid = uuid4()
        self.G.add_node(node_uuid, pos=pos, type=object_type)
        return node_uuid

    def add_waypoint_node(self, pos: tuple[float, float]) -> Node:
        """adds start points to the graph"""

        return self.add_node_of_type(pos, Situations.WAYPOINT)

    def add_waypoint_and_diedge(
        self, to_pos: tuple[float, float], from_node: Node
    ) -> None:
        """adds new waypoints and increments wp the idx"""
        new_node = self.add_waypoint_node(to_pos)
        self.add_waypoint_diedge(new_node, from_node)

    def add_waypoint_diedge(self, node_a: Node, node_b: Node) -> None:
        """adds a waypoint edge in both direction to the graph"""

        if self.G.has_edge(node_a, node_b):
            self._log.warning(f"Edge between a:{node_a} and b:{node_b} already exists")
            return
        if self.G.has_edge(node_b, node_a):
            self._log.warning(f"Edge between b:{node_b} and a:{node_a} already exists")
            return

        self.add_edge_of_type(node_a, node_b, Behaviors.GOTO)
        self.add_edge_of_type(node_b, node_a, Behaviors.GOTO)

    def add_frontier(self, pos: tuple[float, float], from_node: Node) -> None:
        """adds a frontier to the graph"""

        ft_node = self.add_node_of_type(pos, Situations.FRONTIER)

        edge_len = self.calc_edge_len(from_node, ft_node)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the longest waypoints
        else:
            cost = edge_len

        if self.G.has_edge(from_node, ft_node):
            self._log.warning(
                f"add_frontier(): Edge between {from_node} and {ft_node} already exists"
            )
            return

        edge = self.add_edge_of_type(from_node, ft_node, Behaviors.EXPLORE, cost=cost)

        self.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

    def remove_frontier(self, ft_node: Node) -> None:
        """removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(ft_node)
        self.remove_tasks_associated_with_node(ft_node)
        if target_frontier["type"] == Situations.FRONTIER:
            self.G.remove_node(ft_node)  # also removes the edge
        else:
            self._log.warning(f"remove_frontier(): {ft_node} is not a frontier")
            return

    def remove_tasks_associated_with_node(self, node: Node):
        """removes all tasks associated with a node"""
        for task in self.tasks:
            if node in task.edge:
                self.tasks.remove(task)

    def get_task_by_edge(self, edge: Edge) -> Optional[Task]:
        """returns the task associated with the edge"""
        for task in self.tasks:
            if task.edge == edge:
                return task

    def get_node_by_pos(self, pos: tuple[float, float]) -> Node:
        """returns the node idx at the given position"""
        for node in self.G.nodes():
            if self.G.nodes[node]["pos"] == pos:
                return node

    def get_node_data_by_node(self, node: Node) -> dict:
        """returns the node data dict"""
        return self.G.nodes[node]

    # this function is 9% of total comopute
    def get_nodes_of_type_in_margin(
        self, pos: tuple[float, float], margin: float, node_type: Situations
    ) -> list:
        """
        Given a position, a margin and a node type, return a list of nodes of that type that are within the margin of the position.
        """
        # TODO: solve this by using neighbors
        # node_pos_data_dict = nx.get_node_attributes(self.G, "pos")
        # nodes_at_pos = [
        #     node
        #     for node, pos_data in node_pos_data_dict.items()
        #     if (
        #         abs(pos[0] - pos_data[0]) < margin
        #         and abs(pos[1] - pos_data[1]) < margin
        #     )
        # ]
        # nodes_of_type = [
        #     node for node in nodes_at_pos if self.G.nodes[node]["type"] == node_type
        # ]
        # return nodes_of_type

        close_nodes = []
        for node in self.G.nodes:
            data = self.get_node_data_by_node(node)
            if data["type"] == node_type:
                pos_data = data["pos"]
                if (
                    abs(pos[0] - pos_data[0]) < margin
                    and abs(pos[1] - pos_data[1]) < margin
                ):
                    close_nodes.append(node)

        return close_nodes

    def get_edge_with_lowest_weight(self, node_a: Node, node_b: Node) -> Edge:
        """returns the lowest weight edge between two nodes"""
        keys_of_parallel_edges = [
            key for key in self.G.get_edge_data(node_a, node_b).keys()
        ]

        if len(keys_of_parallel_edges) == 0:
            self._log.warning(
                f"get_edge_with_lowest_weight(): No edge between {node_a} and {node_b}"
            )
            return None

        key_of_edge_with_min_cost = min(
            keys_of_parallel_edges,
            key=lambda x: self.G.edges[node_a, node_b, x]["cost"],
        )

        return node_a, node_b, key_of_edge_with_min_cost

    def get_behavior_of_edge(self, edge: Edge) -> Optional[Behaviors]:
        """returns the type of the edge between two nodes"""
        if len(edge) == 2:
            yolo = self.G.edges[edge]["type"]
            # print(yolo)
            return yolo
        elif len(edge) == 3:
            node_a, node_b, edge_id = edge
            return self.G.edges[node_a, node_b, edge_id]["type"]
        else:
            self._log.error(f"get_type_of_edge(): wrong length of edge tuple: {edge}")
            return None

    def remove_invalid_tasks(self):
        """removes all tasks that are not valid anymore"""
        for task in self.tasks:
            if not self.G.has_edge(*task.edge):
                self._log.error(f"remove_invalid_tasks(): removing task {task}")
                self.tasks.remove(task)

    def check_if_tasks_exhausted(self) -> bool:
        num_of_tasks = len(self.tasks)
        if num_of_tasks < 1:
            return True
        else:
            return False