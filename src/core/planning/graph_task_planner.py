import logging

from src.shared.situational_graph import SituationalGraph
from src.shared.plan_model import PlanModel
from src.shared.task import Task
from src.shared.types.node_and_edge import Node


class CouldNotFindPlan(Exception):
    pass


class CouldNotFindTask(Exception):
    pass


class TargetNodeNotFound(Exception):
    pass


class GraphTaskPlanner():
    def __init__(self):
        self._log = logging.getLogger(__name__)

    #TODO: refactor this to use just 1 graph not both
    def find_plan_for_task(
        self,
        agent_localized_to: Node,
        full_tosg: SituationalGraph,
        task: Task,
        filtered_tosg: SituationalGraph,
    ) -> PlanModel:
        target_node = task.edge[1]

        if target_node is None or not full_tosg.G.has_node(target_node):
            raise TargetNodeNotFound("Target node is not valid")

        edge_path = filtered_tosg.shortest_path(agent_localized_to, target_node)

        # if the agent can find a plan for that task we remove the task
        # this is necc for the initial task of exploration.
        if edge_path is None:
            full_tosg.tasks.remove(task)
            raise CouldNotFindPlan(f"Could not find a plan for task {task}")

        return PlanModel(edge_path)

    @staticmethod
    def validate_plan(plan: PlanModel, tosg: SituationalGraph) -> bool:
        if not plan:
            return False
        if len(plan) < 1:
            return False
        if not tosg.G.has_node(plan[-1][1]):
            return False

        return True
