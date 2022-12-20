import logging
from typing import Optional, Sequence
from uuid import uuid4

import networkx as nx

from src.shared.prior_knowledge.affordance import Affordance
from src.shared.prior_knowledge.sar_behaviors import Behaviors
from src.shared.prior_knowledge.sar_objectives import Objectives
from src.shared.prior_knowledge.sar_situations import Situations
from src.shared.task import Task
from src.shared.types.node_and_edge import Edge, Node

# **Tuesday, Dec 20@16:22::** 350 lines


class SituationalGraph:
    # TODO: separate behavior from data
    # graphOperations(graph) <-> behavior post effects
    # graphData -> nodes, edges, node_data, edge_data -> dataclass
    # graphInterface -> networkx shit
    # missionState = graph + tasks

    # what operations work on graph + tasks? -> missionOperations
    """Behavior-Oriented Situational Graph tailored to missions centered around data collection and obtaining information"""

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

        self.G = nx.MultiDiGraph()
        self.tasks: list[Task] = []

    def get_nodes_by_type(self, node_type: Situations) -> list[Node]:
        return [
            node for node in self.G.nodes() if self.G.nodes[node]["type"] == node_type
        ]

    """Calc stuff"""

    def calc_edge_len_between_nodes(self, a: Node, b: Node) -> float:
        """calculates the distance between two nodes"""
        return self.calc_edge_len_pos(self.G.nodes[a]["pos"], self.G.nodes[b]["pos"])

    def calc_edge_len_pos(
        self, a: tuple[float, float], b: tuple[float, float]
    ) -> float:
        """calculates the distance between two nodes"""
        (x1, y1) = a
        (x2, y2) = b
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    """Add stuff"""

    def add_edge_of_type(
        self,
        a: Node,
        b: Node,
        edge_type: Behaviors,
        cost: Optional[float] = None,
    ) -> Edge:
        e_id = uuid4()
        
        if not cost:
            cost = self.calc_edge_len_between_nodes(a, b)

        self.G.add_edge(
            a,
            b,
            key=e_id,
            type=edge_type,
            cost=cost,
        )
        return (a, b, e_id)

    def add_node_of_type(
        self, pos: tuple[float, float], object_type: Situations
    ) -> Node:
        node_uuid = uuid4()
        self.G.add_node(node_uuid, pos=pos, type=object_type)
        return node_uuid

    def add_waypoint_node(self, pos: tuple[float, float]) -> Node:
        """used to add start points to the graph"""

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

        ft_node = self.add_node_of_type(pos, Situations.FRONTIER)

        edge_len = self.calc_edge_len_between_nodes(from_node, ft_node)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the frontiers with the longest edges.
        else:
            cost = edge_len

        if self.G.has_edge(from_node, ft_node):
            self._log.warning(
                f"add_frontier(): Edge between {from_node} and {ft_node} already exists"
            )
            return

        edge = self.add_edge_of_type(from_node, ft_node, Behaviors.EXPLORE, cost=cost)

        self.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

    """Remove stuff"""

    def remove_frontier(self, ft_node: Node) -> None:
        """removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(ft_node)
        self.remove_tasks_associated_with_node(ft_node)
        if target_frontier["type"] == Situations.FRONTIER:
            self.G.remove_node(ft_node)  # also removes the edge
        else:
            self._log.warning(f"remove_frontier(): {ft_node} is not a frontier")
            return

    """Get stuff"""

    def get_task_by_edge(self, edge: Edge) -> Optional[Task]:
        """returns the task associated with the edge"""
        for task in self.tasks:
            if task.edge == edge:
                return task

    def get_node_by_exact_pos(self, pos: tuple[float, float]) -> Node:
        """returns the node idx at the given exact position"""
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

        if edge not in self.G.edges:
            self._log.warning(f"get_behavior_of_edge(): {edge} not in graph")
            return None
        if len(edge) != 3:
            self._log.error(f"get_behavior_of_edge(): wrong length of edge tuple: {edge}")
            return None

        node_a, node_b, edge_id = edge
        return self.G.edges[node_a, node_b, edge_id]["type"]

    def get_closest_waypoint_to_pos(self, pos: tuple[float, float]) -> Node:
        """returns the closest waypoint to the given position"""
        closest_node = None
        min_dist = float("inf")
        for node in self.G.nodes:
            if self.G.nodes[node]["type"] == Situations.WAYPOINT:
                dist = self.calc_edge_len_pos(pos, self.G.nodes[node]["pos"])
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node

        return closest_node

    """Extract value from graph stuff"""
    # TODO: add Self typing
    def filter_graph(self, capabilities: set):
        def filter_edges_based_on_agent_capabilities(u: Node, v: Node, k: Node) -> bool:
            behavior_enum = self.G.edges[u, v, k]["type"]  # Behaviors
            for req_cap in behavior_enum.required_capabilities:
                if req_cap not in capabilities:
                    return False
            return True

        filtered_G = nx.subgraph_view(
            self.G, filter_edge=filter_edges_based_on_agent_capabilities
        )

        # here we insert the filtered graph into a new tosg object
        filtered_tosg = SituationalGraph()
        filtered_tosg.tasks = self.tasks
        filtered_tosg.G = filtered_G
        return filtered_tosg

    """Task manager stuff"""

    def check_if_tasks_exhausted(self) -> bool:
        num_of_tasks = len(self.tasks)
        if num_of_tasks < 1:
            print("No more tasks left")
            return True
        else:
            return False

    def remove_tasks_associated_with_node(self, node: Node):
        """removes all tasks associated with a node"""
        for task in self.tasks:
            if node in task.edge:
                self.tasks.remove(task)

    def add_node_with_task_and_edges_from_affordances(
        self,
        from_node: Node,
        object_type: Situations,
        pos: tuple[float, float],
        affordances: list[Affordance],
    ) -> Node:
        new_node = self.add_node_of_type(pos, object_type)
        for affordance in affordances:
            if affordance[0] == object_type:
                edge = self.add_edge_of_type(from_node, new_node, affordance[1])
                self.tasks.append(Task(edge, affordance[2]))

        return new_node

    """Convert stuff"""

    def node_list_to_edge_list(self, node_list: Sequence[Node]) -> list[Edge]:
        action_path: list[Edge] = []
        for i in range(len(node_list) - 1):
            min_cost_edge = self.get_edge_with_lowest_weight(
                node_list[i], node_list[i + 1]
            )
            action_path.append(min_cost_edge)
        self._log.debug(f"node_list_to_edge_list(): action_path: {action_path}")

        return action_path
