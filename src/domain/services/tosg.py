import logging
from typing import List, Optional, Sequence
from uuid import UUID, uuid4

import networkx as nx
from src.configuration.config import Config
from src.domain import (
    Affordance,
    Behaviors,
    Edge,
    Node,
    Objectives,
    ObjectTypes,
    Plan,
    Task,
)


# TODO: separate behavior from data
"""Task-Oriented Situational Graph"""


class TOSG:
    def __init__(self, cfg: Config) -> None:
        self._log = logging.getLogger(__name__)

        self.G = nx.MultiDiGraph()
        self.cfg = cfg

        self.tasks: List[Task] = []

    def shortest_path(self, source: Node, target: Node) -> Optional[Sequence[Edge]]:
        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        path_of_nodes = nx.astar_path(
            self.G,
            source=source,
            target=target,
            weight="cost",
            heuristic=dist_heur_wrapper,
        )
        if len(path_of_nodes) > 1:
            return self.node_list_to_edge_list(path_of_nodes)
        else:
            self._log.error(f"shortest_path: No path found from {source} to {target}.")
            return None

    def shortest_path_len(self, source: Node, target: Node):
        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        path_len = nx.astar_path_length(
            self.G,
            source=source,
            target=target,
            weight="cost",
            heuristic=dist_heur_wrapper,
        )

        return path_len

    def calc_edge_len(self, a: Node, b: Node) -> float:
        """calculates the distance between two nodes"""
        (x1, y1) = self.G.nodes[a]["pos"]
        (x2, y2) = self.G.nodes[b]["pos"]
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    # TODO: this  is kind of
    def node_list_to_edge_list(self, node_list: Sequence[Node]) -> Sequence[Edge]:
        action_path: list[Edge] = []
        for i in range(len(node_list) - 1):
            min_cost_edge = self.get_edge_with_lowest_weight(
                node_list[i], node_list[i + 1]
            )
            action_path.append(min_cost_edge)
        self._log.debug(f"node_list_to_edge_list(): action_path: {action_path}")

        return action_path

    # this is the only place where we call the add_node method
    def add_node_of_type(self, pos: tuple[float, float], object_type: ObjectTypes):
        node_uuid = uuid4()
        self.G.add_node(node_uuid, pos=pos, type=object_type, id=node_uuid)
        # self.graph.add_node(node_uuid, pos=pos, type=object_type)
        return node_uuid

    def add_waypoint_node(self, pos: tuple) -> UUID:
        """adds start points to the graph"""

        return self.add_node_of_type(pos, ObjectTypes.WAYPOINT)

    def add_waypoint_and_diedge(self, pos: tuple, prev_wp) -> None:
        """adds new waypoints and increments wp the idx"""
        # self.add_waypoint_node(pos)

        new_node = self.add_waypoint_node(pos)
        self.add_waypoint_diedge(new_node, prev_wp)

    def add_my_edge(
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
            id=my_id,
        )
        return (node_a, node_b, my_id)

    def add_waypoint_diedge(self, node_a: Node, node_b: Node) -> None:
        """adds a waypoint edge in both direction to the graph"""
        # HACK: this edge should be based on an affordance
        d = {
            "type": Behaviors.GOTO,
            "id": uuid4(),  # TODO: remove
            "cost": self.calc_edge_len(node_a, node_b),
        }
        if self.G.has_edge(node_a, node_b):
            self._log.warning(f"Edge between a:{node_a} and b:{node_b} already exists")
            return
        if self.G.has_edge(node_b, node_a):
            self._log.warning(f"Edge between b:{node_b} and a:{node_a} already exists")
            return

        # TODO: make this use the my edge fucntion above
        self.G.add_edges_from(
            [(node_a, node_b, uuid4(), d), (node_b, node_a, uuid4(), d)]
        )

    def add_frontier(self, pos: tuple, agent_at_wp: Node) -> None:
        """adds a frontier to the graph"""
        ft_node_uuid = uuid4()
        self.G.add_node(
            ft_node_uuid, pos=pos, type=ObjectTypes.FRONTIER, id=ft_node_uuid
        )

        edge_len = self.calc_edge_len(agent_at_wp, ft_node_uuid)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the longest waypoints
        else:
            cost = edge_len

        if self.G.has_edge(agent_at_wp, ft_node_uuid):
            self._log.warning(
                f"add_frontier(): Edge between {agent_at_wp} and {ft_node_uuid} already exists"
            )
            return

        # edge_uuid = uuid4()

        # self.G.add_edge(
        #     agent_at_wp,
        #     ft_node_uuid,
        #     type=Behaviors.EXPLORE,
        #     id=edge_uuid,
        #     cost=cost,
        #     key=edge_uuid,
        # )
        # _, _, edge_uuid = self.add_my_edge(
        #     agent_at_wp, ft_node_uuid, Behaviors.EXPLORE, cost=cost
        # )
        edge = self.add_my_edge(agent_at_wp, ft_node_uuid, Behaviors.EXPLORE, cost=cost)

        self.tasks.append(Task(edge, Objectives.EXPLORE_ALL_FTS))

    def remove_frontier(self, target_frontier_idx: Node) -> None:
        """removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(target_frontier_idx)
        self.remove_tasks_associated_with_node(target_frontier_idx)
        if target_frontier["type"] == ObjectTypes.FRONTIER:
            self.G.remove_node(target_frontier_idx)  # also removes the edge
        else:
            self._log.warning(
                f"remove_frontier(): {target_frontier_idx} is not a frontier"
            )
            return

    def remove_tasks_associated_with_node(self, node_idx: Node):
        """removes all tasks associated with a node"""
        for task in self.tasks:
            if node_idx in task.edge:
                self.tasks.remove(task)

    def get_task_by_edge(self, edge: Edge) -> Optional[Task]:
        """returns the task associated with the edge"""
        for task in self.tasks:
            if task.edge == edge:
                return task

    # # TODO: this should be invalidate, so that we change its alpha or smth
    # # e.g. a method to invalidate a world object for planning, but still maintain it for vizualisation
    # def remove_world_object(self, idx) -> None:
    #     """removes a frontier from the graph"""
    #     removal_target = self.get_node_data_by_node(idx)
    #     if removal_target["type"] == ObjectTypes.WORLD_OBJECT:
    #         self.G.remove_node(idx)  # also removes the edge

    def get_node_by_pos(self, pos: tuple):
        """returns the node idx at the given position"""
        for node in self.G.nodes():
            if self.G.nodes[node]["pos"] == pos:
                return node

    # THIS one can soon be gone.
    def get_node_by_UUID(self, uuid: UUID) -> Node:
        """returns the node idx with the given UUID"""
        for node in self.G.nodes():
            if self.G.nodes[node]["id"] == uuid:
                return node

    def get_edge_by_UUID(self, UUID) -> Optional[Edge]:
        """returns the edge tuple with the given UUID"""
        for src_node, target_node, edge_key, edge_id in self.G.edges(
            data="id", keys=True
        ):
            if edge_id == UUID:
                # if edge_id == UUID or edge_key == UUID:
                return src_node, target_node, edge_key

    def get_node_data_by_node(self, node: Node) -> dict:
        """returns the node corresponding to the given index"""
        return self.G.nodes[node]

    def get_all_waypoints(self) -> list:
        """returns all waypoints in the graph"""
        return [
            self.G.nodes[node]
            for node in self.G.nodes()
            if self.G.nodes[node]["type"] == ObjectTypes.WAYPOINT
        ]

    def get_all_waypoint_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.G.nodes()
            if self.G.nodes[node]["type"] == ObjectTypes.WAYPOINT
        ]

    def get_all_frontiers_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.G.nodes()
            if self.G.nodes[node]["type"] == ObjectTypes.FRONTIER
        ]

    def get_all_world_object_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.G.nodes()
            if self.G.nodes[node]["type"] == ObjectTypes.WORLD_OBJECT
        ]

    def get_nodes_of_type_in_margin(
        self, pos: tuple[float, float], margin: float, node_type: ObjectTypes
    ) -> list:
        """
        Given a position, a margin and a node type, return a list of nodes of that type that are within the margin of the position.

        :param pos: the position of the agent
        :param margin: the margin of the square to look
        :param node_type: the type of node to search for
        :return: The list of nodes that are close to the given position.
        """
        close_nodes = []
        for node in self.G.nodes:
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
            # return self.graph.edges[edge]["type"]
            yolo = self.G.edges[edge]["type"]
            print(yolo)
            return yolo
        elif len(edge) == 3:
            node_a, node_b, edge_id = edge
            return self.G.edges[node_a, node_b, edge_id]["type"]
        else:
            self._log.error(f"get_type_of_edge(): wrong length of edge tuple: {edge}")

    def remove_invalid_tasks(self):
        # all_edge_ids = [ddict["id"] for u, v, ddict in self.G.edges(data=True)]
        # this is like a massive list so I feel like there should be a better way
        for task in self.tasks:
            # if task.edge_uuid not in all_edge_ids:
            if not self.G.has_edge(*task.edge):
                self._log.error(f"remove_invalid_tasks(): removing task {task}")
                self.tasks.remove(task)

    def validate_plan(self, plan: Plan) -> bool:
        if not plan:
            return False
        if len(plan) < 1:
            return False
        if not self.G.has_node(plan[-1][1]):
            return False

        return True

    def remove_node(self, node: Node):
        self.G.remove_node(node)

    def add_node_with_task_and_edges_from_affordances(
        self,
        from_node: Node,
        object_type: ObjectTypes,
        pos: tuple,
        affordances: list[Affordance],
    ):
        """
        Adds a node with edges from the affordances of the given object type.
        :param object_type: the type of object to add
        :param pos: the position of the node
        :return: the id of the node
        """
        node_id = uuid4()
        self.G.add_node(node_id, pos=pos, type=object_type, id=node_id)
        for affordance in affordances:
            if affordance[0] == object_type:

                edge = self.add_my_edge(from_node, node_id, affordance[1])

                self.tasks.append(Task(edge, affordance[2]))

        print(self.tasks)

        return node_id
