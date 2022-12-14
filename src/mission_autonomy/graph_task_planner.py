import networkx as nx

from src.mission_autonomy.graph_planner_interface import GraphPlannerInterface
from src.mission_autonomy.situational_graph import SituationalGraph
from src.shared.plan_model import PlanModel
from src.shared.task import Task
from src.shared.types.node_and_edge import Node


class CouldNotFindPlan(Exception):
    pass


class CouldNotFindTask(Exception):
    pass


class TargetNodeNotFound(Exception):
    pass


class GraphTaskPlanner(GraphPlannerInterface):
    @staticmethod
    def _filter_graph(tosg: SituationalGraph, capabilities: set) -> SituationalGraph:
        def filter_edges_based_on_agent_capabilities(u: Node, v: Node, k: Node) -> bool:
            behavior_enum = tosg.G.edges[u, v, k]["type"]  # Behaviors
            for req_cap in behavior_enum.required_capabilities:
                if req_cap not in capabilities:
                    return False
            return True

        filtered_G = nx.subgraph_view(
            tosg.G, filter_edge=filter_edges_based_on_agent_capabilities
        )

        # here we insert the filtered graph into a new tosg object
        filtered_tosg = SituationalGraph()
        filtered_tosg.tasks = tosg.tasks
        filtered_tosg.G = filtered_G
        return filtered_tosg

    # this is the api
    def find_plan_for_task(
        self,
        agent_localized_to: Node,
        full_tosg: SituationalGraph,
        task: Task,
        filtered_tosg: SituationalGraph,
    ) -> PlanModel:
        target_node = task.edge[1]

        # if not self._check_target_still_valid(full_tosg, target_node):
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
