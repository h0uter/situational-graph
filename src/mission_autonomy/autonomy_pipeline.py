from src.mission_autonomy.graph_planner_interface import GraphPlannerInterface
from src.mission_autonomy.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.mission_autonomy.situational_graph import SituationalGraph
from src.mission_autonomy.task_allocator import TaskAllocator
from src.platform_autonomy.control.abstract_agent import AbstractAgent


# TODO: extract this pipeline to the mission usecase level
class AutonomyPipeline:
    def mission_pipeline(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        task_allocator: TaskAllocator,
        planner: GraphPlannerInterface,
    ):
        if agent.init_explore_step_completed:

            # TODO: conceptually figure out who should do the filtering of the graph
            filtered_tosg = planner._filter_graph(tosg, agent)

            """select a task"""
            agent.task = task_allocator._single_agent_task_selection(
                agent, filtered_tosg
            )
            if not agent.task:
                return tosg.check_if_tasks_exhausted()

            return filtered_tosg