from typing import Optional

import networkx as nx

from src.core import event_system as event_system
from src.core.topics import Topics
from src.shared.situational_graph import SituationalGraph
from src.shared.task import Task
from src.shared.types.node_and_edge import Node


class TaskAllocator:
    """
    Naive task allocator that selects the task with the highest utility.
    Multiple agents can be assigned to the same task.
    """

    def single_agent_task_selection(
        self, agent_at_wp: Node, sg: SituationalGraph
    ) -> Optional[Task]:
        target_node_to_task = {task.edge[1]: task for task in sg.tasks}

        path_costs = self.distance_and_path_dijkstra(sg,
            agent_at_wp, set(target_node_to_task.keys())
        )

        def calc_utility(reward: float, path_cost: float) -> float:
            if path_cost == 0:
                return float("inf")
            else:
                return reward / path_cost

        task_to_utility = {
            task: calc_utility(task.reward, path_costs[task.edge[1]])
            for task in sg.tasks
            if task.edge[1] in path_costs
        }

        event_system.post_event(Topics.LOG__TASK_UTILITIES, task_to_utility)

        if len(task_to_utility) == 0:
            return None

        return max(task_to_utility, key=lambda task: task_to_utility[task])

    # TODO: move to task allocator
    def distance_and_path_dijkstra(
        self, sg: SituationalGraph, source: Node, targets: set[Node]
    ) -> dict[Node, float]:
        """returns the length of the shortest path between a single source and multiple targets"""


        try:
            distance, _ = nx.single_source_dijkstra(
                sg.G,
                source=source,
                weight="cost",
            )
        except nx.NetworkXNoPath:
            sg._log.debug(
                f"shortest_path_len: No path found from {source} to {targets}."
            )
            distance = {target: float("inf") for target in targets}

        return distance
