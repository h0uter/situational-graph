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


class SituationalGraph:
    # TODO: separate behavior from data
    # graphController(graph) <-> behavior post effects
    # graphData -> nodes, edges, node_data, edge_data -> dataclass
    # graphInterface -> networkx shit
    # missionState = graph + tasks

    # what operations work on graph + tasks? -> missionOperations
    """
    Behavior-Oriented Situational Graph
    tailored to missions centered around data collection and obtaining information
    """

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

        self.G = nx.MultiDiGraph()
        self.tasks: list[Task] = []

    """Calc stuff"""

    def calc_edge_len_between_nodes(self, a: Node, b: Node) -> float:
        """calculates the distance between two nodes"""
        return self._calc_edge_len_pos(self.G.nodes[a]["pos"], self.G.nodes[b]["pos"])

    @staticmethod
    def _calc_edge_len_pos(a: tuple[float, float], b: tuple[float, float]) -> float:
        """calculates the distance between two positions"""
        (x1, y1) = a
        (x2, y2) = b
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    """Get stuff"""

    def get_nodes_by_type(self, node_type: Situations) -> list[Node]:
        return [
            node for node in self.G.nodes() if self.G.nodes[node]["type"] == node_type
        ]

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
        Given a position, a margin and a node type,
        return a list of nodes of that type that are within the margin of the position.
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

    def get_edge_with_lowest_weight(self, a: Node, b: Node) -> Optional[Edge]:
        """returns the lowest weight edge between two nodes"""
        edge_data = self.G.get_edge_data(a, b)
        if not edge_data:
            return None
        keys_of_parallel_edges = [key for key in edge_data.keys()]

        if len(keys_of_parallel_edges) == 0:
            self._log.warning(
                f"get_edge_with_lowest_weight(): No edge between {a} and {b}"
            )
            return None

        key_of_edge_with_min_cost = min(
            keys_of_parallel_edges,
            key=lambda x: self.G.edges[a, b, x]["cost"],
        )

        return a, b, key_of_edge_with_min_cost

    def get_behavior_of_edge(self, edge: Edge) -> Optional[Behaviors]:
        """returns the type of the edge between two nodes"""

        if edge not in self.G.edges:
            self._log.warning(f"{edge} not in graph")
            return None
        if len(edge) != 3:
            self._log.error(f"wrong length of edge tuple: {edge}")
            return None

        node_a, node_b, edge_id = edge
        return self.G.edges[node_a, node_b, edge_id]["type"]

    def get_closest_waypoint_to_pos(self, pos: tuple[float, float]) -> Node:
        """returns the closest waypoint to the given position"""
        closest_node = None
        min_dist = float("inf")
        for node in self.G.nodes:
            if self.G.nodes[node]["type"] == Situations.WAYPOINT:
                dist = self._calc_edge_len_pos(pos, self.G.nodes[node]["pos"])
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node

        return closest_node

    def get_filtered_graph(self, capabilities: set):
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

    """Convert stuff"""

    def node_list_to_edge_list(self, node_list: Sequence[Node]) -> list[Edge]:
        action_path: list[Edge] = []
        for i in range(len(node_list) - 1):
            min_cost_edge = self.get_edge_with_lowest_weight(
                node_list[i], node_list[i + 1]
            )
            action_path.append(min_cost_edge)
        self._log.debug(f"action_path: {action_path}")

        return action_path

    """GRAPH CONTROLLER"""
    """Add stuff"""

    def add_node_with_task_and_edges_from_affordances(
        self,
        from_node: Node,
        object_type: Situations,
        pos: tuple[float, float],
        affordances: list[Affordance],
    ) -> Node:
        new_node = self.add_node_of_type(pos, object_type)
        for affordance in affordances:
            # TODO: named tuple would be nicer
            if affordance[0] == object_type:
                edge = self.add_edge_of_type(from_node, new_node, affordance[1])
                self.tasks.append(Task(edge, affordance[2]))

        return new_node

    def add_node_of_type(self, pos: tuple[float, float], node_type: Situations) -> Node:
        node_uuid = uuid4()
        self.G.add_node(node_uuid, pos=pos, type=node_type)
        return node_uuid

    def add_edge_of_type(
        self,
        a: Node,
        b: Node,
        edge_type: Behaviors,
    ) -> Edge:

        edge_id = uuid4()

        cost = self.calc_edge_len_between_nodes(a, b)

        self.G.add_edge(
            a,
            b,
            key=edge_id,
            type=edge_type,
            cost=cost,
        )
        return (a, b, edge_id)

    def add_waypoint_diedge(self, a: Node, b: Node) -> None:
        self.add_edge_of_type(a, b, Behaviors.GOTO)
        self.add_edge_of_type(b, a, Behaviors.GOTO)

    """Remove stuff"""

    def remove_node_and_tasks(self, a: Node):
        self.G.remove_node(a)  # also removes the edge
        self.remove_tasks_associated_with_node(a)

    """Task manager stuff"""

    def check_if_tasks_exhausted(self) -> bool:
        if len(self.tasks) < 1:
            return True
        else:
            return False

    def remove_tasks_associated_with_node(self, node: Node):
        """removes all tasks associated with a node"""
        for task in self.tasks:
            if node in task.edge:
                self.tasks.remove(task)
