from src.mission.graph_task_planner import (
    CouldNotFindPlan,
    GraphTaskPlanner,
    TargetNodeNotFound,
)
from src.mission.plan_executor import PlanExecutor
from src.mission.graph_planner_interface import GraphPlannerInterface
from src.mission.situational_graph import SituationalGraph
from src.mission.task_allocator import TaskAllocator
from src.platform.control.abstract_agent import AbstractAgent


class PlanningPipeline(GraphTaskPlanner):
    """This planner selects the optimal task and makes a plan each iteration"""

    # TODO: extract this pipeline to the mission usecase level
    # one of the arguments for this pipeline should be the task allocator.
    def pipeline(
        self,
        agent: AbstractAgent,
        tosg: SituationalGraph,
        executor: PlanExecutor,
        task_allocator: TaskAllocator,
    ) -> bool:
        if agent.init_explore_step_completed:

            filtered_tosg = self._filter_graph(tosg, agent)

            """select a task"""
            agent.task = task_allocator._single_agent_task_selection(
                agent, filtered_tosg
            )
            if not agent.task:
                return tosg.check_if_tasks_exhausted()

            """ generate a plan"""
            try:
                # this is the planner interface
                agent.plan = self._find_plan_for_task(
                    agent.at_wp, tosg, agent.task, filtered_tosg
                )
            except CouldNotFindPlan:
                self._log.error(f"Could not find a plan for task {agent.task}")
                agent.clear_task()
            except TargetNodeNotFound:
                self._log.error(f"Could not find a target node for task {agent.task}")
                agent.clear_task()

        if not self.validate_plan(agent.plan, tosg):
            return None
