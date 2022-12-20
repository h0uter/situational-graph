import logging
from typing import Optional

import networkx as nx

from src.shared.plan import Plan
from src.shared.situational_graph import SituationalGraph
from src.shared.task import Task
from src.shared.types.node_and_edge import Edge, Node


class CouldNotFindPlan(Exception):
    pass


class CouldNotFindTask(Exception):
    pass


class TargetNodeNotFound(Exception):
    pass


class GraphTaskPlanner:
    def __init__(self):
        self._log = logging.getLogger(__name__)

    # TODO: refactor this to use just 1 graph not both
    def find_plan_for_task(
        self,
        agent_localized_to: Node,
        full_sgraph: SituationalGraph,
        task: Task,
        filtered_sgraph: SituationalGraph,
    ) -> Plan:
        # BUG: we just crashed here while bashing my leftmouse click 2022-12-14.
        if task is None:
            raise CouldNotFindPlan("Task is None")

        target_node = task.edge[1]

        if target_node is None or not full_sgraph.G.has_node(target_node):
            raise TargetNodeNotFound("Target node is not valid")

        edge_path = self.shortest_edge_path(
            filtered_sgraph, agent_localized_to, target_node
        )

        # if the agent can find a plan for that task we remove the task
        # this is necc for the initial task of exploration.
        if edge_path is None:
            full_sgraph.tasks.remove(task)
            raise CouldNotFindPlan(f"Could not find a plan for task {task}")

        return Plan(edge_path)

    @staticmethod
    def validate_plan(plan: Plan, situational_graph: SituationalGraph) -> bool:
        if not plan:
            return False
        if len(plan) < 1:
            return False
        if not situational_graph.G.has_node(plan[-1][1]):
            return False

        return True

    def shortest_edge_path(
        self, sg: SituationalGraph, source: Node, target: Node
    ) -> Optional[list[Edge]]:
        """returns the shortest path between two nodes"""

        def dist_heur_wrapper(a: Node, b: Node):
            return sg.calc_edge_len_between_nodes(a, b)

        try:
            path_of_nodes = nx.astar_path(
                sg.G,
                source=source,
                target=target,
                weight="cost",
                heuristic=dist_heur_wrapper,
            )
        except nx.NetworkXNoPath:
            self._log.debug(f"shortest_path: No path found from {source} to {target}.")
            return None

        if len(path_of_nodes) > 1:
            return sg.node_list_to_edge_list(path_of_nodes)
        else:
            self._log.error(f"shortest_path: No path found from {source} to {target}.")
            return None
