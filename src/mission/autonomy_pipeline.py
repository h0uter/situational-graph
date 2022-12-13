from src.mission.graph_planner_interface import GraphPlannerInterface
from src.mission.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.mission.plan_executor import PlanExecutor
from src.mission.situational_graph import SituationalGraph
from src.mission.task_allocator import TaskAllocator
from src.platform.control.abstract_agent import AbstractAgent


class AutonomyPipeline:
    # TODO: extract this pipeline to the mission usecase level
    def pipeline(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        task_allocator: TaskAllocator,
        planner: GraphPlannerInterface,
    ) -> bool:
        if agent.init_explore_step_completed:

            filtered_tosg = planner._filter_graph(tosg, agent)

            """select a task"""
            agent.task = task_allocator._single_agent_task_selection(
                agent, filtered_tosg
            )
            if not agent.task:
                return tosg.check_if_tasks_exhausted()

            """ generate a plan"""
            try:
                # this is the planner interface
                agent.plan = planner._find_plan_for_task(
                    agent.at_wp, tosg, agent.task, filtered_tosg
                )
            except CouldNotFindPlan:
                planner._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                planner._log.error(
                    f"Could not find a target node for task {agent.task}"
                )
                agent.clear_task()

        if not planner.validate_plan(agent.plan, tosg):
            return None
