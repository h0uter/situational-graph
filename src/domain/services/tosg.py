import logging
import math
from typing import List, Optional, Sequence
from uuid import UUID, uuid4

import networkx as nx
from src.configuration.config import Config
from src.domain import (Affordance, Behaviors, Edge, Node, Objectives,
                        ObjectTypes, Plan, Task)


# FIXME: refactor this class a lot
# separate behavior from data
class TOSG:
    def __init__(self, cfg: Config) -> None:
        self._log = logging.getLogger(__name__)

        self.graph = nx.MultiDiGraph()  # Knowledge Road Map
        self.cfg = cfg
        self.next_wp_idx = 0

        self.tasks: List[Task] = []

        # self.next_frontier_idx = cfg.FRONTIER_INDEX_START
        # self.next_wo_idx = cfg.WORLD_OBJECT_INDEX_START

    def shortest_path(self, source: Node, target: Node) -> Optional[Sequence[Edge]]:
        def dist_heur_wrapper(a: Node, b: Node):
            return self.calc_edge_len(a, b)

        path_of_nodes = nx.astar_path(
            self.graph,
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
            self.graph,
            source=source,
            target=target,
            weight="cost",
            heuristic=dist_heur_wrapper,
        )

        return path_len

    def calc_edge_len(self, a: Node, b: Node) -> float:
        """calculates the distance between two nodes"""
        (x1, y1) = self.graph.nodes[a]["pos"]
        (x2, y2) = self.graph.nodes[b]["pos"]
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
        self.graph.add_node(node_uuid, pos=pos, type=object_type, id=node_uuid)
        # self.graph.add_node(node_uuid, pos=pos, type=object_type)
        return node_uuid

    # def add_waypoint_node(self, pos: tuple) -> int:
    def add_waypoint_node(self, pos: tuple) -> UUID:
        """adds start points to the graph"""
        # self.graph.add_node(
        #     self.next_wp_idx, pos=pos, type=ObjectTypes.WAYPOINT, id=uuid4()
        # )
        return self.add_node_of_type(pos, ObjectTypes.WAYPOINT)
        # self.next_wp_idx += 1
        # return self.next_wp_idx - 1

    def add_waypoint_and_diedge(self, pos: tuple, prev_wp) -> None:
        """adds new waypoints and increments wp the idx"""
        # self.add_waypoint_node(pos)
        # self.graph.add_node(
        #     self.next_wp_idx, pos=pos, type=ObjectTypes.WAYPOINT, id=uuid4()
        # )
        new_node = self.add_waypoint_node(pos)
        # self.add_waypoint_diedge(self.next_wp_idx, prev_wp)
        self.add_waypoint_diedge(new_node, prev_wp)
        # self.next_wp_idx += 1

    def add_my_edge(self, node_a: Node, node_b: Node, edge_type: Behaviors) -> UUID:
        # my_id = (uuid.uuid4(),)
        my_id = uuid4()
        self.graph.add_edge(
            node_a,
            node_b,
            key=my_id,
            type=edge_type,
            cost=self.calc_edge_len(node_a, node_b),
            id=my_id,
        )
        # self.graph.add_edge(
        #     node_a,
        #     node_b,
        #     key=my_id,
        #     type=edge_type,
        #     cost=self.calc_edge_len(node_a, node_b),
        #     id=my_id,
        # )
        return my_id

    def add_waypoint_diedge(self, node_a: Node, node_b: Node) -> None:
        """adds a waypoint edge in both direction to the graph"""
        # HACK: this edge should be based on an affordance
        d = {
            "type": Behaviors.GOTO,
            "id": uuid4(),  # TODO: remove
            "cost": self.calc_edge_len(node_a, node_b),
        }
        if self.graph.has_edge(node_a, node_b):
            self._log.warning(f"Edge between a:{node_a} and b:{node_b} already exists")
            return
        if self.graph.has_edge(node_b, node_a):
            self._log.warning(f"Edge between b:{node_b} and a:{node_a} already exists")
            return

        # TODO: make this use the my edge fucntion above
        self.graph.add_edges_from([(node_a, node_b, uuid4(), d), (node_b, node_a, uuid4(), d)])

    def add_frontier(self, pos: tuple, agent_at_wp: Node) -> None:
        """adds a frontier to the graph"""
        # self.graph.add_node(
        #     self.next_frontier_idx, pos=pos, type=ObjectTypes.FRONTIER, id=uuid4()
        # )
        ft_node_uuid = uuid4()
        self.graph.add_node(
            ft_node_uuid, pos=pos, type=ObjectTypes.FRONTIER, id=ft_node_uuid
        )

        # edge_len = self.calc_edge_len(agent_at_wp, self.next_frontier_idx)
        edge_len = self.calc_edge_len(agent_at_wp, ft_node_uuid)
        if edge_len:  # edge len can be zero in the final step.
            cost = 1 / edge_len  # Prefer the longest waypoints
        else:
            cost = edge_len

        # if self.graph.has_edge(agent_at_wp, self.next_frontier_idx):
        if self.graph.has_edge(agent_at_wp, ft_node_uuid):
            self._log.warning(
                # f"add_frontier(): Edge between {agent_at_wp} and {self.next_frontier_idx} already exists"
                f"add_frontier(): Edge between {agent_at_wp} and {ft_node_uuid} already exists"
            )
            return

        edge_uuid = uuid4()
        # self.graph.add_edge(
        #     agent_at_wp,
        #     self.next_frontier_idx,
        #     type=Behaviors.EXPLORE,
        #     id=edge_uuid,
        #     cost=cost,
        #     # key=edge_uuid,
        # )
        self.graph.add_edge(
            agent_at_wp,
            ft_node_uuid,
            type=Behaviors.EXPLORE,
            id=edge_uuid,
            cost=cost,
            key=edge_uuid,
        )
        self.tasks.append(Task(edge_uuid, Objectives.EXPLORE_ALL_FTS))

        # self.next_frontier_idx += 1

    # def add_guide_action_edges(self, path: Sequence[Node]):
    #     """adds edges between the nodes in the path"""
    #     # TODO: make these edge costs super explicit
    #     for i in range(len(path) - 1):
    #         self.graph.add_edge(
    #             path[i],
    #             path[i + 1],
    #             type=Behaviors.GUIDE_WP_EDGE,
    #             id=uuid4(),
    #             cost=0,
    #         )

    def remove_frontier(self, target_frontier_idx) -> None:
        """removes a frontier from the graph"""
        target_frontier = self.get_node_data_by_node(target_frontier_idx)
        if target_frontier["type"] == ObjectTypes.FRONTIER:
            self.graph.remove_node(target_frontier_idx)  # also removes the edge
        else:
            self._log.warning(f"remove_frontier(): {target_frontier_idx} is not a frontier")
            return

    # TODO: this should be invalidate, so that we change its alpha or smth
    # e.g. a method to invalidate a world object for planning, but still maintain it for vizualisation
    def remove_world_object(self, idx) -> None:
        """removes a frontier from the graph"""
        removal_target = self.get_node_data_by_node(idx)
        if removal_target["type"] == ObjectTypes.WORLD_OBJECT:
            self.graph.remove_node(idx)  # also removes the edge

    def get_node_by_pos(self, pos: tuple):
        """returns the node idx at the given position"""
        for node in self.graph.nodes():
            if self.graph.nodes[node]["pos"] == pos:
                return node

    # THIS one can soon be gone.
    def get_node_by_UUID(self, UUID):
        """returns the node idx with the given UUID"""
        for node in self.graph.nodes():
            if self.graph.nodes[node]["id"] == UUID:
                return node

    def get_edge_by_UUID(self, UUID) -> Optional[Edge]:
        """returns the edge tuple with the given UUID"""
        for src_node, target_node, edge_key, edge_id in self.graph.edges(
            data="id", keys=True
        ):
            if edge_id == UUID:
                # if edge_id == UUID or edge_key == UUID:
                return src_node, target_node, edge_key

    def get_node_data_by_node(self, node: Node) -> dict:
        """returns the node corresponding to the given index"""
        return self.graph.nodes[node]

    def get_all_waypoints(self) -> list:
        """returns all waypoints in the graph"""
        return [
            self.graph.nodes[node]
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == ObjectTypes.WAYPOINT
        ]

    def get_all_waypoint_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == ObjectTypes.WAYPOINT
        ]

    def get_all_frontiers_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == ObjectTypes.FRONTIER
        ]

    def get_all_world_object_idxs(self) -> list:
        """returns all frontier idxs in the graph"""
        return [
            node
            for node in self.graph.nodes()
            if self.graph.nodes[node]["type"] == ObjectTypes.WORLD_OBJECT
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

    def get_behavior_of_edge(self, edge: Edge) -> Optional[Behaviors]:
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

    def destroy_task_and_edge(self, task: Task) -> None:
        """removes a task and its edge from the graph"""
        edge = self.get_edge_by_UUID(task.edge_uuid)
        self.graph.remove_node(edge[1])
        try:
            self.graph.remove_edge(*edge)
        except nx.NetworkXError:
            self._log.error(f"destroy_task_and_edge(): edge {edge} not found")
        self.tasks.remove(task)
        # self._log.info(f"destroy_task_and_edge(): removed task {task_idx} and edge {edge_idx}")

    def remove_invalid_tasks(self):
        all_edge_ids = [ddict["id"] for u, v, ddict in self.graph.edges(data=True)]
        # this is like a massive list so I feel like there should be a better way
        for task in self.tasks:
            if task.edge_uuid not in all_edge_ids:
                self.tasks.remove(task)

    # FIXME: this is 2nd most expensive function
    def get_task_target_node(self, task: Task) -> Optional[Node]:
        """returns the target node of a task"""
        # BUG: sometimes task is None
        edge = self.get_task_edge(task)
        if edge:
            return edge[1]
        else:
            self._log.error(f"get_target_node(): No edge with UUID {task.edge_uuid}")
            return None

    def get_task_edge(self, task: Task) -> Optional[Edge]:
        """returns the edge of a task"""
        # BUG: some times task is None
        edge = self.get_edge_by_UUID(task.edge_uuid)
        if edge:
            return edge
        else:
            self._log.error(f"get_task_edge(): No edge with UUID {task.edge_uuid}")
            return None

    """
    what makes more sense:
    - asking the tosg which target node corresponds to a task
    - or asking the task what its target node is?
    """

    def validate_plan(self, plan: Plan) -> bool:
        if not plan:
            return False
        if len(plan) < 1:
            return False
        if not self.graph.has_node(plan[-1][1]):
            return False

        return True

    def remove_node(self, node: Node):
        self.graph.remove_node(node)


    def get_task_by_uuid(self, uuid: UUID) -> Optional[Task]:
        for task in self.tasks:
            if task.uuid == uuid:
                return task
        return None

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
        edge_uuid = None
        self.graph.add_node(node_id, pos=pos, type=object_type, id=node_id)
        for affordance in affordances:
            if affordance[0] == object_type:

                edge_uuid = self.add_my_edge(from_node, node_id, affordance[1])

                self.tasks.append(Task(edge_uuid, affordance[2]))

        print(self.tasks)

        return node_id
