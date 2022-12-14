from typing import Optional

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

    @staticmethod
    def single_agent_task_selection(
        agent_at_wp: Node, tosg: SituationalGraph
    ) -> Optional[Task]:
        target_node_to_task = {task.edge[1]: task for task in tosg.tasks}

        path_costs, paths = tosg.distance_and_path_dijkstra(
            agent_at_wp, target_node_to_task.keys()
        )

        def calc_utility(reward: float, path_cost: float) -> float:
            if path_cost == 0:
                return float("inf")
            else:
                return reward / path_cost

        task_to_utility = {
            task: calc_utility(task.reward, path_costs[task.edge[1]])
            for task in tosg.tasks
            if task.edge[1] in path_costs
        }

        event_system.post_event(Topics.LOG__TASK_UTILITIES, task_to_utility)

        if len(task_to_utility) == 0:
            return None

        return max(task_to_utility, key=task_to_utility.get)
